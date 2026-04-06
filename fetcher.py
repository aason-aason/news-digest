"""
fetcher.py: 複数RSSソースから記事を取得する
"""

import feedparser


def fetch_articles(config: dict) -> list[dict]:
    sources = config["rss"]["sources"]
    max_per_feed = config["rss"]["max_articles_per_feed"]

    articles = []

    for source in sources:
        try:
            feed = feedparser.parse(source["url"])
            for entry in feed.entries[:max_per_feed]:
                articles.append({
                    "title": entry.get("title", ""),
                    "link": entry.get("link", ""),
                    "summary": entry.get("summary", ""),
                    "published": entry.get("published", ""),
                    "source": source["name"],
                    "category": source["category"],
                })
        except Exception as e:
            print(f"  [警告] {source['name']} の取得に失敗: {e}")

    return articles
