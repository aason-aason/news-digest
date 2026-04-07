"""
renderer.py: 要約データをUI仕様に沿ったindex.htmlに変換してdocs/に保存する

UI仕様:
- スマホ優先・1カラム・余白多め・フォント大きめ
- 🔴緊急は最上部に別枠固定
- カテゴリ別セクション（🟡を先頭、🟢を後方）
- ソース名のみ表示（URLは非表示）
"""

import os
from datetime import datetime

CATEGORY_COLOR = {
    "テック":    "#1a73e8",
    "ビジネス":  "#e67e22",
    "音楽・DTM": "#8e44ad",
}

IMPORTANCE_LABEL = {
    "🔴": "緊急",
    "🟡": "重要",
    "🟢": "有益",
}


def render_html(articles: list[dict], config: dict) -> str:
    """要約データをHTMLに変換してdocs/に保存し、パスを返す。"""
    docs_dir  = config["output"]["docs_dir"]
    filename  = config["output"]["filename"]
    os.makedirs(docs_dir, exist_ok=True)

    today = datetime.now().strftime("%Y年%m月%d日")

    # 重要度で分類
    urgent   = [a for a in articles if a.get("importance", "").startswith("🔴")]
    normal   = [a for a in articles if not a.get("importance", "").startswith("🔴")]

    # カテゴリ別に束ねる（🟡を先頭に）
    categories = list(dict.fromkeys(a.get("category", "") for a in normal))
    sections_html = ""
    for cat in categories:
        items = [a for a in normal if a.get("category") == cat]
        items.sort(key=lambda x: 0 if x.get("importance", "").startswith("🟡") else 1)
        sections_html += _build_section(cat, items)

    urgent_html = _build_urgent(urgent) if urgent else ""

    html = f"""<!DOCTYPE html>
<html lang="ja" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>News Digest - {today}</title>
  <style>
    :root {{
      --bg:        #f5f6f8;
      --surface:   #ffffff;
      --text:      #111111;
      --subtext:   #4a4a4a;
      --muted:     #888888;
      --border:    #e4e4e4;
      --hdr:       rgba(255,255,255,0.92);
      --shadow:    0 1px 6px rgba(0,0,0,0.07);
      --urgent-bg: #fff4f4;
      --urgent-border: #ff4444;
    }}
    [data-theme="dark"] {{
      --bg:        #18191a;
      --surface:   #242526;
      --text:      #e4e6eb;
      --subtext:   #b0b3b8;
      --muted:     #777;
      --border:    #3a3b3c;
      --hdr:       rgba(24,25,26,0.95);
      --shadow:    0 1px 6px rgba(0,0,0,0.4);
      --urgent-bg: #2a1a1a;
      --urgent-border: #ff4444;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Hiragino Sans", "Noto Sans JP", sans-serif;
      background: var(--bg);
      color: var(--text);
      font-size: 16px;
      line-height: 1.75;
      transition: background 0.3s, color 0.3s;
    }}

    /* ヘッダー */
    header {{
      background: var(--hdr);
      backdrop-filter: blur(10px);
      -webkit-backdrop-filter: blur(10px);
      border-bottom: 1px solid var(--border);
      padding: 16px 20px;
      position: sticky;
      top: 0;
      z-index: 100;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}
    header h1 {{ font-size: 1.1rem; font-weight: 800; }}
    header .date {{ font-size: 0.78rem; color: var(--muted); margin-top: 2px; }}
    .dark-btn {{
      background: none;
      border: 1px solid var(--border);
      border-radius: 20px;
      padding: 6px 14px;
      font-size: 0.82rem;
      cursor: pointer;
      color: var(--text);
      white-space: nowrap;
      transition: background 0.2s;
    }}
    .dark-btn:hover {{ background: var(--border); }}

    /* メインコンテンツ */
    main {{
      max-width: 680px;
      margin: 0 auto;
      padding: 24px 16px 60px;
      display: flex;
      flex-direction: column;
      gap: 32px;
    }}

    /* 🔴 緊急アラート枠 */
    .urgent-section {{
      background: var(--urgent-bg);
      border: 2px solid var(--urgent-border);
      border-radius: 14px;
      padding: 20px;
      display: flex;
      flex-direction: column;
      gap: 4px;
    }}
    .urgent-section .section-label {{
      font-size: 0.8rem;
      font-weight: 800;
      color: var(--urgent-border);
      letter-spacing: 0.05em;
      margin-bottom: 12px;
    }}

    /* カテゴリセクション */
    .category-section {{ display: flex; flex-direction: column; gap: 4px; }}
    .category-label {{
      font-size: 0.75rem;
      font-weight: 800;
      letter-spacing: 0.08em;
      padding: 0 4px;
      margin-bottom: 8px;
    }}

    /* 記事カード */
    .item {{
      background: var(--surface);
      border-radius: 12px;
      padding: 20px;
      box-shadow: var(--shadow);
      display: flex;
      flex-direction: column;
      gap: 12px;
      transition: transform 0.15s, box-shadow 0.15s;
      animation: fadeUp 0.35s ease both;
    }}
    .item:hover {{
      transform: translateY(-2px);
      box-shadow: 0 4px 16px rgba(0,0,0,0.12);
    }}
    @keyframes fadeUp {{
      from {{ opacity: 0; transform: translateY(10px); }}
      to   {{ opacity: 1; transform: translateY(0); }}
    }}
    .item-header {{ display: flex; align-items: flex-start; gap: 8px; flex-wrap: wrap; }}
    .imp-badge {{
      font-size: 0.72rem;
      font-weight: 700;
      padding: 2px 8px;
      border-radius: 20px;
      white-space: nowrap;
      flex-shrink: 0;
    }}
    .imp-urgent  {{ background: #ffe0e0; color: #cc0000; }}
    .imp-important {{ background: #fff3e0; color: #b35a00; }}
    .imp-useful  {{ background: #e8f5e9; color: #2e7d32; }}
    .item h2 {{
      font-size: 1.0rem;
      font-weight: 700;
      line-height: 1.5;
      color: var(--text);
    }}
    .item .summary {{
      font-size: 0.93rem;
      color: var(--subtext);
      line-height: 1.8;
    }}
    details {{ border-top: 1px solid var(--border); padding-top: 12px; }}
    summary {{
      font-size: 0.83rem;
      color: #1a73e8;
      cursor: pointer;
      list-style: none;
      user-select: none;
    }}
    summary::-webkit-details-marker {{ display: none; }}
    summary::before {{ content: "▶ もっと詳しく"; }}
    details[open] summary::before {{ content: "▲ 閉じる"; }}
    .detail-text {{
      font-size: 0.9rem;
      color: var(--subtext);
      line-height: 1.8;
      margin-top: 12px;
      animation: fadeIn 0.2s ease;
    }}
    @keyframes fadeIn {{
      from {{ opacity: 0; }}
      to   {{ opacity: 1; }}
    }}
    .source-name {{
      font-size: 0.75rem;
      color: var(--muted);
      margin-top: 2px;
    }}
  </style>
</head>
<body>
  <header>
    <div>
      <h1>News Digest</h1>
      <p class="date">{today} 更新</p>
    </div>
    <button class="dark-btn" id="darkBtn">🌙 ダーク</button>
  </header>
  <main>
    {urgent_html}
    {sections_html}
  </main>
  <script>
    const btn = document.getElementById('darkBtn');
    const root = document.documentElement;
    const saved = localStorage.getItem('theme') || 'light';
    root.dataset.theme = saved;
    btn.textContent = saved === 'dark' ? '☀️ ライト' : '🌙 ダーク';
    btn.addEventListener('click', () => {{
      const dark = root.dataset.theme !== 'dark';
      root.dataset.theme = dark ? 'dark' : 'light';
      btn.textContent = dark ? '☀️ ライト' : '🌙 ダーク';
      localStorage.setItem('theme', root.dataset.theme);
    }});
  </script>
</body>
</html>
"""

    output_path = os.path.join(docs_dir, filename)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    return output_path


def _importance_badge(importance: str) -> str:
    """重要度バッジのHTMLを返す。"""
    if importance.startswith("🔴"):
        return f'<span class="imp-badge imp-urgent">🔴 緊急</span>'
    if importance.startswith("🟡"):
        return f'<span class="imp-badge imp-important">🟡 重要</span>'
    return f'<span class="imp-badge imp-useful">🟢 有益</span>'


def _build_item(article: dict, delay: float) -> str:
    """1記事分のカードHTMLを返す。"""
    title       = article.get("title", "")
    summary     = article.get("summary", "")
    detail      = article.get("detail", "")
    source_name = article.get("source_name", "")
    importance  = article.get("importance", "🟢")
    badge       = _importance_badge(importance)

    detail_block = ""
    if detail:
        detail_block = f"""<details>
        <summary></summary>
        <p class="detail-text">{detail}</p>
      </details>"""

    source_block = f'<p class="source-name">📰 {source_name}</p>' if source_name else ""

    return f"""<div class="item" style="animation-delay:{delay:.2f}s">
      <div class="item-header">
        {badge}
      </div>
      <h2>{title}</h2>
      <p class="summary">{summary}</p>
      {detail_block}
      {source_block}
    </div>"""


def _build_urgent(articles: list[dict]) -> str:
    """🔴緊急アラートセクションのHTMLを返す。"""
    items = "\n".join(_build_item(a, i * 0.05) for i, a in enumerate(articles))
    return f"""<section class="urgent-section">
      <p class="section-label">🔴 緊急アラート — 即確認してください</p>
      {items}
    </section>"""


def _build_section(category: str, articles: list[dict]) -> str:
    """カテゴリセクションのHTMLを返す。"""
    color = CATEGORY_COLOR.get(category, "#666")
    items = "\n".join(_build_item(a, i * 0.05) for i, a in enumerate(articles))
    return f"""<section class="category-section">
      <p class="category-label" style="color:{color}">● {category}</p>
      {items}
    </section>"""
