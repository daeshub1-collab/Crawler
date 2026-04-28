import feedparser
from bs4 import BeautifulSoup
from .base_crawler import BaseCrawler

RSS_URL = "https://mexicobusiness.news/feed"
SOURCE = "Mexico Business News"

FILTER_KEYWORDS = {"plastic", "manufacturing", "injection"}


class MexicoBusinessCrawler(BaseCrawler):
    def parse(self):
        # fetch_page()로 요청 → verify=False 적용, feedparser에 본문 직접 전달
        resp = self.fetch_page(RSS_URL)
        if not resp:
            return []

        feed = feedparser.parse(resp.content)
        items = []

        for entry in feed.entries:
            title   = entry.get("title", "")
            summary = entry.get("summary", "")
            text    = (title + " " + summary).lower()

            if not any(kw in text for kw in FILTER_KEYWORDS):
                continue

            url           = entry.get("link", "")
            date          = entry.get("published", "")
            clean_summary = BeautifulSoup(summary, "html.parser").get_text(strip=True)

            items.append({
                "title":   title,
                "url":     url,
                "date":    date,
                "summary": clean_summary[:300],
                "source":  SOURCE,
            })

        return items
