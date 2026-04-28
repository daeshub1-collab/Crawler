import ssl
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

# SSL 검증 오류를 무시하는 컨텍스트 (프록시 환경 대응)
_SSL_CTX = ssl.create_default_context()
_SSL_CTX.check_hostname = False
_SSL_CTX.verify_mode = ssl.CERT_NONE


class BaseCrawler(ABC):
    def fetch_page(self, url, timeout=15, **kwargs):
        """
        GET 요청 후 Response 반환. 실패 시 최대 2회 재시도.

        - SSL 자체서명 인증서 오류 → verify=False 로 재시도
        - HTTP 403 + x-deny-reason: host_not_allowed → 즉시 None 반환
          (이 서버 IP가 대상 사이트의 WAF 허용 목록에 없음. 로컬 PC에서 실행하면 정상 동작.)
        """
        for attempt in range(3):
            try:
                resp = requests.get(
                    url, headers=HEADERS, timeout=timeout,
                    verify=False,   # 프록시/방화벽 자체서명 인증서 대응
                    **kwargs,
                )

                # WAF host_not_allowed: 재시도해도 소용없으므로 즉시 종료
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

            except requests.exceptions.SSLError:
                # SSL 오류는 verify=False 이미 적용 중이므로 다음 재시도로 넘김
                if attempt < 2:
                    time.sleep(2 ** attempt)
                else:
                    print(f"[ERROR] {self.__class__.__name__} SSL 오류 ({url})")
                    return None

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
