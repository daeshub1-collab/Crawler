import time
from typing import Optional
from bs4 import BeautifulSoup
from .base_crawler import BaseCrawler

BASE_URL = "https://dream.kotra.or.kr"
LIST_URL = (
    f"{BASE_URL}/kotranews/cms/news/actionKotraBoardList.do"
    "?SITE_NO=3&MENU_ID=180&CONTENTS_NO=1&bbsGbn=244&bbsSn=244"
)
SOURCE = "KOTRA"

REGION_KEYWORDS = {
    "미국", "캐나다", "멕시코",
    "usa", "u.s.", "united states",
    "canada", "mexico",
    "북미", "north america",
}


class KotraCrawler(BaseCrawler):
    def parse(self):
        html = self._get_rendered_html()
        if not html:
            return []

        soup = BeautifulSoup(html, "html.parser")
        items = []

        rows = soup.select("table tbody tr, .board-list li, ul.news-list li")
        if not rows:
            rows = soup.select("tr")

        for row in rows:
            title_tag = row.select_one("a, .title a, td a")
            if not title_tag:
                continue

            title = title_tag.get_text(strip=True)
            if not title or not self._is_north_america(title):
                continue

            href = title_tag.get("href", "")
            url = href if href.startswith("http") else BASE_URL + href

            date_tag = row.select_one("td.date, .date, time, td:last-child")
            date = date_tag.get_text(strip=True) if date_tag else ""

            items.append({
                "title": title,
                "url": url,
                "date": date,
                "summary": "",
                "source": SOURCE,
            })

        return items

    def _get_rendered_html(self) -> Optional[str]:
        """Selenium으로 JS 렌더링 후 페이지 소스 반환. 미설치 시 requests로 폴백."""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from webdriver_manager.chrome import ChromeDriverManager
        except ImportError:
            print("[WARN] KotraCrawler: selenium/webdriver-manager 미설치 — requests 폴백 사용")
            resp = super().fetch_page(LIST_URL)
            return resp.text if resp else None

        opts = Options()
        opts.add_argument("--headless")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--disable-gpu")
        opts.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        driver = None
        try:
            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=opts,
            )
            driver.get(LIST_URL)
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "table tbody tr, .board-list, ul.news-list")
                )
            )
            time.sleep(1)  # 추가 렌더링 대기
            return driver.page_source
        except Exception as e:
            print(f"[ERROR] KotraCrawler Selenium 실패: {e}")
            return None
        finally:
            if driver:
                driver.quit()

    def _is_north_america(self, text: str) -> bool:
        text_lower = text.lower()
        return any(kw in text_lower for kw in REGION_KEYWORDS)
