import requests
from crawlers.base_crawler import BaseCrawler
from filter import is_relevant


class FederalRegisterCrawler(BaseCrawler):
    """미국 연방관보 API 크롤러"""

    name = "federalregister"
    API_URL = (
        "https://www.federalregister.gov/api/v1/articles.json"
        "?conditions[term]=injection+molding+tariff"
        "&per_page=20&order=newest"
    )

    def crawl(self) -> list:
        print(f"🔍 {self.name} 크롤링 시작...")
        try:
            response = requests.get(
                self.API_URL,
                verify=False,
                timeout=15,
                headers={"User-Agent": "Mozilla/5.0"}
            )
            data = response.json()
        except Exception as e:
            print(f"  ❌ {self.name} 실패: {e}")
            return []

        results = []
        for article in data.get("results", []):
            title = article.get("title", "")
            url = article.get("html_url", "")
            date = article.get("publication_date", "")

            if is_relevant(title):
                results.append({
                    "title": title,
                    "url": url,
                    "source": "Federal Register",
                    "date": date,
                })

        print(f"  ✅ {self.name}: {len(results)}건 수집")
        return results