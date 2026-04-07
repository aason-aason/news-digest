# CLAUDE.md — ニュースダイジェストツール
> 自動更新ファイル。セッション開始時に必ず読むこと。
> 最終更新：2026-04-07

---

## このプロジェクトについて

**あーそんinc.** が運営するニュース自動配信ツール。
海外テック・AI領域のニュースを収集・要約し、Discordに定時配信する。
実行環境はGitHub Actions（cron）。コードを触らずconfig.yamlだけで運用変更できることが最優先。

---

## ファイル構成

```
news-digest/
├── CLAUDE.md          ← このファイル（セッション間の引き継ぎ）
├── config.yaml        ← 配信設定・キーワード・ソースon/off
├── main.py            ← エントリポイント。全モジュールを呼び出す
├── fetcher.py         ← ニュース取得（RSS / arXiv / HackerNews / Reddit）
├── summarizer.py      ← AI要約（Claude API or Groq fallback）
├── notifier.py        ← Discord Webhook送信（URL通知のみ）
└── renderer.py        ← HTMLページ生成（GitHub Pages用）
```

---

## 各ファイルの責務

### main.py
- fetcher → summarizer → notifier の順で呼び出す
- config.yamlを読み込んで各モジュールに渡す
- エラーが起きても配信を止めない（ソース単位でスキップ）

### fetcher.py
- ソースごとにクラスまたは関数を分ける
- 返り値は統一フォーマット：`{"title": str, "url": str, "summary_raw": str, "source": str}`
- ソースの優先順：TechCrunch等RSS → arXiv → HackerNews → Reddit → 国内RSS

### summarizer.py
- デフォルト：Claude API（claude-sonnet-4-20250514）
- fallback：Groq（config.yamlで `use_groq: true` にすると切替）
- 要約言語・長さはconfig.yamlから取得
- APIキーは環境変数から取得（ハードコード禁止）

### notifier.py
- Discord Webhook URLは環境変数 `DISCORD_WEBHOOK_URL` から取得
- メッセージフォーマット：タイトル・要約・元記事URL・ソース名
- 1メッセージあたり2000文字制限に注意（超えたら分割送信）

### config.yaml
```yaml
schedule:
  cron: "0 8 * * *"   # JST 17:00（UTC 8:00）

filter:
  include_keywords: ["AI", "LLM", "automation"]
  exclude_keywords: ["crypto", "NFT"]

sources:
  techcrunch_rss: true
  arxiv: true
  hackernews: true
  reddit: true
  domestic_rss: true
  # 音楽・DTM系
  bedroom_producers_blog: true   # プラグイン・音源の無料配布・新作
  kvr_audio: true                # VST/AUプラグイン新着・セール情報
  musicradar: true               # 機材・DAW・制作テクニック全般
  attack_magazine: true          # 電子音楽・ミックス・マスタリング寄り
  dtm_station: true              # 国内DTM情報
  reddit_WeAreTheMusicMakers: true
  reddit_edmproduction: true

summary:
  language: "ja"
  length: "short"   # short / medium / long
  use_groq: false   # true にするとGroqで要約（コスト0）

cost:
  monthly_limit_yen: 500   # 超えたら自動でGroqに切替（Phase 3で実装）

digest:
  mode: "category"              # カテゴリ別にまとめる
  topics_per_category: 3        # カテゴリ内のトピック数（AIが内容に応じて判断）
  articles_per_topic: 3         # トピックごとに参照する記事数
  include_source_links: true    # 末尾に元記事リンク一覧を添付
```

---

## ダイジェスト仕様（確定）

### 配信構造
- **本文**：GitHub Pagesに毎日HTMLとして生成・公開
- **通知**：DiscordにURLを1行だけ送る（「今日のまとめを更新しました → URL」）
- 全カテゴリを1ページにまとめて読める

### GitHub Pages
- リポジトリ：`news-digest` の `gh-pages` ブランチ or `docs/` フォルダ
- 公開URL：`https://{GitHubユーザー名}.github.io/news-digest/`
- GitHub Actionsがindex.htmlを毎日上書きpushする
- 過去分はarchive/YYYY-MM-DD.htmlとして保存する

### カテゴリ構造
各カテゴリ内はAIが複数記事をトピック単位に束ねて要約する。

### Discordの出力フォーマット
```
🤖 【テック・AI】今日のまとめ
─────────────────
**① OpenAI / エージェントAIの加速**
新モデル発表とMicrosoftのCopilot刷新が重なり、
エージェント型AIへの移行が業界全体で加速。

**② RAG精度改善の新潮流**
arXivで関連論文が複数公開。
「何を検索しないか」の設計が重要という知見が増えている。

**③ OSS LLMのコスト競争**
Llama系の新モデルがコスト比で更新。
Claude / GPT-4oとの使い分けが現実的な選択肢に。

📎 参照記事
・https://techcrunch.com/...
・https://arxiv.org/...
・https://news.ycombinator.com/...
```

### summarizer.pyへの影響
- 単記事要約ではなく、複数記事（タイトル+本文冒頭）をまとめてプロンプトに渡す
- AIへの指示：「以下の記事群をトピックごとに束ね、各トピック3〜5行で要約せよ」
- トピック数は `topics_per_category` を上限として、AIが内容に応じて判断する

---

## 環境変数（GitHub Secretsに登録）

| 変数名 | 用途 |
|--------|------|
| `ANTHROPIC_API_KEY` | Claude API |
| `GROQ_API_KEY` | Groq fallback |
| `DISCORD_WEBHOOK_URL` | Discord通知先 |
| `GITHUB_TOKEN` | GitHub PagesへのPush（Actions自動付与のため登録不要） |

---

## GitHub Actions設定

`.github/workflows/news-digest.yml` に記述。
- cron: config.yamlの `schedule.cron` に合わせて設定
- Python 3.11
- 依存パッケージは `requirements.txt` で管理

---

## 開発フェーズと現在地

| フェーズ | 内容 | 状態 |
|----------|------|------|
| Phase 1 | RSS + Claude + Discord 最小構成 | 🔲 未着手 |
| Phase 2 | arXiv / HackerNews / Reddit 追加 | 🔲 未着手 |
| Phase 3 | Groq fallback / コスト監視 | 🔲 未着手 |
| Phase 4 | X投稿ソース追加 | 🔲 後日 |

---

## コーディング規約

- Python 3.11
- 型ヒントを書く
- 関数単位でコメントを書く（日本語可）
- エラーはloggingモジュールで記録。printは使わない
- 外部APIのタイムアウトは10秒を上限にする
- テストは `tests/` ディレクトリに置く（pytest）

---

## RSSソース一覧

| キー | URL |
|------|-----|
| techcrunch_rss | https://techcrunch.com/feed/ |
| domestic_rss | https://feeds.feedburner.com/itmedia-news |
| bedroom_producers_blog | https://bedroomproducersblog.com/feed/ |
| kvr_audio | https://www.kvraudio.com/rss/latest_news.php |
| musicradar | https://www.musicradar.com/feeds/all |
| attack_magazine | https://www.attackmagazine.com/feed/ |
| dtm_station | https://dtmstation.com/feed |
| reddit_WeAreTheMusicMakers | Reddit API（r/WeAreTheMusicMakers） |
| reddit_edmproduction | Reddit API（r/edmproduction） |



作業が終わったら、このファイルの以下の項目を更新すること：
- 「開発フェーズと現在地」の状態（🔲 未着手 / 🔄 進行中 / ✅ 完了）
- 変更・追加した仕様があれば該当セクションに追記
- 次のセッションへの申し送り事項があれば末尾に追記

---

## 申し送り事項
（最初のセッション開始時に追記すること）
---

## 重要度判断基準（確定）

ClaudeがあーそんIncの文脈で記事の重要度を判断する基準。

### 🔴 緊急（即確認）
- Claude APIの仕様変更・障害・価格変更
- Gemini APIの仕様変更（コミドネに影響）
- Supabase・Vercel・GitHubの障害
- Next.js・Supabaseのセキュリティ脆弱性
- GitHub Actionsの仕様変更
- OpenWeatherMap APIの仕様変更・無料枠変更
- n8nのアップデート・仕様変更
- A8.netなどアフィリエイトASPの規約変更・サービス終了
- Reddit APIの仕様変更
- Discord Webhookの仕様変更
- Groq APIの仕様変更

### 🟡 重要（今日中に確認）
- コミドネ競合プロダクトのリリース
- DTM・音楽制作ツールの新機能・セール
- 個人開発者の収益事例（月5万円以上）
- アフィリエイト・SEOのアルゴリズム変更
- フリーランス映像編集の市場動向・単価相場
- note・Zennのアルゴリズム変更
- Anthropicの新機能・新モデル発表（Claude Code含む）
- フリーランス・個人事業主向けの税制・法律変更（日本）
- App Store・Google Playのポリシー変更
- Uberの報酬体系変更
- クラウドワークスの手数料・規約変更
- AI動画生成ツールの進化（Sora・Runway系）
- X・Instagramのアルゴリズム変更

### 🟢 有益（時間あるときに）
- AI・テックの一般的な動向
- 音楽業界トレンド
- ビジネス戦略・経営の知見
- 音楽×AIの最新ツール（Suno・Udio系）
- 個人開発者のマーケティング事例
- 生産性・習慣系の知見
- 著作権・音楽ライセンスの動向

### 表示ルール
- 🔴 は最上部に別枠で表示・Discordにも即時通知
- 🟡 は各カテゴリの先頭に表示
- 🟢 は通常表示
- 該当なしの日は該当カテゴリを省略する
---

## UI・表示仕様（確定）

### デバイス
- スマホ優先（レスポンシブ対応）
- 1カラム
- 余白多め・フォント大きめ

### レイアウト
- 一覧型
- 🔴緊急アラートは最上部に別枠で固定表示
- カテゴリ別にセクション分け

### 各トピックの表示
- デフォルトで十分な量の要約を表示（薄い要約は禁止）
- 「もっと詳しく」で更に深掘り要約を折りたたみ展開
- 参照記事リンクは各トピック直下にサイト名のみ表示（URLは非表示）

### 言語・翻訳方針
- AIまとめは日本語で完結させる
- 元記事は海外ソース維持（Chromeの自動翻訳で対応）
- まとめを読むだけで完結する設計を優先する
