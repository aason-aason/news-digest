"""
news-digest: TechCrunch RSS → Claude要約 → GitHub Pages → Discord通知
"""

import yaml
import sys
from pathlib import Path


def load_config(path: str = "config.yaml") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main():
    config = load_config()

    # 1. RSSフェッチ
    print("[1/4] RSSから記事を取得中...")
    from fetcher import fetch_articles
    articles = fetch_articles(config)
    print(f"  → {len(articles)} 件取得")

    # 2. Claude APIで要約
    print("[2/4] Claude APIで要約中...")
    from summarizer import summarize_articles
    summary_html = summarize_articles(articles, config)
    print("  → 要約完了")

    # 3. index.html生成
    print("[3/4] index.htmlを生成中...")
    from renderer import render_html
    output_path = render_html(summary_html, config)
    print(f"  → {output_path} に保存")

    # 4. Discord通知
    print("[4/4] Discordに通知中...")
    from notifier import notify_discord
    notify_discord(config)
    print("  → 通知送信完了")

    print("\n完了しました。")


if __name__ == "__main__":
    # news-digestディレクトリをカレントにして実行されることを想定
    script_dir = Path(__file__).parent
    import os
    os.chdir(script_dir)
    main()
