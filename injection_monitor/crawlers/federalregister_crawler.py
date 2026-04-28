from .base_crawler import BaseCrawler

API_URL = (
    "https://www.federalregister.gov/api/v1/articles.json"
    "?conditions[term]=injection+molding+tariff"
    "&per_page=20"
    "&order=newest"
)
SOURCE = "Federal Register"


class FederalRegisterCrawler(BaseCrawler):
    def parse(self):
        resp = self.fetch_page(API_URL)
        if not resp:
            return []

        try:
            data = resp.json()
        except ValueError:
            print("[ERROR] FederalRegisterCrawler: JSON 파싱 실패")
            return []

        items = []
        for entry in data.get("results", []):
            title = entry.get("title", "")
            url = entry.get("html_url", "") or entry.get("pdf_url", "")
            date = entry.get("publication_date", "")
            summary = entry.get("abstract", "") or entry.get("excerpt", "")

            if not title or not url:
                continue

            items.append({
                "title": title,
                "url": url,
                "date": date,
                "summary": summary[:300] if summary else "",
                "source": SOURCE,
            })

        return items
