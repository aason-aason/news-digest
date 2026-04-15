"""
renderer.py: 要約データをUI仕様に沿ったindex.htmlに変換してdocs/に保存する

UI仕様:
- エディトリアルスタイル（新聞・雑誌風）
- セリフ体ロゴ・タイトル
- カテゴリをセクション見出しで区切る構造
- スマホ優先・1カラム
- 🔴緊急は最上部に別枠固定
"""

import os
from datetime import datetime

CATEGORY_COLOR = {
    "テック": "#1a1a1a",
    "ビジネス": "#1a1a1a",
    "音楽・DTM": "#1a1a1a",
}

IMPORTANCE_LABEL = {
    "🔴": "緊急",
    "🟡": "重要",
    "🟢": "有益",
}

def render_html(articles: list[dict], config: dict) -> str:
    """要約データをHTMLに変換してdocs/に保存し、パスを返す。"""
    docs_dir = config["output"]["docs_dir"]
    filename = config["output"]["filename"]
    os.makedirs(docs_dir, exist_ok=True)

    today = datetime.now().strftime("%Y年%m月%d日")
    today_vol = datetime.now().strftime("%Y.%m.%d")

    # 重要度で分類
    urgent = [a for a in articles if a.get("importance", "").startswith("🔴")]
    normal = [a for a in articles if not a.get("importance", "").startswith("🔴")]

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
        filter_btns += '<button class="filter-btn" data-cat="urgent">🔴 緊急</button>\n'
    for cat in categories:
        filter_btns += f'<button class="filter-btn" data-cat="{cat}">{cat}</button>\n'

    html = f"""<!DOCTYPE html>
<html lang="ja" data-theme="light">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>News Digest - {today}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Noto+Serif+JP:wght@700&display=swap" rel="stylesheet">
<style>
:root {{
  --bg: #f9f7f4;
  --surface: #ffffff;
  --text: #111111;
  --subtext: #444444;
  --muted: #888888;
  --border: #e0ddd8;
  --border-strong: #111111;
  --hdr: rgba(249,247,244,0.95);
  --serif: 'Playfair Display', 'Noto Serif JP', Georgia, serif;
}}
[data-theme="dark"] {{
  --bg: #1a1918;
  --surface: #242220;
  --text: #f0ede8;
  --subtext: #b0ada8;
  --muted: #666360;
  --border: #333130;
  --border-strong: #f0ede8;
  --hdr: rgba(26,25,24,0.97);
}}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
  font-family: -apple-system, BlinkMacSystemFont, "Hiragino Sans", "Noto Sans JP", sans-serif;
  background: var(--bg);
  color: var(--text);
  font-size: 16px;
  line-height: 1.8;
  transition: background 0.3s, color 0.3s;
}}

/* ヘッダー */
header {{
  background: var(--hdr);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border-bottom: 2px solid var(--border-strong);
  padding: 16px 20px 0;
  position: sticky;
  top: 0;
  z-index: 100;
}}
.header-top {{
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  padding-bottom: 10px;
}}
.header-logo {{
  font-family: var(--serif);
  font-size: 26px;
  font-weight: 700;
  color: var(--text);
  letter-spacing: -0.01em;
  line-height: 1;
}}
.header-meta {{
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}}
.header-date {{
  font-size: 10px;
  letter-spacing: 0.1em;
  color: var(--muted);
}}
.header-links {{
  display: flex;
  gap: 8px;
}}
.header-link {{
  font-size: 11px;
  color: var(--subtext);
  text-decoration: none;
  border: 1px solid var(--border);
  border-radius: 20px;
  padding: 4px 11px;
  transition: background 0.2s;
  background: none;
  cursor: pointer;
  font-family: inherit;
}}
.header-link:hover {{ background: var(--border); color: var(--text); }}
.filter-bar {{
  display: flex;
  gap: 0;
  overflow-x: auto;
  scrollbar-width: none;
  border-top: 1px solid var(--border);
  margin-top: 10px;
}}
.filter-bar::-webkit-scrollbar {{ display: none; }}
.filter-btn {{
  flex-shrink: 0;
  padding: 8px 16px;
  border: none;
  border-bottom: 2px solid transparent;
  background: none;
  color: var(--muted);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.07em;
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: -2px;
}}
.filter-btn.active, .filter-btn:hover {{
  color: var(--text);
  border-bottom-color: var(--border-strong);
}}

/* メインコンテンツ */
main {{
  max-width: 680px;
  margin: 0 auto;
  padding: 32px 20px 80px;
}}

/* 緊急セクション */
.urgent-section {{
  border: 2px solid #cc0000;
  border-radius: 4px;
  padding: 20px;
  margin-bottom: 40px;
}}
.urgent-label {{
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.14em;
  color: #cc0000;
  margin-bottom: 16px;
}}

/* カテゴリセクション */
.category-section {{
  margin-bottom: 40px;
}}
.category-label {{
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.14em;
  color: var(--muted);
  margin-bottom: 0;
}}
.category-label::after {{
  content: '';
  flex: 1;
  height: 1px;
  background: var(--border);
}}
.category-divider {{
  border: none;
  border-top: 1px solid var(--border);
  margin: 0;
}}

/* 記事 */
.item {{
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 16px;
  padding: 20px 0;
  border-bottom: 1px solid var(--border);
  align-items: start;
  animation: fadeIn 0.3s ease both;
}}
.item:first-of-type {{
  border-top: 1px solid var(--border);
  margin-top: 12px;
}}
@keyframes fadeIn {{
  from {{ opacity: 0; transform: translateY(6px); }}
  to {{ opacity: 1; transform: translateY(0); }}
}}
.item-body {{ min-width: 0; }}
.item-meta {{
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}}
.imp-badge {{
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 0.08em;
  padding: 2px 7px;
  border-radius: 3px;
}}
.imp-urgent {{ background: #ffe0e0; color: #cc0000; }}
.imp-important {{ background: #fff3e0; color: #8a4800; }}
.imp-useful {{ background: #e8f5e9; color: #2e7d32; }}
.item-source {{
  font-size: 10px;
  color: var(--muted);
  letter-spacing: 0.06em;
}}
.item h2 {{
  font-family: var(--serif);
  font-size: 16px;
  font-weight: 700;
  line-height: 1.5;
  color: var(--text);
  margin-bottom: 8px;
}}
.item .summary {{
  font-size: 13px;
  color: var(--subtext);
  line-height: 1.85;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}}
details {{
  margin-top: 10px;
  border-top: 1px solid var(--border);
  padding-top: 10px;
}}
summary {{
  font-size: 12px;
  color: var(--muted);
  cursor: pointer;
  list-style: none;
  user-select: none;
}}
summary::-webkit-details-marker {{ display: none; }}
summary::before {{ content: "▶ 続きを読む"; }}
details[open] summary::before {{ content: "▲ 閉じる"; }}
.detail-text {{
  font-size: 13px;
  color: var(--subtext);
  line-height: 1.85;
  margin-top: 10px;
}}
.item-thumb {{
  width: 72px;
  height: 54px;
  background: var(--border);
  border-radius: 3px;
  flex-shrink: 0;
}}
.item-actions {{
  display: flex;
  gap: 10px;
  margin-top: 12px;
  flex-wrap: wrap;
}}
.action-btn {{
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 0;
  border: none;
  background: none;
  color: var(--muted);
  font-size: 11px;
  cursor: pointer;
  text-decoration: none;
  transition: color 0.2s;
  font-family: inherit;
}}
.action-btn:hover {{ color: var(--text); }}
.action-btn.star-btn.starred {{ color: #b35a00; }}
.action-sep {{
  color: var(--border);
  font-size: 11px;
  line-height: 1;
  align-self: center;
}}

.toast {{
  position: fixed;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%) translateY(20px);
  background: var(--text);
  color: var(--bg);
  padding: 8px 18px;
  border-radius: 20px;
  font-size: 12px;
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
    <div class="header-logo">News Digest</div>
    <div class="header-meta">
      <span class="header-date">{today_vol}</span>
      <div class="header-links">
        <a class="header-link" href="saved.html">⭐ 保存済み</a>
        <button class="header-link" id="darkBtn">🌙 ダーク</button>
      </div>
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

// ⭐ 保存
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
        title: btn.dataset.title,
        summary: btn.dataset.summary,
        source_name: btn.dataset.source,
        url: btn.dataset.url,
        importance: btn.dataset.importance,
        category: btn.dataset.category,
      }};
      btn.classList.add('starred');
      showToast('⭐ 保存しました');
    }}
    saveStarred(obj);
  }});
}});

// 🤖 Claudeに聞く
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
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Noto+Serif+JP:wght@700&display=swap" rel="stylesheet">
<style>
:root {
  --bg: #f9f7f4; --surface: #fff; --text: #111; --subtext: #444;
  --muted: #888; --border: #e0ddd8; --border-strong: #111;
  --hdr: rgba(249,247,244,0.95);
  --serif: 'Playfair Display', 'Noto Serif JP', Georgia, serif;
}
[data-theme="dark"] {
  --bg: #1a1918; --surface: #242220; --text: #f0ede8; --subtext: #b0ada8;
  --muted: #666360; --border: #333130; --border-strong: #f0ede8;
  --hdr: rgba(26,25,24,0.97);
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Hiragino Sans", "Noto Sans JP", sans-serif;
  background: var(--bg); color: var(--text); font-size: 16px; line-height: 1.8;
  transition: background 0.3s, color 0.3s;
}
header {
  background: var(--hdr); backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border-bottom: 2px solid var(--border-strong);
  padding: 16px 20px;
  position: sticky; top: 0; z-index: 100;
  display: flex; align-items: center; justify-content: space-between;
}
.header-logo { font-family: var(--serif); font-size: 20px; font-weight: 700; }
.header-links { display: flex; gap: 8px; }
.header-link {
  font-size: 11px; color: var(--subtext); text-decoration: none;
  border: 1px solid var(--border); border-radius: 20px; padding: 4px 11px;
  transition: background 0.2s; background: none; cursor: pointer; font-family: inherit;
}
.header-link:hover { background: var(--border); color: var(--text); }
main { max-width: 680px; margin: 0 auto; padding: 32px 20px 80px; }
.empty { text-align: center; color: var(--muted); padding: 80px 20px; font-size: 14px; line-height: 2.2; }
.item {
  padding: 20px 0; border-bottom: 1px solid var(--border);
  animation: fadeIn 0.3s ease both;
}
.item:first-child { border-top: 1px solid var(--border); }
@keyframes fadeIn { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }
.item-meta { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
.imp-badge { font-size: 9px; font-weight: 700; letter-spacing: 0.08em; padding: 2px 7px; border-radius: 3px; }
.imp-urgent { background: #ffe0e0; color: #cc0000; }
.imp-important { background: #fff3e0; color: #8a4800; }
.imp-useful { background: #e8f5e9; color: #2e7d32; }
.item-source { font-size: 10px; color: var(--muted); }
.item h2 { font-family: var(--serif); font-size: 16px; font-weight: 700; line-height: 1.5; margin-bottom: 8px; }
.summary { font-size: 13px; color: var(--subtext); line-height: 1.85; }
.item-actions { display: flex; gap: 10px; margin-top: 12px; flex-wrap: wrap; }
.action-btn {
  display: flex; align-items: center; gap: 4px; padding: 4px 0;
  border: none; background: none; color: var(--muted); font-size: 11px;
  cursor: pointer; text-decoration: none; transition: color 0.2s; font-family: inherit;
}
.action-btn:hover { color: var(--text); }
.action-btn.remove-btn { color: #cc4444; }
.action-sep { color: var(--border); font-size: 11px; align-self: center; }
.toast {
  position: fixed; bottom: 24px; left: 50%;
  transform: translateX(-50%) translateY(20px);
  background: var(--text); color: var(--bg); padding: 8px 18px;
  border-radius: 20px; font-size: 12px; opacity: 0;
  transition: all 0.3s; pointer-events: none; z-index: 999;
}
.toast.show { opacity: 1; transform: translateX(-50%) translateY(0); }
</style>
</head>
<body>
<header>
  <div class="header-logo">News Digest</div>
  <div class="header-links">
    <a class="header-link" href="index.html">← トップ</a>
    <button class="header-link" id="darkBtn">🌙 ダーク</button>
  </div>
</header>
<main id="main"></main>
<div class="toast" id="toast"></div>
<script>
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
    const tweetUrl = 'https://twitter.com/intent/tweet?text=' + tweetText;
    const titleEsc = (a.title || '').replace(/"/g, '&quot;');
    return `<div class="item" style="animation-delay:${i * 0.05}s" data-id="${a.id}">
      <div class="item-meta">${impBadge(a.importance || '🟢')}<span class="item-source">${a.source_name || ''}</span></div>
      <h2>${a.title || ''}</h2>
      <p class="summary">${a.summary || ''}</p>
      <div class="item-actions">
        <button class="action-btn remove-btn" data-id="${a.id}">⭐ 保存を解除</button>
        <span class="action-sep">|</span>
        <a class="action-btn" href="${tweetUrl}" target="_blank" rel="noopener">𝕏 投稿</a>
        <span class="action-sep">|</span>
        <button class="action-btn claude-btn" data-title="${titleEsc}">🤖 Claudeに聞く</button>
      </div>
    </div>`;
  }).join('');
  document.querySelectorAll('.remove-btn').forEach(b => {
    b.addEventListener('click', () => {
      const obj = JSON.parse(localStorage.getItem(STAR_KEY) || '{}');
      delete obj[b.dataset.id];
      localStorage.setItem(STAR_KEY, JSON.stringify(obj));
      showToast('保存を解除しました');
      render();
    });
  });
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
        return '<span class="imp-badge imp-urgent">🔴 緊急</span>'
    if importance.startswith("🟡"):
        return '<span class="imp-badge imp-important">🟡 重要</span>'
    return '<span class="imp-badge imp-useful">🟢 有益</span>'


def _build_item(article: dict, delay: float) -> str:
    """1記事分のHTMLを返す。"""
    import urllib.parse

    title = article.get("title", "")
    summary = article.get("summary", "")
    detail = article.get("detail", "")
    source_name = article.get("source_name", "")
    url = article.get("url", "")
    importance = article.get("importance", "🟢")
    badge = _importance_badge(importance)

    article_id = urllib.parse.quote(url, safe="") if url else urllib.parse.quote(title, safe="")

    detail_block = ""
    if detail:
        detail_block = f"""<details>
<summary></summary>
<p class="detail-text">{detail}</p>
</details>"""

    tweet_text = urllib.parse.quote(f"{title} {url}" if url else title, safe="")
    tweet_url = f"https://twitter.com/intent/tweet?text={tweet_text}"

    title_escaped = title.replace('"', '&quot;')
    summary_escaped = summary.replace('"', '&quot;')
    source_name_escaped = source_name.replace('"', '&quot;')
    url_escaped = url.replace('"', '&quot;')
    importance_escaped = importance.replace('"', '&quot;')
    category_escaped = article.get("category", "").replace('"', '&quot;')

    return f"""<div class="item" style="animation-delay:{delay:.2f}s">
  <div class="item-body">
    <div class="item-meta">
      {badge}
      <span class="item-source">{source_name}</span>
    </div>
    <h2>{title}</h2>
    <p class="summary">{summary}</p>
    {detail_block}
    <div class="item-actions">
      <button class="action-btn star-btn"
        data-id="{article_id}"
        data-title="{title_escaped}"
        data-summary="{summary_escaped}"
        data-source="{source_name_escaped}"
        data-url="{url_escaped}"
        data-importance="{importance_escaped}"
        data-category="{category_escaped}">⭐ 保存</button>
      <span class="action-sep">|</span>
      <a class="action-btn" href="{tweet_url}" target="_blank" rel="noopener">𝕏 投稿</a>
      <span class="action-sep">|</span>
      <button class="action-btn claude-btn" data-title="{title_escaped}">🤖 Claudeに聞く</button>
    </div>
  </div>
  <div class="item-thumb"></div>
</div>"""


def _build_urgent(articles: list[dict]) -> str:
    """🔴緊急アラートセクションのHTMLを返す。"""
    items = "\n".join(_build_item(a, i * 0.05) for i, a in enumerate(articles))
    return f"""<section class="urgent-section">
  <p class="urgent-label">🔴 緊急アラート</p>
  {items}
</section>"""


def _build_section(category: str, articles: list[dict]) -> str:
    """カテゴリセクションのHTMLを返す。"""
    items = "\n".join(_build_item(a, i * 0.05) for i, a in enumerate(articles))
    return f"""<section class="category-section" data-cat="{category}">
  <p class="category-label">{category}</p>
  {items}
</section>"""
