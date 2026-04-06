"""
summarizer.py: Gemini Flashで記事をトピック別に日本語要約する
"""

import os
from google import genai


def summarize_articles(articles: list[dict], config: dict) -> str:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("GEMINI_API_KEY が設定されていません")

    client = genai.Client(api_key=api_key)

    # 記事リストをテキストに整形
    articles_text = ""
    for i, article in enumerate(articles, 1):
        articles_text += f"""
記事{i}: {article['title']}
URL: {article['link']}
概要: {article['summary']}
---
"""

    prompt = f"""以下はTechCrunchの最新記事です。
トピック別にまとめて、日本語でわかりやすく要約してください。
各トピックには記事のURLも含めてください。

{articles_text}
"""

    response = client.models.generate_content(
        model=config["gemini"]["model"],
        contents=prompt,
    )

    return response.text
