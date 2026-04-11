"""
fetcher.py: 複数RSSソースから記事を取得する

各ソースは categories（リスト）を持つ。
複数カテゴリに属するソースは1回だけフェッチし、
カテゴリごとに記事エントリを複製して返す。
"""

import feedparser


def fetch_articles(config: dict) -> list[dict]:
    """RSSソース一覧から記事を取得し、カテゴリ付きリストで返す。"""
    sources = config["rss"]["sources"]
    max_per_feed = config["rss"]["max_articles_per_feed"]

    articles = []

    for source in sources:
        # categories（リスト）または category（文字列）に対応
        categories = source.get("categories") or [source.get("category", "")]

        try:
            feed = feedparser.parse(source["url"])
            entries = feed.entries[:max_per_feed]

            for category in categories:
                for entry in entries:
                    articles.append({
                        "title":    entry.get("title", ""),
                        "link":     entry.get("link", ""),
                        "summary":  entry.get("summary", ""),
                        "published": entry.get("published", ""),
                        "source":   source["name"],
                        "category": category,
                    })

        except Exception as e:
            print(f"  [警告] {source['name']} の取得に失敗: {e}")

    return articles
