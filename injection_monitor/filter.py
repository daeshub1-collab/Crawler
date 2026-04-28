from config import KEYWORDS_FILE

def load_keywords():
    """keywords.txt 파일을 읽어서 카테고리별로 반환"""
    keywords = {
        "REQUIRED": [],
        "TARIFF": [],
        "MARKET": [],
        "EXCLUDE": []
    }
    current = None

    with open(KEYWORDS_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith("[") and line.endswith("]"):
                current = line[1:-1]
            elif current and line:
                keywords[current].append(line.lower())

    return keywords


def is_relevant(title: str, summary: str = "") -> bool:
    """
    공고가 관련 있는지 판단
    - REQUIRED 키워드 중 하나라도 포함 → 통과
    - EXCLUDE 키워드 있으면 → 무조건 제외
    """
    keywords = load_keywords()
    text = (title + " " + summary).lower()

    # 제외 키워드 체크
    for kw in keywords["EXCLUDE"]:
        if kw in text:
            return False

    # 필수 키워드 체크
    for kw in keywords["REQUIRED"]:
        if kw in text:
            return True

    return False