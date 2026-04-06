"""
renderer.py: 要約データをリッチなカード形式のindex.htmlに変換してdocs/に保存する
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
    categories = sorted(set(a.get("category", "") for a in articles if a.get("category")))
    filter_buttons = "\n".join(
        f'<button class="filter-btn" data-category="{c}" style="--cat-color:{CATEGORY_COLOR.get(c,"#666")}">{c}</button>'
        for c in categories
    )

    html = f"""<!DOCTYPE html>
<html lang="ja" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>News Digest - {today}</title>
  <style>
    :root {{
      --bg: #f0f2f5;
      --surface: #ffffff;
      --text: #111111;
      --subtext: #555555;
      --border: #e8e8e8;
      --header-bg: rgba(255,255,255,0.85);
      --shadow: 0 2px 12px rgba(0,0,0,0.08);
      --shadow-hover: 0 8px 24px rgba(0,0,0,0.14);
    }}
    [data-theme="dark"] {{
      --bg: #18191a;
      --surface: #242526;
      --text: #e4e6eb;
      --subtext: #b0b3b8;
      --border: #3a3b3c;
      --header-bg: rgba(36,37,38,0.92);
      --shadow: 0 2px 12px rgba(0,0,0,0.4);
      --shadow-hover: 0 8px 24px rgba(0,0,0,0.6);
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Hiragino Sans", sans-serif;
      background: var(--bg);
      color: var(--text);
      transition: background 0.3s, color 0.3s;
    }}
    header {{
      background: var(--header-bg);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      border-bottom: 1px solid var(--border);
      padding: 14px 20px;
      position: sticky;
      top: 0;
      z-index: 100;
    }}
    .header-top {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 12px;
    }}
    header h1 {{ font-size: 1.15rem; font-weight: 800; color: var(--text); }}
    header .date {{ font-size: 0.75rem; color: var(--subtext); margin-top: 2px; }}
    .dark-toggle {{
      background: none;
      border: 1px solid var(--border);
      border-radius: 20px;
      padding: 5px 12px;
      font-size: 0.8rem;
      cursor: pointer;
      color: var(--text);
      transition: all 0.2s;
    }}
    .dark-toggle:hover {{ background: var(--border); }}
    .controls {{
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      align-items: center;
    }}
    .search-box {{
      flex: 1;
      min-width: 160px;
      padding: 7px 14px;
      border: 1px solid var(--border);
      border-radius: 20px;
      background: var(--surface);
      color: var(--text);
      font-size: 0.85rem;
      outline: none;
      transition: border-color 0.2s, box-shadow 0.2s;
    }}
    .search-box:focus {{
      border-color: #1a73e8;
      box-shadow: 0 0 0 3px rgba(26,115,232,0.15);
    }}
    .filter-btn {{
      padding: 5px 14px;
      border: 2px solid var(--cat-color);
      border-radius: 20px;
      background: none;
      color: var(--cat-color);
      font-size: 0.8rem;
      font-weight: 700;
      cursor: pointer;
      transition: all 0.2s;
      white-space: nowrap;
    }}
    .filter-btn:hover, .filter-btn.active {{
      background: var(--cat-color);
      color: #fff;
    }}
    .filter-btn.all-btn {{
      border-color: var(--subtext);
      color: var(--subtext);
      --cat-color: var(--subtext);
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 16px;
      max-width: 1100px;
      margin: 24px auto;
      padding: 0 16px 40px;
    }}
    .card {{
      background: var(--surface);
      border-radius: 14px;
      padding: 18px 20px;
      box-shadow: var(--shadow);
      display: flex;
      flex-direction: column;
      gap: 10px;
      transition: transform 0.2s, box-shadow 0.2s, opacity 0.3s;
      animation: fadeUp 0.4s ease both;
      cursor: default;
    }}
    .card:hover {{
      transform: translateY(-4px);
      box-shadow: var(--shadow-hover);
    }}
    .card.hidden {{ display: none; }}
    @keyframes fadeUp {{
      from {{ opacity: 0; transform: translateY(16px); }}
      to   {{ opacity: 1; transform: translateY(0); }}
    }}
    .badge {{
      display: inline-block;
      font-size: 0.7rem;
      font-weight: 800;
      padding: 2px 10px;
      border-radius: 20px;
      color: #fff;
      width: fit-content;
      letter-spacing: 0.03em;
    }}
    .card h2 {{
      font-size: 0.95rem;
      font-weight: 700;
      color: var(--text);
      line-height: 1.5;
    }}
    .short {{
      font-size: 0.87rem;
      color: var(--subtext);
      line-height: 1.75;
    }}
    details {{
      border-top: 1px solid var(--border);
      padding-top: 10px;
    }}
    summary {{
      font-size: 0.82rem;
      color: #1a73e8;
      cursor: pointer;
      list-style: none;
      user-select: none;
      transition: color 0.2s;
    }}
    summary:hover {{ color: #1558b0; }}
    summary::-webkit-details-marker {{ display: none; }}
    summary::before {{ content: "▶ もっと詳しく"; }}
    details[open] summary::before {{ content: "▲ 閉じる"; }}
    .detail {{
      font-size: 0.87rem;
      color: var(--subtext);
      line-height: 1.8;
      margin-top: 10px;
      animation: fadeIn 0.25s ease;
    }}
    @keyframes fadeIn {{
      from {{ opacity: 0; transform: translateY(4px); }}
      to   {{ opacity: 1; transform: translateY(0); }}
    }}
    .no-results {{
      grid-column: 1/-1;
      text-align: center;
      color: var(--subtext);
      padding: 60px 0;
      font-size: 0.95rem;
    }}
    @media (max-width: 600px) {{
      .grid {{ grid-template-columns: 1fr; padding: 0 12px 32px; }}
      .card {{ padding: 16px; }}
    }}
  </style>
</head>
<body>
  <header>
    <div class="header-top">
      <div>
        <h1>News Digest</h1>
        <p class="date">{today} 更新</p>
      </div>
      <button class="dark-toggle" id="darkToggle">🌙 ダーク</button>
    </div>
    <div class="controls">
      <input class="search-box" type="search" id="searchBox" placeholder="🔍 キーワードで絞り込む...">
      <button class="filter-btn all-btn active" data-category="all">すべて</button>
      {filter_buttons}
    </div>
  </header>
  <div class="grid" id="grid">
    {cards_html}
    <div class="no-results" id="noResults" style="display:none">該当する記事が見つかりませんでした</div>
  </div>
  <script>
    // ダークモード
    const toggle = document.getElementById('darkToggle');
    const html = document.documentElement;
    const saved = localStorage.getItem('theme');
    if (saved) {{ html.dataset.theme = saved; toggle.textContent = saved === 'dark' ? '☀️ ライト' : '🌙 ダーク'; }}
    toggle.addEventListener('click', () => {{
      const isDark = html.dataset.theme === 'dark';
      html.dataset.theme = isDark ? 'light' : 'dark';
      toggle.textContent = isDark ? '🌙 ダーク' : '☀️ ライト';
      localStorage.setItem('theme', html.dataset.theme);
    }});

    // フィルター & 検索
    let activeCategory = 'all';
    let searchQuery = '';

    function updateCards() {{
      const cards = document.querySelectorAll('.card[data-category]');
      let visible = 0;
      cards.forEach(card => {{
        const catMatch = activeCategory === 'all' || card.dataset.category === activeCategory;
        const textMatch = !searchQuery || card.textContent.toLowerCase().includes(searchQuery);
        card.classList.toggle('hidden', !(catMatch && textMatch));
        if (catMatch && textMatch) visible++;
      }});
      document.getElementById('noResults').style.display = visible === 0 ? 'block' : 'none';
    }}

    document.querySelectorAll('.filter-btn').forEach(btn => {{
      btn.addEventListener('click', () => {{
        document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        activeCategory = btn.dataset.category;
        updateCards();
      }});
    }});

    document.getElementById('searchBox').addEventListener('input', e => {{
      searchQuery = e.target.value.toLowerCase();
      updateCards();
    }});
  </script>
</body>
</html>
"""

    output_path = os.path.join(docs_dir, filename)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    return output_path


def _build_cards(articles: list[dict]) -> str:
    cards = []
    for i, article in enumerate(articles):
        category = article.get("category", "")
        title = article.get("title", "")
        short = article.get("short", "")
        detail = article.get("detail", "")
        color = CATEGORY_COLOR.get(category, "#666")
        delay = f"{i * 0.05:.2f}s"

        card = f"""<div class="card" data-category="{category}" style="animation-delay:{delay}">
      <span class="badge" style="background:{color}">{category}</span>
      <h2>{title}</h2>
      <p class="short">{short}</p>
      <details>
        <summary></summary>
        <p class="detail">{detail}</p>
      </details>
    </div>"""
        cards.append(card)

    return "\n    ".join(cards)
