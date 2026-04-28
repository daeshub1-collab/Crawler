import feedparser
from bs4 import BeautifulSoup
from .base_crawler import BaseCrawler

RSS_URL = "https://www.plasticsnews.com/arc/outboundfeeds/rss/"
SOURCE = "Plastics News"


class PlasticsNewsCrawler(BaseCrawler):
    def parse(self):
        feed = feedparser.parse(RSS_URL)
        items = []

        for entry in feed.entries:
            title = entry.get("title", "")
            url = entry.get("link", "")
            if not title or not url:
                continue

            date = entry.get("published", "")
            raw_summary = entry.get("summary", "") or entry.get("description", "")
            summary = BeautifulSoup(raw_summary, "html.parser").get_text(strip=True)

            items.append({
                "title": title,
                "url": url,
                "date": date,
                "summary": summary[:300],
                "source": SOURCE,
            })

        return items

    def fetch_page(self, url, timeout=15, **kwargs):
        pass  # feedparser가 직접 HTTP 요청을 처리함
