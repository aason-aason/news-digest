"""
fetcher.py: TechCrunch RSSから記事を取得する
"""

import feedparser


def fetch_articles(config: dict) -> list[dict]:
    url = config["rss"]["url"]
    max_articles = config["rss"]["max_articles"]

    feed = feedparser.parse(url)
    articles = []

    for entry in feed.entries[:max_articles]:
        articles.append({
            "title": entry.get("title", ""),
            "link": entry.get("link", ""),
            "summary": entry.get("summary", ""),
            "published": entry.get("published", ""),
        })

    return articles
