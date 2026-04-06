"""
renderer.py: 要約データをカード形式のindex.htmlに変換してdocs/に保存する
"""

import os
from datetime import datetime


CATEGORY_COLOR = {
    "テック": "#1a73e8",
    "ビジネス": "#e67e22",
    "音楽・DTM": "#8e44ad",
}


def render_html(articles: list[dict], config: dict) -> str:
    docs_dir = config["output"]["docs_dir"]
    filename = config["output"]["filename"]

    os.makedirs(docs_dir, exist_ok=True)

    today = datetime.now().strftime("%Y年%m月%d日")

    cards_html = _build_cards(articles)

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>News Digest - {today}</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Hiragino Sans", sans-serif;
      background: #f0f2f5;
      color: #222;
    }}
    header {{
      background: #fff;
      border-bottom: 1px solid #e0e0e0;
      padding: 16px 20px;
      position: sticky;
      top: 0;
      z-index: 10;
    }}
    header h1 {{ font-size: 1.2rem; font-weight: 700; color: #111; }}
    header .date {{ font-size: 0.78rem; color: #999; margin-top: 2px; }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 16px;
      max-width: 1100px;
      margin: 24px auto;
      padding: 0 16px 40px;
    }}
    .card {{
      background: #fff;
      border-radius: 12px;
      padding: 18px 20px;
      box-shadow: 0 1px 4px rgba(0,0,0,0.08);
      display: flex;
      flex-direction: column;
      gap: 10px;
    }}
    .badge {{
      display: inline-block;
      font-size: 0.72rem;
      font-weight: 700;
      padding: 2px 8px;
      border-radius: 20px;
      color: #fff;
      width: fit-content;
    }}
    .card h2 {{
      font-size: 0.95rem;
      font-weight: 700;
      color: #111;
      line-height: 1.5;
    }}
    .short {{
      font-size: 0.88rem;
      color: #555;
      line-height: 1.7;
    }}
    details {{ border-top: 1px solid #f0f0f0; padding-top: 10px; }}
    summary {{
      font-size: 0.82rem;
      color: #1a73e8;
      cursor: pointer;
      list-style: none;
      user-select: none;
    }}
    summary::-webkit-details-marker {{ display: none; }}
    summary::before {{ content: "▶ "; font-size: 0.7rem; }}
    details[open] summary::before {{ content: "▼ "; }}
    .detail {{
      font-size: 0.87rem;
      color: #444;
      line-height: 1.75;
      margin-top: 10px;
    }}
    @media (max-width: 600px) {{
      .grid {{ grid-template-columns: 1fr; padding: 0 12px 32px; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>News Digest</h1>
    <p class="date">{today} 更新</p>
  </header>
  <div class="grid">
    {cards_html}
  </div>
</body>
</html>
"""

    output_path = os.path.join(docs_dir, filename)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    return output_path


def _build_cards(articles: list[dict]) -> str:
    cards = []
    for article in articles:
        category = article.get("category", "")
        title = article.get("title", "")
        short = article.get("short", "")
        detail = article.get("detail", "")
        color = CATEGORY_COLOR.get(category, "#666")

        card = f"""<div class="card">
      <span class="badge" style="background:{color}">{category}</span>
      <h2>{title}</h2>
      <p class="short">{short}</p>
      <details>
        <summary>もっと詳しく</summary>
        <p class="detail">{detail}</p>
      </details>
    </div>"""
        cards.append(card)

    return "\n    ".join(cards)
