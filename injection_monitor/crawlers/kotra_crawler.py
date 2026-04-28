import requests
from bs4 import BeautifulSoup
from crawlers.base_crawler import BaseCrawler
from filter import is_relevant


class KotraCrawler(BaseCrawler):
    """KOTRA 해외시장뉴스 크롤러"""

    name = "kotra"
    URL = "https://dream.kotra.or.kr/kotranews/cms/news/actionKotraBoardList.do?SITE_NO=3&MENU_ID=180&CONTENTS_NO=1&bbsGbn=243&bbsSn=243"

    def crawl(self) -> list:
        print(f"🔍 {self.name} 크롤링 시작...")
        try:
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                "Referer": "https://dream.kotra.or.kr",
            }
            response = requests.get(
                self.URL,
                headers=headers,
                verify=False,
                timeout=15,
            )
            html = response.text
        except Exception as e:
            print(f"  ❌ {self.name} 실패: {e}")
            return []

        soup = BeautifulSoup(html, "html.parser")
        results = []

        for a in soup.select("a[href]"):
            title = a.get_text(strip=True)
            url = a["href"]

            if not title or len(title) < 10:
                continue
            if not url.startswith("http"):
                url = "https://dream.kotra.or.kr" + url

            if is_relevant(title):
                results.append({
                    "title": title,
                    "url": url,
                    "source": "KOTRA",
                    "date": "",
                })

        print(f"  ✅ {self.name}: {len(results)}건 수집")
        return results