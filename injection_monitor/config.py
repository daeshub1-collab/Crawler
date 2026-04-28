import os
from dotenv import load_dotenv

load_dotenv()

# 이메일 설정
MAIL_TO = os.getenv("MAIL_TO", "daeseop.lee@lsmtron.com")
MAIL_SUBJECT = os.getenv("MAIL_SUBJECT", "[Injection Monitor] Weekly Report")

# 크롤링 설정
FETCH_TIMEOUT = int(os.getenv("FETCH_TIMEOUT", 15))
FETCH_RETRY = int(os.getenv("FETCH_RETRY", 2))
SELENIUM_WAIT = int(os.getenv("SELENIUM_WAIT", 20))

# 스케줄 설정
SCHEDULE_DAY = os.getenv("SCHEDULE_DAY", "monday")
SCHEDULE_TIME = os.getenv("SCHEDULE_TIME", "09:00")

# 파일 경로
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KEYWORDS_FILE = os.path.join(BASE_DIR, "keywords.txt")
SENT_IDS_FILE = os.path.join(BASE_DIR, "sent_ids.txt")
SENT_LOG_FILE = os.path.join(BASE_DIR, "sent_log.html")