import json
import ssl
import time
import http.client
from urllib.parse import urlencode
from .base_crawler import BaseCrawler

_HOST   = "www.federalregister.gov"
_PATH   = "/api/v1/articles.json"
_PARAMS = {
    "conditions[term]": "injection molding tariff",
    "per_page": 20,
    "order": "newest",
}
SOURCE = "Federal Register"

_HEADERS = {
    "User-Agent": "injection-monitor/1.0 (research bot)",
    "Accept":     "application/json",
}

# urlencode가 [ ]를 %5B%5D로 인코딩하므로 원래 형태로 되돌린다
def _build_path() -> str:
    qs = urlencode(_PARAMS).replace("%5B", "[").replace("%5D", "]")
    return f"{_PATH}?{qs}"


class FederalRegisterCrawler(BaseCrawler):
    def parse(self):
        data = self._fetch_json()
        if data is None:
            return []

        items = []
        for entry in data.get("results", []):
            title   = entry.get("title", "")
            url     = entry.get("html_url", "") or entry.get("pdf_url", "")
            date    = entry.get("publication_date", "")
            summary = entry.get("abstract", "") or entry.get("excerpt", "")

            if not title or not url:
                continue

            items.append({
                "title":   title,
                "url":     url,
                "date":    date,
                "summary": summary[:300] if summary else "",
                "source":  SOURCE,
            })

        return items

    def _fetch_json(self) -> dict | None:
        """
        http.client를 직접 사용해 URL 브라켓 인코딩을 방지하고
        SSL 인증서 오류를 우회한다 (자체 서명 인증서 환경 대응).
        """
        path = _build_path()
        ctx  = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode    = ssl.CERT_NONE

        for attempt in range(3):
            try:
                conn = http.client.HTTPSConnection(_HOST, timeout=15, context=ctx)
                conn.request("GET", path, headers=_HEADERS)
                resp = conn.getresponse()

                if resp.status == 403:
                    deny = resp.getheader("x-deny-reason", "")
                    if deny == "host_not_allowed":
                        print("[WARN] FederalRegisterCrawler: 이 실행 환경의 IP가 API 허용 목록에 없습니다. "
                              "로컬 PC에서 실행하면 정상 동작합니다.")
                    else:
                        print(f"[ERROR] FederalRegisterCrawler: HTTP 403 Forbidden")
                    return None   # 403은 재시도해도 소용없음
                if resp.status != 200:
                    raise ConnectionError(f"HTTP {resp.status} {resp.reason}")

                body = resp.read().decode("utf-8")
                conn.close()
                return json.loads(body)

            except Exception as e:
                conn.close() if 'conn' in dir() else None
                if attempt < 2:
                    time.sleep(2 ** attempt)
                else:
                    print(f"[ERROR] FederalRegisterCrawler fetch 실패: {e}")
                    return None
