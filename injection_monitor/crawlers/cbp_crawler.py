from bs4 import BeautifulSoup
from .base_crawler import BaseCrawler

BASE_URL = "https://www.cbp.gov"
LIST_URL = f"{BASE_URL}/newsroom/national-media-release"
SOURCE = "CBP (미국세관)"


class CbpCrawler(BaseCrawler):
    def parse(self):
        resp = self.fetch_page(LIST_URL)
        if not resp:
            return []

        soup = BeautifulSoup(resp.text, "html.parser")
        items = []

        # CBP 뉴스룸: .view-content 안의 각 .views-row
        rows = soup.select(".view-content .views-row")
        if not rows:
            # fallback: article 태그
            rows = soup.select("article")

        for row in rows:
            title_tag = row.select_one("h3 a, h2 a, .views-field-title a, .field-title a")
            if not title_tag:
                continue

            title = title_tag.get_text(strip=True)
            href = title_tag.get("href", "")
            url = href if href.startswith("http") else BASE_URL + href

            date_tag = row.select_one(
                ".views-field-created, .date-display-single, time, .field-date"
            )
            date = date_tag.get_text(strip=True) if date_tag else ""

            summary_tag = row.select_one(
                ".views-field-body, .field-summary, .views-field-field-summary, p"
            )
            summary = summary_tag.get_text(strip=True) if summary_tag else ""

            items.append({
                "title": title,
                "url": url,
                "date": date,
                "summary": summary,
                "source": SOURCE,
            })

        return items
