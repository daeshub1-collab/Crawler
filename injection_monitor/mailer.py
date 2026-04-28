"""
Outlook(pywin32)으로 카테고리별 HTML 메일을 발송한다.
.env에서 MAIL_TO, MAIL_SUBJECT를 읽는다.
"""

import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

MAIL_TO      = os.getenv("MAIL_TO", "")
MAIL_SUBJECT = os.getenv("MAIL_SUBJECT", "[사출기 모니터링] 주간 공고 알림")

# 카테고리 순서 및 표시 설정
_CATEGORIES = [
    ("관세/무역", "🔴", "#c0392b", "#fdecea"),
    ("시장동향",  "🟡", "#d68910", "#fef9e7"),
    ("경쟁사",   "🟠", "#ca6f1e", "#fdf2e9"),
    ("일반",     "🔵", "#1a5276", "#eaf2ff"),
]


def send_mail(items: list) -> bool:
    """
    필터링된 공고 목록을 Outlook으로 발송한다.

    Args:
        items: filter_items()가 반환한 dict 리스트 (category 필드 포함)

    Returns:
        True: 발송 성공, False: 발송 안 함 또는 실패
    """
    if not items:
        print("[MAILER] 발송할 공고 없음 — 메일 발송 건너뜀")
        return False

    if not MAIL_TO:
        print("[MAILER][ERROR] .env에 MAIL_TO가 설정되지 않았습니다")
        return False

    try:
        import win32com.client
    except ImportError:
        print("[MAILER][ERROR] pywin32 미설치 — pip install pywin32")
        return False

    subject = f"{MAIL_SUBJECT} ({datetime.now().strftime('%Y-%m-%d')})"
    body    = _build_html(items)

    try:
        outlook = win32com.client.Dispatch("Outlook.Application")
        mail = outlook.CreateItem(0)   # 0 = olMailItem
        mail.To       = MAIL_TO
        mail.Subject  = subject
        mail.HTMLBody = body
        mail.Send()
        print(f"[MAILER] 발송 완료 → {MAIL_TO}  ({len(items)}건)")
        return True
    except Exception as e:
        print(f"[MAILER][ERROR] 발송 실패: {e}")
        return False


# ── HTML 빌더 ─────────────────────────────────────────────────────────────────

def _build_html(items: list) -> str:
    today = datetime.now().strftime("%Y년 %m월 %d일")

    by_cat: dict[str, list] = {name: [] for name, *_ in _CATEGORIES}
    for item in items:
        cat = item.get("category", "일반")
        by_cat.setdefault(cat, []).append(item)

    sections = "".join(
        _section_html(name, emoji, color, bg, by_cat.get(name, []))
        for name, emoji, color, bg in _CATEGORIES
        if by_cat.get(name)
    )

    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"></head>
<body style="margin:0;padding:20px;background:#f0f2f5;font-family:Arial,'Malgun Gothic',sans-serif;">
<div style="max-width:700px;margin:0 auto;">

  <!-- 헤더 -->
  <div style="background:#1a73e8;color:#fff;padding:22px 28px;border-radius:10px 10px 0 0;">
    <h2 style="margin:0;font-size:1.15rem;letter-spacing:-.3px;">
      사출기(IMM) 북미 시장 모니터링 리포트
    </h2>
    <p style="margin:6px 0 0;font-size:0.82rem;opacity:.85;">
      {today} &nbsp;|&nbsp; 총 {len(items)}건
    </p>
  </div>

  <!-- 본문 -->
  <div style="background:#fff;padding:24px 28px;border-radius:0 0 10px 10px;
              box-shadow:0 2px 8px rgba(0,0,0,.09);">
    {sections}
    <p style="margin-top:28px;padding-top:14px;border-top:1px solid #eee;
              font-size:0.73rem;color:#bbb;">
      본 메일은 자동 발송입니다.
    </p>
  </div>

</div>
</body></html>"""


def _section_html(name: str, emoji: str, color: str, bg: str, items: list) -> str:
    cards = "".join(_card_html(item, color, bg) for item in items)
    return f"""
<div style="margin-bottom:28px;">
  <h3 style="margin:0 0 12px;padding-left:10px;
             border-left:4px solid {color};color:{color};font-size:1rem;">
    {emoji} {name} &nbsp;<span style="font-weight:normal;font-size:0.85rem;">({len(items)}건)</span>
  </h3>
  {cards}
</div>"""


def _card_html(item: dict, color: str, bg: str) -> str:
    title   = _esc(item.get("title",   ""))
    url     = item.get("url",    "#")
    source  = _esc(item.get("source",  ""))
    date    = _esc(item.get("date",    ""))
    summary = _esc(item.get("summary", ""))

    summary_block = (
        f'<p style="margin:8px 0 0;font-size:0.82rem;color:#444;line-height:1.5;">'
        f"{summary}</p>"
        if summary else ""
    )

    return f"""
<div style="margin-bottom:10px;padding:12px 16px;border-radius:7px;
            background:{bg};border:1px solid {color}2a;">
  <a href="{url}" style="font-size:0.93rem;font-weight:bold;color:{color};
                          text-decoration:none;line-height:1.4;">{title}</a>
  <p style="margin:5px 0 0;font-size:0.76rem;color:#777;">
    {source}&nbsp;&nbsp;|&nbsp;&nbsp;{date}
  </p>
  {summary_block}
</div>"""


def _esc(text: str) -> str:
    return (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
    )
