import feedparser
from bs4 import BeautifulSoup
from .base_crawler import BaseCrawler

RSS_URL = "https://www.plasticsnews.com/arc/outboundfeeds/rss/"
SOURCE = "Plastics News"


class PlasticsNewsCrawler(BaseCrawler):
    def parse(self):
        # fetch_page()로 요청 → verify=False 적용, feedparser에 본문 직접 전달
        resp = self.fetch_page(RSS_URL)
        if not resp:
            return []

        feed = feedparser.parse(resp.content)
        items = []

        for entry in feed.entries:
            title = entry.get("title", "")
            url   = entry.get("link", "")
            if not title or not url:
                continue

            date      = entry.get("published", "")
            raw_sum   = entry.get("summary", "") or entry.get("description", "")
            summary   = BeautifulSoup(raw_sum, "html.parser").get_text(strip=True)

            items.append({
                "title":   title,
                "url":     url,
                "date":    date,
                "summary": summary[:300],
                "source":  SOURCE,
            })

        return items
