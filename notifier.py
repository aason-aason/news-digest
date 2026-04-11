"""
notifier.py: GmailでGitHub PagesのURLまたは緊急アラートを通知する

通常時 : 件名「📰 今日のニュースまとめを更新しました」+ URL
緊急時 : 件名「🔴【緊急】{タイトル}」+ アラート詳細
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


TO_ADDRESS = "nobu.dougahennsyuu@gmail.com"
SMTP_HOST  = "smtp.gmail.com"
SMTP_PORT  = 587


def _send_mail(sender: str, password: str, subject: str, body: str) -> None:
    """Gmailで1通メールを送る。"""
    msg = MIMEMultipart()
    msg["From"]    = sender
    msg["To"]      = TO_ADDRESS
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login(sender, password)
        smtp.sendmail(sender, TO_ADDRESS, msg.as_string())


def notify_gmail(config: dict, articles: list[dict] | None = None) -> None:
    """
    Gmailで通知を送る。
    articles に 🔴 が含まれる場合は緊急メールを送信。
    """
    sender   = os.environ.get("GMAIL_SENDER")
    password = os.environ.get("GMAIL_APP_PASSWORD")

    if not sender or not password:
        raise EnvironmentError(
            "GMAIL_SENDER または GMAIL_APP_PASSWORD が設定されていません"
        )

    pages_url = config["github_pages"]["url"]
    urgent    = [a for a in (articles or []) if a.get("importance", "").startswith("🔴")]

    if urgent:
        first_title = urgent[0].get("title", "緊急アラート")
        subject = f"🔴【緊急】{first_title}"

        lines = [f"🔴 緊急アラート（{len(urgent)}件）\n"]
        for a in urgent:
            lines.append(f"■ {a.get('title', '')}")
            lines.append(a.get("summary", ""))
            if a.get("detail"):
                lines.append(a["detail"])
            lines.append(f"ソース: {a.get('source_name', '')}")
            lines.append("")
        lines.append(f"詳細はこちら → {pages_url}")
        body = "\n".join(lines)
    else:
        subject = "📰 今日のニュースまとめを更新しました"
        body    = f"今日のまとめを更新しました。\n\n{pages_url}"

    _send_mail(sender, password, subject, body)
    print(f"  → Gmail送信完了（宛先: {TO_ADDRESS}、件名: {subject}）")
