"""
실행 환경 설정

민감 정보(수신 이메일, 제목)는 .env 파일에 저장한다.
.env 파일이 없으면 아래 DEFAULT 값이 사용된다.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

# ── 이메일 ────────────────────────────────────────────────────────────────────
MAIL_TO      = os.getenv("MAIL_TO", "")
MAIL_SUBJECT = os.getenv("MAIL_SUBJECT", "[사출기 모니터링] 주간 공고 알림")

# ── 스케줄 ────────────────────────────────────────────────────────────────────
SCHEDULE_DAY  = os.getenv("SCHEDULE_DAY", "monday")   # monday ~ sunday
SCHEDULE_TIME = os.getenv("SCHEDULE_TIME", "09:00")   # HH:MM

# ── 크롤링 동작 ───────────────────────────────────────────────────────────────
FETCH_TIMEOUT   = int(os.getenv("FETCH_TIMEOUT", "15"))    # requests 타임아웃(초)
FETCH_RETRY     = int(os.getenv("FETCH_RETRY", "2"))       # 재시도 횟수
SELENIUM_WAIT   = int(os.getenv("SELENIUM_WAIT", "20"))    # Selenium 최대 대기(초)
