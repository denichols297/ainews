import requests
from bs4 import BeautifulSoup
import re

class NewsScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def get_soup(self, url):
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

class DeepLearningAIScraper(NewsScraper):
    def scrape(self):
        base_url = "https://www.deeplearning.ai/the-batch/"
        soup = self.get_soup(base_url)
        if not soup:
            return []

        # Find the link to the latest issue
        latest_issue_link = soup.select_one('a[href*="/the-batch/issue-"]')
        if not latest_issue_link:
            # Fallback to the first "Read more" link
            latest_issue_link = soup.find('a', text=re.compile(r'Read more', re.I))
        
        if not latest_issue_link:
            return []

        latest_url = latest_issue_link['href']
        if not latest_url.startswith('http'):
            latest_url = f"https://www.deeplearning.ai{latest_url}"

        issue_soup = self.get_soup(latest_url)
        if not issue_soup:
            return []

        stories = []
        # Based on research: stories are in h1 tags within the content area
        # We look for the main content container first
        content_div = issue_soup.select_one('div[class*="post_postContent"]')
        if not content_div:
            content_div = issue_soup.select_one('article') or issue_soup.body

        # Find all H1s that are news stories (skipping the main issue title)
        headlines = content_div.find_all('h1')
        for h1 in headlines:
            title = h1.get_text(strip=True)
            # Skip common header titles
            if any(skip in title.lower() for skip in ["issue", "news", "what matters"]):
                continue
            
            # Summary is usually in the next paragraph
            p = h1.find_next_sibling('p')
            summary = p.get_text(strip=True) if p else ""
            
            stories.append({
                "title": title,
                "summary": summary,
                "url": latest_url
            })
            if len(stories) == 5:
                break
        
        return stories

class SubstackScraper(NewsScraper):
    def __init__(self, base_url):
        super().__init__()
        self.base_url = base_url

    def scrape(self):
        archive_url = f"{self.base_url}/archive"
        soup = self.get_soup(archive_url)
        if not soup:
            return []

        # Find the latest post link - using a more robust search
        # Substack often uses <a> tags with data-testid="post-preview-title" or class containing "post-preview-title"
        latest_post = soup.select_one('a[data-testid="post-preview-title"]') \
                      or soup.select_one('.post-preview-title') \
                      or soup.select_one('div.post-preview a') \
                      or soup.find('a', href=re.compile(r'/p/'))

        if not latest_post:
            return []

        post_url = latest_post['href']
        if not post_url.startswith('http'):
            post_url = f"{self.base_url.rstrip('/')}/{post_url.lstrip('/')}"
            
        post_soup = self.get_soup(post_url)
        if not post_soup:
            return []

        stories = []
        
        # Substack content is usually inside .body.markup or .available-content
        content = post_soup.select_one('.body.markup') \
                  or post_soup.select_one('.available-content') \
                  or post_soup.select_one('.post-content') \
                  or post_soup.select_one('article')

        if not content:
            return []

        # Strategy 1: Look for headlines inside strong tags or H2/H3
        # In Import AI, stories often start with "Story Name:" in bold
        possible_headlines = content.find_all(['p', 'h2', 'h3'])
        for item in possible_headlines:
            text = item.get_text(strip=True)
            strong = item.find('strong')
            
            # Check if this looks like a headline (bold at start, or specific header tags)
            is_headline = False
            title = ""
            summary = ""
            
            if item.name in ['h2', 'h3'] and len(text) < 200:
                is_headline = True
                title = text
            elif strong and text.startswith(strong.get_text(strip=True)) and len(strong.get_text(strip=True)) > 5:
                is_headline = True
                title = strong.get_text(strip=True).strip(': ')
            
            if is_headline:
                # Get the summary from the rest of the text or next paragraph
                if item.name in ['h2', 'h3']:
                    next_p = item.find_next_sibling('p')
                    summary = next_p.get_text(strip=True) if next_p else ""
                else:
                    summary = text.replace(strong.get_text(strip=True), "").strip(': ').strip()
                    if not summary:
                        next_p = item.find_next_sibling('p')
                        summary = next_p.get_text(strip=True) if next_p else ""
                
                # Filter out metadata-like headlines
                if any(skip in title.lower() for skip in ["subscribe", "archive", "share", "about", "sponsor"]):
                    continue
                    
                if title and summary:
                    stories.append({
                        "title": title,
                        "summary": summary[:300] + ("..." if len(summary) > 300 else ""),
                        "url": post_url
                    })
                
            if len(stories) >= 5:
                break

        # Strategy 2: Check for list items (common in Ben's Bites "Daily Bits")
        if len(stories) < 2:
            list_items = content.find_all('li')
            for li in list_items:
                text = li.get_text(strip=True)
                if len(text) > 30:
                    strong = li.find('strong')
                    if strong:
                        title = strong.get_text(strip=True).strip(': ')
                        summary = text.replace(strong.get_text(strip=True), "").strip(': ').strip()
                    else:
                        parts = text.split(':', 1)
                        if len(parts) > 1:
                            title = parts[0][:100]
                            summary = parts[1]
                        else:
                            title = text[:50] + "..."
                            summary = text
                    
                    if title and summary:
                        stories.append({
                            "title": title,
                            "summary": summary[:300] + ("..." if len(summary) > 300 else ""),
                            "url": post_url
                        })
                if len(stories) >= 5:
                    break

        return stories[:5]

class RSScraper(NewsScraper):
    def __init__(self, feed_url):
        super().__init__()
        self.feed_url = feed_url

    def scrape(self):
        try:
            response = requests.get(self.feed_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'xml')
            
            stories = []
            items = soup.find_all('item')
            for item in items:
                title = item.find('title').get_text(strip=True)
                summary = item.find('description').get_text(strip=True)
                # Clean up HTML tags from summary if any
                summary = BeautifulSoup(summary, 'html.parser').get_text(strip=True)
                url = item.find('link').get_text(strip=True)
                
                stories.append({
                    "title": title,
                    "summary": summary[:300] + ("..." if len(summary) > 300 else ""),
                    "url": url
                })
                if len(stories) == 5:
                    break
            return stories
        except Exception as e:
            print(f"Error scraping RSS {self.feed_url}: {e}")
            return []

def get_all_news():
    scrapers = [
        ("DeepLearning.AI", DeepLearningAIScraper()),
        ("eSchool News", RSScraper("https://www.eschoolnews.com/feed/")),
        ("Import AI", SubstackScraper("https://importai.substack.com"))
    ]
    
    results = {}
    for name, scraper in scrapers:
        try:
            results[name] = scraper.scrape()
        except Exception as e:
            print(f"Error scraping {name}: {e}")
            results[name] = []
    
    return results

if __name__ == "__main__":
    import json
    print(json.dumps(get_all_news(), indent=2))
