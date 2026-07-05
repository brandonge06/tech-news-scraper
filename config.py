import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")
STOCK_TICKERS = os.getenv("STOCK_TICKERS", "AAPL,MSFT,NVDA,GOOGL,META,TSLA").split(",")

RSS_FEEDS = {
    "general": [
        ("Hacker News", "https://news.ycombinator.com/rss"),
        ("TechCrunch", "https://techcrunch.com/feed/"),
        ("The Verge", "https://www.theverge.com/rss/index.xml"),
        ("Ars Technica", "https://feeds.arstechnica.com/arstechnica/index"),
        ("Wired", "https://www.wired.com/feed/rss"),
    ],
    "ai": [
        ("MIT Tech Review AI", "https://www.technologyreview.com/topic/artificial-intelligence/feed"),
        ("The Batch", "https://read.deeplearning.ai/the-batch/rss/"),
        ("Google DeepMind", "https://deepmind.google/blog/rss.xml"),
        ("Hugging Face", "https://huggingface.co/blog/feed.xml"),
        ("Import AI", "https://jack-clark.net/feed/"),
    ],
}

INTERNSHIP_REPO = "SimplifyJobs/Summer2026-Internships"
