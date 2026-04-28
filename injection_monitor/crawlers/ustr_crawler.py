from bs4 import BeautifulSoup
from .base_crawler import BaseCrawler

BASE_URL = "https://ustr.gov"
LIST_URL = f"{BASE_URL}/press-office/press-releases"
SOURCE = "USTR (미국무역대표부)"


class USTRCrawler(BaseCrawler):
    def parse(self):
        resp = self.fetch_page(LIST_URL)
        if not resp:
            return []

        soup = BeautifulSoup(resp.text, "html.parser")
        items = []

        # USTR: Drupal 기반 .view-content .views-row 구조
        rows = soup.select(".view-content .views-row")
        if not rows:
            rows = soup.select("article, .press-release-item, .field-items .field-item")

        for row in rows:
            title_tag = row.select_one(
                "h2 a, h3 a, .field-title a, .views-field-title a, .node-title a"
            )
            if not title_tag:
                continue

            title = title_tag.get_text(strip=True)
            href = title_tag.get("href", "")
            url = href if href.startswith("http") else BASE_URL + href

            date_tag = row.select_one(
                "time, .date-display-single, .field-date, .views-field-created, .post-date"
            )
            date = ""
            if date_tag:
                date = date_tag.get("datetime", "") or date_tag.get_text(strip=True)

            summary_tag = row.select_one(
                ".views-field-body p, .field-summary p, .views-field-field-description p, p"
            )
            summary = summary_tag.get_text(strip=True) if summary_tag else ""

            items.append({
                "title": title,
                "url": url,
                "date": date,
                "summary": summary[:300],
                "source": SOURCE,
            })

        return items
