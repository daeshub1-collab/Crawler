from bs4 import BeautifulSoup
from .base_crawler import BaseCrawler

BASE_URL = "https://www.kita.net"
LIST_URL = f"{BASE_URL}/board/totalTradeNews/totalTradeNewsList.do"
SOURCE = "KITA (한국무역협회)"

# 수집 대상 키워드 (제목에 하나라도 포함 시 수집)
FILTER_KEYWORDS = {
    "미국", "멕시코", "캐나다",
    "관세", "tariff", "customs duty",
    "usa", "u.s.", "united states",
    "mexico", "canada",
    "usmca", "section 301", "section 232",
    "무역", "수출", "수입",
}


class KitaCrawler(BaseCrawler):
    def parse(self):
        resp = self.fetch_page(LIST_URL)
        if not resp:
            return []

        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "html.parser")
        items = []

        # KITA 게시판 목록: table tbody tr 또는 ul.board-list li
        rows = soup.select("table.board-list tbody tr, .board_list tbody tr, ul.list li")
        if not rows:
            rows = soup.select("table tbody tr")

        for row in rows:
            title_tag = row.select_one("a, td.subject a, .title a, td a")
            if not title_tag:
                continue

            title = title_tag.get_text(strip=True)
            if not title:
                continue

            if not self._is_relevant(title):
                continue

            href = title_tag.get("href", "")
            if not href:
                continue
            url = href if href.startswith("http") else BASE_URL + href

            date_tag = row.select_one("td.date, .date, td:last-child, time")
            date = date_tag.get_text(strip=True) if date_tag else ""

            items.append({
                "title": title,
                "url": url,
                "date": date,
                "summary": "",
                "source": SOURCE,
            })

        return items

    def _is_relevant(self, text):
        text_lower = text.lower()
        return any(kw in text_lower for kw in FILTER_KEYWORDS)
