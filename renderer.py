"""
renderer.py: 要約テキストをindex.htmlに変換してdocs/に保存する
"""

import os
from datetime import datetime


def render_html(summary_text: str, config: dict) -> str:
    docs_dir = config["output"]["docs_dir"]
    filename = config["output"]["filename"]

    os.makedirs(docs_dir, exist_ok=True)

    today = datetime.now().strftime("%Y年%m月%d日")

    # 改行をHTMLの<br>に変換
    body = summary_text.replace("\n", "<br>\n")

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Tech News ダイジェスト - {today}</title>
  <style>
    body {{ font-family: sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; line-height: 1.8; }}
    h1 {{ font-size: 1.4rem; border-bottom: 2px solid #333; padding-bottom: 8px; }}
    .date {{ color: #888; font-size: 0.9rem; margin-bottom: 24px; }}
    .content {{ white-space: pre-wrap; }}
  </style>
</head>
<body>
  <h1>Tech News ダイジェスト</h1>
  <p class="date">{today} 更新</p>
  <div class="content">{body}</div>
</body>
</html>
"""

    output_path = os.path.join(docs_dir, filename)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    return output_path
