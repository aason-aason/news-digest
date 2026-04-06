"""
renderer.py: 要約テキストをindex.htmlに変換してdocs/に保存する
"""

import os
import re
from datetime import datetime


def linkify(text: str) -> str:
    """テキスト中のURLをクリッカブルなリンクに変換する"""
    url_pattern = re.compile(r'(https?://[^\s\）\)]+)')
    return url_pattern.sub(r'<a href="\1" target="_blank" rel="noopener">\1</a>', text)


def render_html(summary_text: str, config: dict) -> str:
    docs_dir = config["output"]["docs_dir"]
    filename = config["output"]["filename"]

    os.makedirs(docs_dir, exist_ok=True)

    today = datetime.now().strftime("%Y年%m月%d日")

    # URLをリンクに変換してから改行を<br>に変換
    body = linkify(summary_text).replace("\n", "<br>\n")

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>News Digest - {today}</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: #f5f5f5;
      color: #222;
      line-height: 1.8;
    }}
    header {{
      background: #111;
      color: #fff;
      padding: 24px 32px;
    }}
    header h1 {{ font-size: 1.4rem; font-weight: 700; }}
    header .date {{ font-size: 0.85rem; color: #aaa; margin-top: 4px; }}
    main {{
      max-width: 860px;
      margin: 32px auto;
      padding: 0 20px;
    }}
    .card {{
      background: #fff;
      border-radius: 10px;
      padding: 28px 32px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.07);
    }}
    .content {{ white-space: pre-wrap; font-size: 0.97rem; }}
    a {{ color: #0066cc; text-decoration: none; word-break: break-all; }}
    a:hover {{ text-decoration: underline; }}
  </style>
</head>
<body>
  <header>
    <h1>News Digest</h1>
    <p class="date">{today} 更新</p>
  </header>
  <main>
    <div class="card">
      <div class="content">{body}</div>
    </div>
  </main>
</body>
</html>
"""

    output_path = os.path.join(docs_dir, filename)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    return output_path
