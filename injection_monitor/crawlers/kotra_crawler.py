from bs4 import BeautifulSoup
from .base_crawler import BaseCrawler

BASE_URL = "https://dream.kotra.or.kr"
LIST_URL = (
    f"{BASE_URL}/kotranews/cms/news/actionKotraBoardList.do"
    "?SITE_NO=3&MENU_ID=180&CONTENTS_NO=1&bbsGbn=244&bbsSn=244"
)
SOURCE = "KOTRA"

# 북미 3개국 관련 필터 키워드
REGION_KEYWORDS = {
    "미국", "캐나다", "멕시코",
    "usa", "u.s.", "united states",
    "canada", "mexico",
    "북미", "north america",
}


class KotraCrawler(BaseCrawler):
    def parse(self):
        resp = self.fetch_page(LIST_URL)
        if not resp:
            return []

        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "html.parser")
        items = []

        # KOTRA dream 포털: 게시판 목록 행
        rows = soup.select("table tbody tr, .board-list li, ul.news-list li")
        if not rows:
            rows = soup.select("tr")

        for row in rows:
            title_tag = row.select_one("a, .title a, td a")
            if not title_tag:
                continue

            title = title_tag.get_text(strip=True)
            if not title:
                continue

            if not self._is_north_america(title):
                continue

            href = title_tag.get("href", "")
            url = href if href.startswith("http") else BASE_URL + href

            date_tag = row.select_one("td.date, .date, time, td:last-child")
            date = date_tag.get_text(strip=True) if date_tag else ""

            # KOTRA 목록에는 요약이 없으므로 빈 문자열
            items.append({
                "title": title,
                "url": url,
                "date": date,
                "summary": "",
                "source": SOURCE,
            })

        return items

    def _is_north_america(self, text):
        text_lower = text.lower()
        return any(kw in text_lower for kw in REGION_KEYWORDS)
