"""
notifier.py: DiscordにGitHub PagesのURLを通知する
"""

import os
import urllib.request
import json


def notify_discord(config: dict) -> None:
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        raise EnvironmentError("DISCORD_WEBHOOK_URL が設定されていません")
    print(f"  [debug] Webhook URL先頭30文字: {webhook_url[:30]}")

    pages_url = config["github_pages"]["url"]
    message = f"今日のまとめを更新しました → {pages_url}"

    payload = json.dumps({"content": message}).encode("utf-8")

    req = urllib.request.Request(
        webhook_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(req) as res:
        if res.status != 204:
            raise RuntimeError(f"Discord通知に失敗しました（status: {res.status}）")
