import feedparser
from datetime import datetime, timezone
from config import RSS_FEEDS


def fetch_feed(name: str, url: str, limit: int = 5) -> list[dict]:
    feed = feedparser.parse(url)
    articles = []
    for entry in feed.entries[:limit]:
        articles.append({
            "source": name,
            "title": entry.get("title", ""),
            "url": entry.get("link", ""),
            "summary": entry.get("summary", ""),
        })
    return articles


def fetch_all(category: str, limit_per_feed: int = 5) -> list[dict]:
    articles = []
    for name, url in RSS_FEEDS[category]:
        try:
            articles.extend(fetch_feed(name, url, limit_per_feed))
        except Exception as e:
            print(f"[rss] failed to fetch {name}: {e}")
    return articles
