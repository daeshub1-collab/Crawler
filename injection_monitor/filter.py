"""
keywords.txt를 읽어 항목을 필터링하고 카테고리를 태그한다.

섹션별 역할:
  [REQUIRED] - 하나라도 있으면 수집 후보
  [TARIFF]   - 관세/무역 카테고리
  [MARKET]   - 시장동향 카테고리 (경쟁사명 포함)
  [EXCLUDE]  - 있으면 무조건 제외

카테고리 우선순위 (위에서부터 먼저 매칭된 것 적용):
  1. TARIFF 키워드 매칭  → "관세/무역"
  2. 경쟁사명 매칭       → "경쟁사"  (MARKET보다 먼저 확인해 경쟁사가 시장동향으로 묻히지 않게)
  3. MARKET 키워드 매칭  → "시장동향"
  4. 나머지              → "일반"
"""

from pathlib import Path

KEYWORDS_FILE = Path(__file__).parent / "keywords.txt"

# 별도 경쟁사 목록 (keywords.txt [MARKET] 섹션에 포함돼 있지만 카테고리를 따로 분류)
COMPETITOR_BRANDS = {
    "engel", "haitian", "kraussmaffei", "fanuc",
    "sumitomo", "arburg", "milacron", "husky", "nissei",
}


def _parse_keywords(filepath: Path) -> dict:
    """keywords.txt를 섹션별로 파싱해 소문자 리스트 딕셔너리로 반환한다."""
    sections: dict[str, list] = {"REQUIRED": [], "TARIFF": [], "MARKET": [], "EXCLUDE": []}
    current = None

    for line in filepath.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            current = line[1:-1]
            continue
        if current in sections:
            sections[current].append(line.lower())

    return sections


_kw = _parse_keywords(KEYWORDS_FILE)
_REQUIRED = _kw["REQUIRED"]
_TARIFF   = _kw["TARIFF"]
_MARKET   = _kw["MARKET"]
_EXCLUDE  = _kw["EXCLUDE"]


def _hit(text: str, keywords: list) -> bool:
    return any(kw in text for kw in keywords)


def _assign_category(text: str) -> str:
    if _hit(text, _TARIFF):
        return "관세/무역"
    if any(brand in text for brand in COMPETITOR_BRANDS):
        return "경쟁사"
    if _hit(text, _MARKET):
        return "시장동향"
    return "일반"


def filter_items(items: list) -> list:
    """
    크롤러가 수집한 항목을 키워드 기준으로 필터링하고 카테고리를 추가한다.

    Args:
        items: list[dict] — title, url, date, summary, source 포함

    Returns:
        list[dict] — 필터 통과한 항목에 'category' 키가 추가된 새 리스트
    """
    result = []
    for item in items:
        text = (item.get("title", "") + " " + item.get("summary", "")).lower()

        if _hit(text, _EXCLUDE):
            continue

        if not (_hit(text, _REQUIRED) or _hit(text, _TARIFF) or _hit(text, _MARKET)):
            continue

        new_item = dict(item)
        new_item["category"] = _assign_category(text)
        result.append(new_item)

    return result
