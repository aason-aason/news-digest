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

    # フィルターボタン
    filter_btns = '<button class="filter-btn active" data-cat="all">すべて</button>\n'
    if urgent:
        filter_btns += '<button class="filter-btn" data-cat="urgent" style="--c:#ff4444">🔴 緊急</button>\n'
    for cat in categories:
        color = CATEGORY_COLOR.get(cat, "#666")
        filter_btns += f'<button class="filter-btn" data-cat="{cat}" style="--c:{color}">{cat}</button>\n'

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
      font-size: 17px;
      line-height: 1.8;
      transition: background 0.3s, color 0.3s;
    }}

    /* ヘッダー */
    header {{
      background: var(--hdr);
      backdrop-filter: blur(10px);
      -webkit-backdrop-filter: blur(10px);
      border-bottom: 1px solid var(--border);
      padding: 14px 20px 0;
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
    header h1 {{ font-size: 1.1rem; font-weight: 800; }}
    header .date {{ font-size: 0.78rem; color: var(--muted); margin-top: 2px; }}
    .saved-link {{
      font-size: 0.82rem;
      color: var(--subtext);
      text-decoration: none;
      border: 1px solid var(--border);
      border-radius: 20px;
      padding: 5px 12px;
      transition: background 0.2s;
    }}
    .saved-link:hover {{ background: var(--border); }}
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
    .filter-bar {{
      display: flex;
      gap: 8px;
      overflow-x: auto;
      padding-bottom: 12px;
      scrollbar-width: none;
    }}
    .filter-bar::-webkit-scrollbar {{ display: none; }}
    .filter-btn {{
      flex-shrink: 0;
      padding: 5px 14px;
      border: 2px solid var(--c, #888);
      border-radius: 20px;
      background: none;
      color: var(--c, #888);
      font-size: 0.8rem;
      font-weight: 700;
      cursor: pointer;
      transition: all 0.2s;
    }}
    .filter-btn.active, .filter-btn:hover {{
      background: var(--c, #888);
      color: #fff;
    }}
    .filter-btn[data-cat="all"] {{ --c: #555; }}

    /* メインコンテンツ */
    main {{
      max-width: 680px;
      margin: 0 auto;
      padding: 28px 20px 80px;
      display: flex;
      flex-direction: column;
      gap: 36px;
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
      border-radius: 14px;
      padding: 24px;
      box-shadow: var(--shadow);
      display: flex;
      flex-direction: column;
      gap: 14px;
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
      font-size: 1.05rem;
      font-weight: 700;
      line-height: 1.55;
      color: var(--text);
    }}
    .item .summary {{
      font-size: 0.96rem;
      color: var(--subtext);
      line-height: 1.9;
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
      font-size: 0.8rem;
      color: var(--muted);
      display: inline-block;
      margin-top: 2px;
    }}
    .actions {{
      display: flex;
      gap: 8px;
      border-top: 1px solid var(--border);
      padding-top: 12px;
      flex-wrap: wrap;
    }}
    .action-btn {{
      display: flex;
      align-items: center;
      gap: 4px;
      padding: 6px 12px;
      border: 1px solid var(--border);
      border-radius: 20px;
      background: none;
      color: var(--subtext);
      font-size: 0.8rem;
      cursor: pointer;
      text-decoration: none;
      transition: all 0.2s;
      white-space: nowrap;
    }}
    .action-btn:hover {{ background: var(--border); color: var(--text); }}
    .action-btn.star-btn.starred {{
      border-color: #f5a623;
      color: #f5a623;
      background: #fff8ed;
    }}
    [data-theme="dark"] .action-btn.star-btn.starred {{
      background: #2a2010;
    }}
    .toast {{
      position: fixed;
      bottom: 24px;
      left: 50%;
      transform: translateX(-50%) translateY(20px);
      background: #333;
      color: #fff;
      padding: 8px 18px;
      border-radius: 20px;
      font-size: 0.82rem;
      opacity: 0;
      transition: all 0.3s;
      pointer-events: none;
      z-index: 999;
    }}
    .toast.show {{ opacity: 1; transform: translateX(-50%) translateY(0); }}
  </style>
</head>
<body>
  <header>
    <div class="header-top">
      <div>
        <h1>News Digest</h1>
        <p class="date">{today} 更新</p>
      </div>
      <div style="display:flex;gap:8px;align-items:center">
        <a class="saved-link" href="saved.html">⭐ 保存済み</a>
        <button class="dark-btn" id="darkBtn">🌙 ダーク</button>
      </div>
    </div>
    <div class="filter-bar">
      {filter_btns}
    </div>
  </header>
  <main>
    {urgent_html}
    {sections_html}
  </main>
  <div class="toast" id="toast"></div>
  <script>
    // トースト通知
    function showToast(msg) {{
      const t = document.getElementById('toast');
      t.textContent = msg;
      t.classList.add('show');
      setTimeout(() => t.classList.remove('show'), 2000);
    }}

    // ダークモード
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

    // カテゴリフィルター
    document.querySelectorAll('.filter-btn').forEach(btn => {{
      btn.addEventListener('click', () => {{
        document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const cat = btn.dataset.cat;
        document.querySelectorAll('.category-section, .urgent-section').forEach(sec => {{
          if (cat === 'all') {{
            sec.style.display = '';
          }} else if (cat === 'urgent') {{
            sec.style.display = sec.classList.contains('urgent-section') ? '' : 'none';
          }} else {{
            sec.style.display = sec.dataset.cat === cat ? '' : 'none';
          }}
        }});
      }});
    }});

    // ⭐ 星ボタン（記事データごとlocalStorageに保存）
    const STAR_KEY = 'starred_articles';
    function getStarred() {{ return JSON.parse(localStorage.getItem(STAR_KEY) || '{{}}'); }}
    function saveStarred(obj) {{ localStorage.setItem(STAR_KEY, JSON.stringify(obj)); }}

    document.querySelectorAll('.star-btn').forEach(btn => {{
      const id = btn.dataset.id;
      if (getStarred()[id]) btn.classList.add('starred');
      btn.addEventListener('click', () => {{
        let obj = getStarred();
        if (obj[id]) {{
          delete obj[id];
          btn.classList.remove('starred');
          showToast('保存を解除しました');
        }} else {{
          obj[id] = {{
            id,
            title:       btn.dataset.title,
            summary:     btn.dataset.summary,
            source_name: btn.dataset.source,
            url:         btn.dataset.url,
            importance:  btn.dataset.importance,
            category:    btn.dataset.category,
          }};
          btn.classList.add('starred');
          showToast('⭐ 保存しました');
        }}
        saveStarred(obj);
      }});
    }});

    // 🤖 Claudeに聞くボタン（クリップボードコピー）
    document.querySelectorAll('.claude-btn').forEach(btn => {{
      btn.addEventListener('click', () => {{
        const title = btn.dataset.title;
        navigator.clipboard.writeText(title).then(() => {{
          showToast('タイトルをコピーしました');
          setTimeout(() => window.open('https://claude.ai/new', '_blank'), 300);
        }}).catch(() => {{
          window.open('https://claude.ai/new', '_blank');
        }});
      }});
    }});
  </script>
</body>
</html>
"""

    output_path = os.path.join(docs_dir, filename)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    # saved.html も同時に生成
    _render_saved_html(docs_dir)

    return output_path


def _render_saved_html(docs_dir: str) -> None:
    """保存済み記事一覧ページ（saved.html）を生成する。"""
    html = """<!DOCTYPE html>
<html lang="ja" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>保存済み記事 - News Digest</title>
  <style>
    :root {
      --bg: #f5f6f8; --surface: #fff; --text: #111; --subtext: #4a4a4a;
      --muted: #888; --border: #e4e4e4; --hdr: rgba(255,255,255,0.92);
      --shadow: 0 1px 6px rgba(0,0,0,0.07);
    }
    [data-theme="dark"] {
      --bg: #18191a; --surface: #242526; --text: #e4e6eb; --subtext: #b0b3b8;
      --muted: #777; --border: #3a3b3c; --hdr: rgba(24,25,26,0.95);
      --shadow: 0 1px 6px rgba(0,0,0,0.4);
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Hiragino Sans", "Noto Sans JP", sans-serif;
      background: var(--bg); color: var(--text); font-size: 16px; line-height: 1.75;
      transition: background 0.3s, color 0.3s;
    }
    header {
      background: var(--hdr); backdrop-filter: blur(10px);
      -webkit-backdrop-filter: blur(10px); border-bottom: 1px solid var(--border);
      padding: 14px 20px; position: sticky; top: 0; z-index: 100;
      display: flex; align-items: center; justify-content: space-between;
    }
    header h1 { font-size: 1.1rem; font-weight: 800; }
    .back-link {
      font-size: 0.82rem; color: var(--subtext); text-decoration: none;
      border: 1px solid var(--border); border-radius: 20px; padding: 5px 12px;
      transition: background 0.2s;
    }
    .back-link:hover { background: var(--border); }
    .dark-btn {
      background: none; border: 1px solid var(--border); border-radius: 20px;
      padding: 6px 14px; font-size: 0.82rem; cursor: pointer; color: var(--text);
      transition: background 0.2s;
    }
    .dark-btn:hover { background: var(--border); }
    main {
      max-width: 680px; margin: 0 auto; padding: 24px 16px 60px;
      display: flex; flex-direction: column; gap: 16px;
    }
    .empty {
      text-align: center; color: var(--muted); padding: 80px 20px;
      font-size: 0.95rem; line-height: 2;
    }
    .item {
      background: var(--surface); border-radius: 12px; padding: 20px;
      box-shadow: var(--shadow); display: flex; flex-direction: column; gap: 12px;
      animation: fadeUp 0.3s ease both;
    }
    @keyframes fadeUp {
      from { opacity: 0; transform: translateY(8px); }
      to   { opacity: 1; transform: translateY(0); }
    }
    .imp-badge {
      font-size: 0.72rem; font-weight: 700; padding: 2px 8px;
      border-radius: 20px; white-space: nowrap; width: fit-content;
    }
    .imp-urgent   { background: #ffe0e0; color: #cc0000; }
    .imp-important{ background: #fff3e0; color: #b35a00; }
    .imp-useful   { background: #e8f5e9; color: #2e7d32; }
    .item h2 { font-size: 1.0rem; font-weight: 700; line-height: 1.5; color: var(--text); }
    .summary { font-size: 0.93rem; color: var(--subtext); line-height: 1.8; }
    .category-tag { font-size: 0.75rem; color: var(--muted); }
    .actions {
      display: flex; gap: 8px; border-top: 1px solid var(--border);
      padding-top: 12px; flex-wrap: wrap;
    }
    .action-btn {
      display: flex; align-items: center; gap: 4px; padding: 6px 12px;
      border: 1px solid var(--border); border-radius: 20px; background: none;
      color: var(--subtext); font-size: 0.8rem; cursor: pointer;
      text-decoration: none; transition: all 0.2s; white-space: nowrap;
    }
    .action-btn:hover { background: var(--border); color: var(--text); }
    .action-btn.remove-btn { border-color: #ffcccc; color: #cc4444; }
    .action-btn.remove-btn:hover { background: #ffeeee; }
    .toast {
      position: fixed; bottom: 24px; left: 50%;
      transform: translateX(-50%) translateY(20px);
      background: #333; color: #fff; padding: 8px 18px;
      border-radius: 20px; font-size: 0.82rem; opacity: 0;
      transition: all 0.3s; pointer-events: none; z-index: 999;
    }
    .toast.show { opacity: 1; transform: translateX(-50%) translateY(0); }
  </style>
</head>
<body>
  <header>
    <div>
      <h1>⭐ 保存済み記事</h1>
    </div>
    <div style="display:flex;gap:8px;align-items:center">
      <a class="back-link" href="index.html">← トップ</a>
      <button class="dark-btn" id="darkBtn">🌙 ダーク</button>
    </div>
  </header>
  <main id="main"></main>
  <div class="toast" id="toast"></div>
  <script>
    // ダークモード
    const btn = document.getElementById('darkBtn');
    const root = document.documentElement;
    const savedTheme = localStorage.getItem('theme') || 'light';
    root.dataset.theme = savedTheme;
    btn.textContent = savedTheme === 'dark' ? '☀️ ライト' : '🌙 ダーク';
    btn.addEventListener('click', () => {
      const dark = root.dataset.theme !== 'dark';
      root.dataset.theme = dark ? 'dark' : 'light';
      btn.textContent = dark ? '☀️ ライト' : '🌙 ダーク';
      localStorage.setItem('theme', root.dataset.theme);
    });

    function showToast(msg) {
      const t = document.getElementById('toast');
      t.textContent = msg;
      t.classList.add('show');
      setTimeout(() => t.classList.remove('show'), 2000);
    }

    function impBadge(imp) {
      if (imp.startsWith('🔴')) return '<span class="imp-badge imp-urgent">🔴 緊急</span>';
      if (imp.startsWith('🟡')) return '<span class="imp-badge imp-important">🟡 重要</span>';
      return '<span class="imp-badge imp-useful">🟢 有益</span>';
    }

    const STAR_KEY = 'starred_articles';

    function render() {
      const main = document.getElementById('main');
      const obj = JSON.parse(localStorage.getItem(STAR_KEY) || '{}');
      const items = Object.values(obj);
      if (items.length === 0) {
        main.innerHTML = '<div class="empty">保存済みの記事はありません。<br>記事の ⭐ ボタンで保存できます。</div>';
        return;
      }
      main.innerHTML = items.map((a, i) => {
        const tweetText = encodeURIComponent((a.title || '') + ' ' + (a.url || ''));
        const tweetUrl  = 'https://twitter.com/intent/tweet?text=' + tweetText;
        const titleEsc  = (a.title || '').replace(/"/g, '&quot;');
        return `<div class="item" style="animation-delay:${i * 0.05}s" data-id="${a.id}">
          ${impBadge(a.importance || '🟢')}
          <h2>${a.title || ''}</h2>
          <p class="summary">${a.summary || ''}</p>
          <span class="category-tag">${a.category || ''} · ${a.source_name || ''}</span>
          <div class="actions">
            <button class="action-btn remove-btn" data-id="${a.id}">⭐ 保存を解除</button>
            <a class="action-btn" href="${tweetUrl}" target="_blank" rel="noopener">𝕏 投稿</a>
            <button class="action-btn claude-btn" data-title="${titleEsc}">🤖 Claudeに聞く</button>
          </div>
        </div>`;
      }).join('');

      // 解除ボタン
      document.querySelectorAll('.remove-btn').forEach(b => {
        b.addEventListener('click', () => {
          const obj = JSON.parse(localStorage.getItem(STAR_KEY) || '{}');
          delete obj[b.dataset.id];
          localStorage.setItem(STAR_KEY, JSON.stringify(obj));
          showToast('保存を解除しました');
          render();
        });
      });

      // Claudeボタン
      document.querySelectorAll('.claude-btn').forEach(b => {
        b.addEventListener('click', () => {
          navigator.clipboard.writeText(b.dataset.title).then(() => {
            showToast('タイトルをコピーしました');
            setTimeout(() => window.open('https://claude.ai/new', '_blank'), 300);
          }).catch(() => window.open('https://claude.ai/new', '_blank'));
        });
      });
    }

    render();
  </script>
</body>
</html>
"""
    saved_path = os.path.join(docs_dir, "saved.html")
    with open(saved_path, "w", encoding="utf-8") as f:
        f.write(html)


def _importance_badge(importance: str) -> str:
    """重要度バッジのHTMLを返す。"""
    if importance.startswith("🔴"):
        return f'<span class="imp-badge imp-urgent">🔴 緊急</span>'
    if importance.startswith("🟡"):
        return f'<span class="imp-badge imp-important">🟡 重要</span>'
    return f'<span class="imp-badge imp-useful">🟢 有益</span>'


def _build_item(article: dict, delay: float) -> str:
    """1記事分のカードHTMLを返す。"""
    import urllib.parse
    title       = article.get("title", "")
    summary     = article.get("summary", "")
    detail      = article.get("detail", "")
    source_name = article.get("source_name", "")
    url         = article.get("url", "")
    importance  = article.get("importance", "🟢")
    badge       = _importance_badge(importance)

    # 記事の一意ID（URLベース）
    article_id = urllib.parse.quote(url, safe="") if url else urllib.parse.quote(title, safe="")

    detail_block = ""
    if detail:
        detail_block = f"""<details>
        <summary></summary>
        <p class="detail-text">{detail}</p>
      </details>"""

    if source_name:
        source_block = f'<span class="source-name">📰 {source_name}</span>'
    else:
        source_block = ""

    # X投稿用 Twitter Intent URL
    tweet_text = urllib.parse.quote(f"{title} {url}" if url else title, safe="")
    tweet_url  = f"https://twitter.com/intent/tweet?text={tweet_text}"

    # タイトルのHTMLエスケープ（data属性用）
    title_escaped = title.replace('"', '&quot;')

    summary_escaped     = summary.replace('"', '&quot;')
    source_name_escaped = source_name.replace('"', '&quot;')
    url_escaped         = url.replace('"', '&quot;')
    importance_escaped  = importance.replace('"', '&quot;')
    category_escaped    = article.get("category", "").replace('"', '&quot;')

    actions = f"""<div class="actions">
        <button class="action-btn star-btn"
          data-id="{article_id}"
          data-title="{title_escaped}"
          data-summary="{summary_escaped}"
          data-source="{source_name_escaped}"
          data-url="{url_escaped}"
          data-importance="{importance_escaped}"
          data-category="{category_escaped}">⭐ 保存</button>
        <a class="action-btn" href="{tweet_url}" target="_blank" rel="noopener">𝕏 投稿</a>
        <button class="action-btn claude-btn" data-title="{title_escaped}">🤖 Claudeに聞く</button>
      </div>"""

    return f"""<div class="item" style="animation-delay:{delay:.2f}s">
      <div class="item-header">
        {badge}
      </div>
      <h2>{title}</h2>
      <p class="summary">{summary}</p>
      {detail_block}
      {source_block}
      {actions}
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
    return f"""<section class="category-section" data-cat="{category}">
      <p class="category-label" style="color:{color}">● {category}</p>
      {items}
    </section>"""
