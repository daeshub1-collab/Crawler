import time
import requests
import urllib3
from abc import ABC, abstractmethod

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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
        """
        GET 요청 후 Response 반환. 실패 시 최대 2회 재시도.

        - verify=False: 회사 방화벽이 SSL을 가로채는 환경(EE certificate key too weak 등) 대응
        - HTTP 403 + x-deny-reason: host_not_allowed → 즉시 None 반환
          (미국 .gov 사이트 WAF 차단. 로컬 PC에서 실행하면 정상 동작.)
        """
        for attempt in range(3):
            try:
                resp = requests.get(
                    url, headers=HEADERS, timeout=timeout,
                    verify=False,
                    **kwargs,
                )

                if resp.status_code == 403:
                    deny = resp.headers.get("x-deny-reason", "")
                    if deny == "host_not_allowed":
                        print(
                            f"[WARN] {self.__class__.__name__}: "
                            f"이 환경의 IP가 {url} WAF 허용 목록에 없습니다. "
                            f"로컬 PC에서 실행하면 정상 동작합니다."
                        )
                        return None

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
        Returns:
            list[dict]: title, url, date, summary, source 키를 포함한 딕셔너리 리스트
        """
        pass
