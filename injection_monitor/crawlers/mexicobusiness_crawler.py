from crawlers.base_crawler import BaseCrawler
from filter import is_relevant


class MexicoBusinessCrawler(BaseCrawler):
    """Mexico Business News RSS 크롤러"""

    name = "mexicobusiness"
    FEED_URL = "https://mexicobusiness.news/rss.xml"

    def crawl(self) -> list:
        print(f"🔍 {self.name} 크롤링 시작...")
        feed = self.fetch_feed(self.FEED_URL)
        if not feed:
            return []

        results = []
        for entry in feed.entries:
            title = entry.get("title", "")
            url = entry.get("link", "")
            date = entry.get("published", "")
            summary = entry.get("summary", "")

            if is_relevant(title, summary):
                results.append({
                    "title": title,
                    "url": url,
                    "source": "Mexico Business News",
                    "date": date,
                })

        print(f"  ✅ {self.name}: {len(results)}건 수집")
        return results