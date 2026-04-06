"""
renderer.py: 要約テキストをindex.htmlに変換してdocs/に保存する
"""

import os
import re
from datetime import datetime


def linkify(text: str) -> str:
    """テキスト中のURLをクリッカブルなリンクに変換する"""
    url_pattern = re.compile(r'(https?://[^\s\）\)<>]+)')
    return url_pattern.sub(r'<a href="\1" target="_blank" rel="noopener">\1</a>', text)


def _build_cards(summary_text: str) -> str:
    """要約テキストをトピックごとのカードHTMLに変換する"""
    cards = []
    current_title = ""
    current_lines = []

    for line in summary_text.splitlines():
        stripped = line.strip()
        # ## または ** で始まる行をトピックタイトルと見なす
        if stripped.startswith("## ") or (stripped.startswith("**") and stripped.endswith("**")):
            if current_lines:
                body = linkify("<br>".join(current_lines))
                title = current_title or "トピック"
                cards.append(f'<div class="card"><h2>{title}</h2><p>{body}</p></div>')
                current_lines = []
            current_title = stripped.lstrip("#").strip().strip("*").strip()
        elif stripped:
            current_lines.append(linkify(stripped))

    # 最後のブロック
    if current_lines:
        body = "<br>".join(current_lines)
        title = current_title or "まとめ"
        cards.append(f'<div class="card"><h2>{title}</h2><p>{body}</p></div>')

    # トピック分割できなかった場合は1枚のカードにまとめる
    if not cards:
        body = linkify("<br>".join(summary_text.splitlines()))
        cards.append(f'<div class="card"><h2>まとめ</h2><p>{body}</p></div>')

    return "\n    ".join(cards)


def render_html(summary_text: str, config: dict) -> str:
    docs_dir = config["output"]["docs_dir"]
    filename = config["output"]["filename"]

    os.makedirs(docs_dir, exist_ok=True)

    today = datetime.now().strftime("%Y年%m月%d日")

    # 要約テキストをトピックブロックごとにカード化する
    cards_html = _build_cards(summary_text)

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
    header h1 {{
      font-size: 1.2rem;
      font-weight: 700;
      color: #111;
    }}
    header .date {{
      font-size: 0.78rem;
      color: #999;
      margin-top: 2px;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
      gap: 16px;
      max-width: 1100px;
      margin: 24px auto;
      padding: 0 16px 40px;
    }}
    .card {{
      background: #fff;
      border-radius: 12px;
      padding: 20px;
      box-shadow: 0 1px 4px rgba(0,0,0,0.08);
      line-height: 1.75;
      font-size: 0.93rem;
    }}
    .card h2 {{
      font-size: 1rem;
      font-weight: 700;
      margin-bottom: 10px;
      padding-bottom: 8px;
      border-bottom: 2px solid #e8e8e8;
      color: #111;
    }}
    .card p {{ color: #444; }}
    a {{
      color: #1a73e8;
      text-decoration: none;
      word-break: break-all;
      -webkit-tap-highlight-color: transparent;
    }}
    a:hover {{ text-decoration: underline; }}
    @media (max-width: 600px) {{
      .grid {{ grid-template-columns: 1fr; padding: 0 12px 32px; }}
      .card {{ padding: 16px; }}
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
