from bs4 import BeautifulSoup
from .base_crawler import BaseCrawler

BASE_URL = "https://www.canplastics.com"
LIST_URL = f"{BASE_URL}/news/"
SOURCE = "Canadian Plastics"


class CanPlasticsCrawler(BaseCrawler):
    def parse(self):
        resp = self.fetch_page(LIST_URL)
        if not resp:
            return []

        soup = BeautifulSoup(resp.text, "html.parser")
        items = []

        # canplastics.com: 기사 목록은 article 또는 .td-module-container 등으로 구성
        articles = soup.select("article, .td-module-container, .jeg_post, .post-item")
        if not articles:
            # fallback: h2/h3 + a 조합으로 탐색
            articles = soup.select(".news-list li, .entry-list li, .items li")

        for article in articles:
            title_tag = article.select_one(
                "h2 a, h3 a, .entry-title a, .td-module-title a, .jeg_post_title a"
            )
            if not title_tag:
                continue

            title = title_tag.get_text(strip=True)
            href = title_tag.get("href", "")
            url = href if href.startswith("http") else BASE_URL + href

            date_tag = article.select_one(
                "time, .entry-date, .td-post-date, .jeg_meta_date, .post-date"
            )
            date = ""
            if date_tag:
                date = date_tag.get("datetime", "") or date_tag.get_text(strip=True)

            summary_tag = article.select_one(
                ".entry-summary, .td-excerpt, .jeg_post_excerpt, p"
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
