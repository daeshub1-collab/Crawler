import time
import requests
from abc import ABC, abstractmethod

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


class BaseCrawler(ABC):
    def fetch_page(self, url, timeout=15, **kwargs):
        """GET 요청 후 Response 반환. 실패 시 최대 2회 재시도."""
        for attempt in range(3):
            try:
                resp = requests.get(url, headers=HEADERS, timeout=timeout, **kwargs)
                resp.raise_for_status()
                return resp
            except requests.RequestException as e:
                if attempt < 2:
                    time.sleep(2 ** attempt)
                else:
                    print(f"[ERROR] {self.__class__.__name__} fetch 실패 ({url}): {e}")
                    return None

    @abstractmethod
    def parse(self):
        """
        크롤링 결과를 반환한다.

        Returns:
            list[dict]: 각 항목은 아래 키를 포함
                - title   (str): 기사 제목
                - url     (str): 원문 링크
                - date    (str): 날짜 (YYYY-MM-DD 또는 원문 형식)
                - summary (str): 요약 / 리드 문장
                - source  (str): 사이트명
        """
        pass
