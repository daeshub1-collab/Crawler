import os
from datetime import datetime
from config import SENT_IDS_FILE, SENT_LOG_FILE


def load_sent_ids() -> set:
    """이미 발송된 공고 URL 목록 불러오기"""
    if not os.path.exists(SENT_IDS_FILE):
        return set()
    with open(SENT_IDS_FILE, encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())


def save_sent_id(url: str):
    """발송된 공고 URL 저장"""
    with open(SENT_IDS_FILE, "a", encoding="utf-8") as f:
        f.write(url + "\n")


def append_to_html_log(items: list):
    """
    발송된 공고를 HTML 파일에 누적 기록
    items: [{"title": ..., "url": ..., "source": ..., "date": ...}, ...]
    """
    if not items:
        return

    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    rows = ""
    for item in items:
        rows += f"""
        <tr>
            <td>{item.get('date', '')}</td>
            <td>{item.get('source', '')}</td>
            <td><a href="{item.get('url', '')}" target="_blank">{item.get('title', '')}</a></td>
        </tr>"""

    block = f"""
<h3>📅 {now} 발송분</h3>
<table border="1" cellpadding="5" cellspacing="0">
    <tr><th>날짜</th><th>출처</th><th>제목</th></tr>
    {rows}
</table>
<hr>
"""

    with open(SENT_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(block)