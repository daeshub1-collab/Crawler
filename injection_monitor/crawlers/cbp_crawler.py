from bs4 import BeautifulSoup
from crawlers.base_crawler import BaseCrawler
from filter import is_relevant


class CbpCrawler(BaseCrawler):
    """미국 세관 (cbp.gov) 크롤러"""

    name = "cbp"
    URL = "https://www.cbp.gov/trade/rulings"

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
                url = "https://www.cbp.gov" + url

            if is_relevant(title):
                results.append({
                    "title": title,
                    "url": url,
                    "source": "CBP",
                    "date": "",
                })

        print(f"  ✅ {self.name}: {len(results)}건 수집")
        return results