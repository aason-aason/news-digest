"""
summarizer.py: Gemini Flashで記事をカテゴリ別・重要度付きで日本語要約する
"""

import os
import json
import re
import logging
from google import genai

logger = logging.getLogger(__name__)

# 重要度判断基準（プロンプト用）
IMPORTANCE_CRITERIA = """
重要度の判断基準：

🔴 緊急（即確認）:
- Claude API / Gemini API の仕様変更・障害・価格変更
- Supabase・Vercel・GitHubの障害
- Next.js・Supabaseのセキュリティ脆弱性
- GitHub Actionsの仕様変更
- OpenWeatherMap APIの仕様変更・無料枠変更
- n8nのアップデート・仕様変更
- A8.netなどアフィリエイトASPの規約変更・サービス終了
- Reddit / Discord Webhook / Groq APIの仕様変更

🟡 重要（今日中に確認）:
- コミドネ競合プロダクトのリリース
- DTM・音楽制作ツールの新機能・セール
- 個人開発者の収益事例（月5万円以上）
- アフィリエイト・SEOのアルゴリズム変更
- フリーランス映像編集の市場動向・単価相場
- Anthropicの新機能・新モデル発表（Claude Code含む）
- フリーランス・個人事業主向けの税制・法律変更（日本）
- App Store・Google Playのポリシー変更
- AI動画生成ツールの進化（Sora・Runway系）
- X・Instagramのアルゴリズム変更
- Uberの報酬体系変更
- コミドネの競合・類似プロダクトの価格変更・新機能
- サブスク型個人プロダクトの収益化事例
- クリエイター向けマネタイズの新手法
- 個人開発者の撤退・失敗事例
- App Store・Google Playのランキング動向

🟢 有益（時間あるときに）:
- AI・テックの一般的な動向
- 音楽業界トレンド
- ビジネス戦略・経営の知見
- 音楽×AIの最新ツール（Suno・Udio系）
- 個人開発者のマーケティング事例
- 生産性・習慣系の知見
- 著作権・音楽ライセンスの動向
- 個人ブランディング・SNS戦略の事例
- ソロ起業家・ひとり法人の経営ノウハウ
- クリエイターエコノミーの市場動向
- 個人開発者のプロダクト成長事例
- 個人開発×AIツール活用の最新動向
- 海外インディーハッカーの収益公開情報
"""


def summarize_articles(articles: list[dict], config: dict) -> list[dict]:
    """記事リストをGeminiで要約し、重要度・カテゴリ付きのリストを返す。"""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("GEMINI_API_KEY が設定されていません")

    client = genai.Client(api_key=api_key)

    # 記事リストをテキストに整形（URLをindex番号で管理）
    url_map = {}
    articles_text = ""
    for i, article in enumerate(articles, 1):
        url_map[i] = article.get("link", "")
        articles_text += (
            f"\n記事{i}【{article.get('category', '')}】"
            f"（ソース: {article.get('source', '')}）\n"
            f"タイトル: {article['title']}\n"
            f"概要: {article['summary']}\n---\n"
        )

    prompt = f"""以下はテック・ビジネス・音楽DTM分野の最新記事です。
各記事について日本語でJSON配列を返してください。

{IMPORTANCE_CRITERIA}

出力形式（JSONのみ、説明文不要）:
[
  {{
    "article_index": 記事番号（整数）,
    "category": "カテゴリ名（テック／ビジネス／音楽・DTM）",
    "title": "記事タイトルの日本語訳",
    "importance": "🔴 または 🟡 または 🟢",
    "summary": "読むだけで内容が完結する、2〜4文の十分な要約。何が起きたか・なぜ重要か・どんな影響があるかを含める。薄い要約は禁止。",
    "detail": "さらに詳しい説明。背景・技術的詳細・具体的な数字・入手方法・価格などを含めた4〜6文。",
    "source_name": "ソース名（例: TechCrunch、DTMステーション）"
  }}
]

{articles_text}
"""

    response = client.models.generate_content(
        model=config["gemini"]["model"],
        contents=prompt,
    )

    text = response.text.strip()
    match = re.search(r'\[.*\]', text, re.DOTALL)
    if match:
        try:
            items = json.loads(match.group())
            # article_indexを使ってURLを付与
            for item in items:
                idx = item.pop("article_index", None)
                if idx and idx in url_map:
                    item["url"] = url_map[idx]
            return items
        except json.JSONDecodeError as e:
            logger.error(f"JSONパースエラー: {e}")
            return []

    logger.error("JSONが見つかりませんでした")
    return []
