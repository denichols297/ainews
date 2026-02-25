# AI News Dashboard

A modern, standalone desktop application that aggregates the latest top 5 news stories from DeepLearning.AI, eSchool News, and Import AI.

## Features

- **Automated Scraping**: Periodically fetches the latest news from three major AI sources.
- **AI-Powered Summaries**: Extracts 1-2 sentence summaries for each story.
- **Standalone Desktop App**: Native macOS `.app` bundle with a custom icon.
- **Modern Dashboard**: Responsive 3-column layout with a dark-mode aesthetic.

## Installation

### Prerequisites
- Python 3.9+

### Setup
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd ainews
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the App

### Standalone (macOS)
If you are on macOS and have built the executable:
- Open `dist/AINews.app`

### Development Mode
Run the desktop wrapper:
```bash
python3 desktop.py
```
Or run as a web server:
```bash
python3 app.py
```

## Build Instructions
To build the standalone `.app` bundle:
```bash
python3 build.py
```
