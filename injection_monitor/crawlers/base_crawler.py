import requests
import urllib3
from config import FETCH_TIMEOUT, FETCH_RETRY

# 회사 방화벽 SSL 경고 억제
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class BaseCrawler:
    """모든 크롤러의 공통 기반 클래스"""

    name = "base"  # 각 크롤러에서 override

    def fetch_page(self, url: str) -> str | None:
        """
        URL에서 HTML 텍스트 가져오기
        - SSL 검증 비활성화 (회사 방화벽 대응)
        - 실패 시 FETCH_RETRY 횟수만큼 재시도
        """
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }

        for attempt in range(1, FETCH_RETRY + 2):
            try:
                response = requests.get(
                    url,
                    headers=headers,
                    timeout=FETCH_TIMEOUT,
                    verify=False,  # SSL 검증 비활성화
                )
                response.raise_for_status()
                return response.text

            except Exception as e:
                if attempt <= FETCH_RETRY:
                    print(f"  ⚠ {self.name} 재시도 {attempt}/{FETCH_RETRY}: {e}")
                else:
                    print(f"  ❌ {self.name} 페이지 로드 실패: {e}")
                    return None

    def fetch_feed(self, url: str):
        """
        RSS 피드 가져오기 (SSL 검증 비활성화)
        """
        import feedparser
        import ssl

        try:
            # SSL 검증 없이 feedparser 요청
            response = requests.get(
                url,
                verify=False,
                timeout=FETCH_TIMEOUT,
                headers={"User-Agent": "Mozilla/5.0"}
            )
            feed = feedparser.parse(response.text)
            return feed
        except Exception as e:
            print(f"  ❌ {self.name} 피드 로드 실패: {e}")
            return None

    def crawl(self) -> list:
        """
        각 크롤러에서 반드시 구현해야 하는 메서드
        반환값: [{"title": ..., "url": ..., "source": ..., "date": ...}, ...]
        """
        raise NotImplementedError