"""
fetcher.py: 複数RSSソースから記事を取得する

各ソースは categories（リスト）を持つ。
複数カテゴリに属するソースは1回だけフェッチし、
カテゴリごとに記事エントリを複製して返す。
"""

import socket
import feedparser

DEFAULT_TIMEOUT = 30  # 通常ソースのタイムアウト（秒）


def _parse_with_timeout(url: str, timeout: int) -> feedparser.FeedParserDict:
    """タイムアウト付きでRSSをパースする。"""
    prev = socket.getdefaulttimeout()
    try:
        socket.setdefaulttimeout(timeout)
        return feedparser.parse(url)
    finally:
        socket.setdefaulttimeout(prev)


def fetch_articles(config: dict) -> list[dict]:
    """RSSソース一覧から記事を取得し、カテゴリ付きリストで返す。"""
    sources = config["rss"]["sources"]
    max_per_feed = config["rss"]["max_articles_per_feed"]

    articles = []

    for source in sources:
        # categories（リスト）または category（文字列）に対応
        categories = source.get("categories") or [source.get("category", "")]
        timeout = source.get("timeout", DEFAULT_TIMEOUT)

        try:
            feed = _parse_with_timeout(source["url"], timeout)
            entries = feed.entries[:max_per_feed]

            if not entries:
                print(f"  [情報] {source['name']}: 記事0件（空フィードまたは取得失敗）")
                continue

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
            print(f"  [警告] {source['name']} の取得をスキップ: {e}")

    return articles
