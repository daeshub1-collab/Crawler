"""
발송 이력 관리 모듈

- sent_ids.txt : 발송된 항목 ID(URL MD5) 목록 — 중복 발송 방지
- sent_log.html : 발송 이력 HTML 뷰어
    - 카테고리 필터 버튼 (전체 / 관세·무역 / 시장동향 / 경쟁사 / 일반)
    - 키워드 검색창
    - 공고 카드: 제목(링크), 출처, 날짜, 카테고리 배지
"""

import hashlib
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent
SENT_IDS_FILE = BASE_DIR / "sent_ids.txt"
SENT_LOG_HTML = BASE_DIR / "sent_log.html"

# 카테고리 표시 설정 (이름, 색상, 배경)
_CATEGORIES = [
    ("관세/무역", "#c0392b", "#fdecea"),
    ("시장동향",  "#d68910", "#fef9e7"),
    ("경쟁사",   "#ca6f1e", "#fdf2e9"),
    ("일반",     "#1a5276", "#eaf2ff"),
]
_CAT_STYLE = {name: (fg, bg) for name, fg, bg in _CATEGORIES}


# ── ID 유틸 ────────────────────────────────────────────────────────────────────

def make_id(item: dict) -> str:
    """항목 URL의 MD5 앞 12자리를 ID로 사용한다."""
    return hashlib.md5(item["url"].encode("utf-8")).hexdigest()[:12]


# ── sent_ids.txt ───────────────────────────────────────────────────────────────

def load_sent_ids() -> set:
    """이미 발송된 ID 집합을 반환한다."""
    if not SENT_IDS_FILE.exists():
        return set()
    return set(SENT_IDS_FILE.read_text(encoding="utf-8").splitlines())


def save_sent_id(item_id: str) -> None:
    """ID를 sent_ids.txt에 추가한다."""
    with open(SENT_IDS_FILE, "a", encoding="utf-8") as f:
        f.write(item_id + "\n")


# ── sent_log.html ──────────────────────────────────────────────────────────────

def update_html_log(new_items: list) -> None:
    """
    새로 발송된 항목들을 sent_log.html 맨 위에 추가한다.
    기존 행은 보존된다.
    """
    existing_rows_html = _load_existing_rows()
    new_rows_html = _build_rows(new_items)
    all_rows = new_rows_html + existing_rows_html
    SENT_LOG_HTML.write_text(_build_page(all_rows), encoding="utf-8")


def _load_existing_rows() -> str:
    """현재 HTML 파일에서 기존 <tr> 블록을 추출한다."""
    if not SENT_LOG_HTML.exists():
        return ""
    content = SENT_LOG_HTML.read_text(encoding="utf-8")
    start, end = "<!-- ROWS_START -->", "<!-- ROWS_END -->"
    if start in content and end in content:
        return content[content.index(start) + len(start): content.index(end)]
    return ""


def _build_rows(items: list) -> str:
    rows = []
    for item in items:
        category = _esc(item.get("category", "일반"))
        source   = _esc(item.get("source", ""))
        title    = _esc(item.get("title", ""))
        url      = _esc(item.get("url", ""))
        date     = _esc(item.get("date", ""))
        summary  = _esc(item.get("summary", "")[:200])

        fg, bg = _CAT_STYLE.get(item.get("category", "일반"), ("#333", "#f5f5f5"))
        badge = (
            f'<span style="display:inline-block;padding:2px 8px;border-radius:12px;'
            f'font-size:0.73rem;background:{bg};color:{fg};white-space:nowrap;">'
            f"{category}</span>"
        )

        rows.append(
            f'<tr data-category="{category}" data-source="{source}">'
            f'<td class="col-date">{date}</td>'
            f'<td class="col-cat">{badge}</td>'
            f'<td class="col-source">{source}</td>'
            f'<td class="col-title"><a href="{url}" target="_blank" rel="noopener">{title}</a></td>'
            f'<td class="col-summary">{summary}</td>'
            f"</tr>"
        )
    return "\n".join(rows)


def _esc(text: str) -> str:
    return (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
    )


def _build_page(rows_html: str) -> str:
    updated = datetime.now().strftime("%Y-%m-%d %H:%M")
    cat_buttons = "\n    ".join(
        f'<button data-filter="{name}">{name}</button>'
        for name, *_ in _CATEGORIES
    )
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>발송 이력 로그</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f4f6f9; color: #333; padding: 24px; }}
  h1 {{ font-size: 1.4rem; margin-bottom: 4px; }}
  .meta {{ color: #888; font-size: 0.82rem; margin-bottom: 20px; }}
  .toolbar {{ display: flex; flex-wrap: wrap; gap: 10px; align-items: center; margin-bottom: 16px; }}
  .filters {{ display: flex; flex-wrap: wrap; gap: 6px; }}
  .filters button {{
    padding: 4px 12px; border: 1px solid #ccc; border-radius: 20px;
    background: #fff; cursor: pointer; font-size: 0.82rem; transition: all .15s;
  }}
  .filters button[data-filter="all"].active  {{ background:#555;   color:#fff; border-color:#555; }}
  .filters button[data-filter="관세/무역"].active {{ background:#c0392b; color:#fff; border-color:#c0392b; }}
  .filters button[data-filter="시장동향"].active  {{ background:#d68910; color:#fff; border-color:#d68910; }}
  .filters button[data-filter="경쟁사"].active    {{ background:#ca6f1e; color:#fff; border-color:#ca6f1e; }}
  .filters button[data-filter="일반"].active      {{ background:#1a5276; color:#fff; border-color:#1a5276; }}
  .filters button:hover:not(.active) {{ background: #e8f0fe; border-color: #1a73e8; }}
  #searchBox {{
    padding: 6px 12px; border: 1px solid #ccc; border-radius: 20px;
    font-size: 0.85rem; width: 240px; outline: none;
  }}
  #searchBox:focus {{ border-color: #1a73e8; box-shadow: 0 0 0 2px #d2e3fc; }}
  #countInfo {{ font-size: 0.82rem; color: #555; margin-left: auto; }}
  .table-wrap {{ overflow-x: auto; }}
  table {{ width: 100%; border-collapse: collapse; background: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,.08); }}
  th {{ background: #34495e; color: #fff; text-align: left; padding: 10px 14px; font-size: 0.83rem; white-space: nowrap; }}
  td {{ padding: 9px 14px; font-size: 0.82rem; border-bottom: 1px solid #f0f0f0; vertical-align: top; }}
  tr:last-child td {{ border-bottom: none; }}
  tr:hover td {{ background: #f8faff; }}
  tr.hidden {{ display: none; }}
  .col-date   {{ white-space: nowrap; color: #555; width: 100px; }}
  .col-cat    {{ width: 100px; }}
  .col-source {{ width: 160px; font-size: 0.78rem; color: #666; }}
  .col-summary {{ color: #555; }}
  a {{ color: #1a73e8; text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}
</style>
</head>
<body>
<h1>발송 이력 로그</h1>
<p class="meta">최종 업데이트: {updated}</p>

<div class="toolbar">
  <div class="filters" id="filterBtns">
    <button class="active" data-filter="all">전체</button>
    {cat_buttons}
  </div>
  <input type="text" id="searchBox" placeholder="키워드 검색...">
  <span id="countInfo"></span>
</div>

<div class="table-wrap">
  <table id="logTable">
    <thead>
      <tr>
        <th>날짜</th>
        <th>카테고리</th>
        <th>출처</th>
        <th>제목</th>
        <th>요약</th>
      </tr>
    </thead>
    <tbody>
<!-- ROWS_START -->
{rows_html}
<!-- ROWS_END -->
    </tbody>
  </table>
</div>

<script>
(function () {{
  const tbody    = document.querySelector('#logTable tbody');
  const filterBtns = document.getElementById('filterBtns');
  const searchBox  = document.getElementById('searchBox');
  const countInfo  = document.getElementById('countInfo');

  let activeFilter = 'all';
  let searchTerm   = '';

  function applyFilters() {{
    const rows = [...tbody.querySelectorAll('tr')];
    let visible = 0;
    rows.forEach(row => {{
      const catMatch = activeFilter === 'all' || row.dataset.category === activeFilter;
      const kwMatch  = !searchTerm || row.textContent.toLowerCase().includes(searchTerm);
      const show     = catMatch && kwMatch;
      row.classList.toggle('hidden', !show);
      if (show) visible++;
    }});
    countInfo.textContent = visible + '건 표시 중';
  }}

  filterBtns.addEventListener('click', e => {{
    const btn = e.target.closest('button');
    if (!btn) return;
    filterBtns.querySelectorAll('button').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    activeFilter = btn.dataset.filter;
    applyFilters();
  }});

  searchBox.addEventListener('input', e => {{
    searchTerm = e.target.value.trim().toLowerCase();
    applyFilters();
  }});

  applyFilters();
}})();
</script>
</body>
</html>"""
