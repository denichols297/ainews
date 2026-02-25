from flask import Flask, render_template, jsonify
from scrapers import get_all_news
import threading
import time
import os
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

app = Flask(__name__, template_folder=resource_path('templates'))

# Cache for news data to avoid scraping on every request
news_cache = {
    "data": None,
    "last_updated": 0
}
cache_lock = threading.Lock()
CACHE_DURATION = 3600 # 1 hour

def update_cache():
    global news_cache
    print("Updating news cache...")
    try:
        data = get_all_news()
        with cache_lock:
            news_cache["data"] = data
            news_cache["last_updated"] = time.time()
        print("Cache updated successfully.")
    except Exception as e:
        print(f"Failed to update cache: {e}")

@app.route('/')
def index():
    global news_cache
    
    # Update cache if it's empty or expired
    should_update = False
    with cache_lock:
        if news_cache["data"] is None or (time.time() - news_cache["last_updated"] > CACHE_DURATION):
            should_update = True
    
    if should_update:
        update_cache()
    
    return render_template('index.html', news=news_cache["data"])

@app.route('/api/news')
def api_news():
    with cache_lock:
        return jsonify(news_cache["data"])

def start_server():
    # Helper to start from desktop script
    update_cache()
    app.run(port=5000, debug=False, use_reloader=False)

if __name__ == '__main__':
    # Initial cache population
    update_cache()
    app.run(debug=True, port=5000)
