"""
summarizer.py: Gemini Flashで記事をカテゴリ別・2段階で日本語要約する
"""

import os
import json
import re
from google import genai


def summarize_articles(articles: list[dict], config: dict) -> list[dict]:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("GEMINI_API_KEY が設定されていません")

    client = genai.Client(api_key=api_key)

    # 記事リストをテキストに整形（URLは除外）
    articles_text = ""
    for i, article in enumerate(articles, 1):
        articles_text += f"""
記事{i}【{article.get('category', '')}】: {article['title']}
概要: {article['summary']}
---
"""

    prompt = f"""以下はテック・ビジネス・音楽DTM分野の最新記事です。
各記事について日本語で以下のJSON配列を返してください。

出力形式（JSONのみ、説明文不要）:
[
  {{
    "category": "カテゴリ名（テック／ビジネス／音楽・DTM）",
    "title": "記事タイトルの日本語訳",
    "short": "1〜2文の短い要約",
    "detail": "何がリリースされたか・どんな特徴か・価格や入手方法なども含めた3〜5文の詳しい説明"
  }}
]

{articles_text}
"""

    response = client.models.generate_content(
        model=config["gemini"]["model"],
        contents=prompt,
    )

    # JSONブロックを抽出してパース
    text = response.text.strip()
    match = re.search(r'\[.*\]', text, re.DOTALL)
    if match:
        return json.loads(match.group())

    return []
