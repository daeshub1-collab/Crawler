import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from config import MAIL_TO, MAIL_SUBJECT
from sent_log import save_sent_id, append_to_html_log
import os
from dotenv import load_dotenv

load_dotenv()

GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")


def build_html_body(items: list) -> str:
    """이메일 본문 HTML 생성"""
    now = datetime.now().strftime("%Y년 %m월 %d일")

    rows = ""
    for item in items:
        rows += f"""
        <tr>
            <td style="padding:8px; border:1px solid #ddd;">{item.get('date', '')}</td>
            <td style="padding:8px; border:1px solid #ddd;">{item.get('source', '')}</td>
            <td style="padding:8px; border:1px solid #ddd;">
                <a href="{item.get('url', '')}">{item.get('title', '')}</a>
            </td>
        </tr>"""

    html = f"""
<html>
<body style="font-family: Arial, sans-serif; font-size: 14px;">
    <h2>🏭 사출기 북미 시장 & 관세 모니터링</h2>
    <p>📅 기준일: {now} &nbsp;|&nbsp; 총 <b>{len(items)}건</b> 수집</p>
    <table style="border-collapse:collapse; width:100%;">
        <tr style="background:#f2f2f2;">
            <th style="padding:8px; border:1px solid #ddd; width:120px;">날짜</th>
            <th style="padding:8px; border:1px solid #ddd; width:150px;">출처</th>
            <th style="padding:8px; border:1px solid #ddd;">제목</th>
        </tr>
        {rows}
    </table>
    <br>
    <p style="color:gray; font-size:12px;">※ 이 메일은 자동 발송됩니다.</p>
</body>
</html>
"""
    return html


def send_mail(items: list, dry_run: bool = False):
    if not items:
        print("📭 발송할 공고가 없습니다.")
        return

    html_body = build_html_body(items)

    if dry_run:
        print(f"\n[DRY-RUN] 이메일 발송 생략 — 수집된 공고 {len(items)}건:")
        for item in items:
            print(f"  - [{item.get('source')}] {item.get('title')} ({item.get('url')})")
        return

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = MAIL_SUBJECT
        msg["From"] = GMAIL_USER
        msg["To"] = MAIL_TO
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            smtp.sendmail(GMAIL_USER, MAIL_TO, msg.as_string())

        print(f"✅ Gmail 발송 완료 → {MAIL_TO} ({len(items)}건)")

        for item in items:
            save_sent_id(item.get("url", ""))
        append_to_html_log(items)

    except Exception as e:
        print(f"❌ Gmail 발송 실패: {e}")