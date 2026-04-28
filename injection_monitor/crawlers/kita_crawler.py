from bs4 import BeautifulSoup
from crawlers.base_crawler import BaseCrawler
from filter import is_relevant


class KitaCrawler(BaseCrawler):
    """KITA 한국무역협회 크롤러"""

    name = "kita"
    URL = "https://www.kita.net/cmmrcInfo/internationalTradeStudies/researchReport/list.do"

    def crawl(self) -> list:
        print(f"🔍 {self.name} 크롤링 시작...")
        html = self.fetch_page(self.URL)
        if not html:
            return []

        soup = BeautifulSoup(html, "html.parser")
        results = []

        for a in soup.select("a[href]"):
            title = a.get_text(strip=True)
            url = a["href"]

            if not title or len(title) < 10:
                continue
            if not url.startswith("http"):
                url = "https://www.kita.net" + url

            if is_relevant(title):
                results.append({
                    "title": title,
                    "url": url,
                    "source": "KITA",
                    "date": "",
                })

        print(f"  ✅ {self.name}: {len(results)}건 수집")
        return results