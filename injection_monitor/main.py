import argparse
import schedule
import time
from datetime import datetime

from crawlers import ALL_CRAWLERS
from mailer import send_mail
from sent_log import load_sent_ids
from config import SCHEDULE_DAY, SCHEDULE_TIME


def run_crawl(dry_run: bool = False, site: str = None, force_send: bool = False):
    """전체 크롤링 실행 후 이메일 발송"""
    print(f"\n{'='*50}")
    print(f"🚀 크롤링 시작: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}")

    sent_ids = load_sent_ids() if not force_send else set()
    all_items = []

    for CrawlerClass in ALL_CRAWLERS:
        crawler = CrawlerClass()

        # 특정 사이트만 실행하는 경우
        if site and crawler.name != site:
            continue

        try:
            items = crawler.crawl()

            # 중복 제거
            new_items = [
                item for item in items
                if item.get("url") not in sent_ids
            ]

            all_items.extend(new_items)

        except Exception as e:
            print(f"  ❌ {crawler.name} 오류: {e}")

    print(f"\n{'='*50}")
    print(f"📊 총 수집: {len(all_items)}건 (중복 제거 후)")
    print(f"{'='*50}\n")

    send_mail(all_items, dry_run=dry_run)


def main():
    parser = argparse.ArgumentParser(description="사출기 북미 시장 모니터링")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="이메일 발송 없이 수집 결과만 출력"
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="스케줄 없이 1회만 실행"
    )
    parser.add_argument(
        "--site",
        type=str,
        default=None,
        help="특정 사이트만 테스트 (예: --site plasticsnews)"
    )
    parser.add_argument(
        "--force-send",
        action="store_true",
        help="중복 무시하고 전체 발송"
    )
    args = parser.parse_args()

    if args.dry_run or args.once:
        # 1회 실행
        run_crawl(
            dry_run=args.dry_run,
            site=args.site,
            force_send=args.force_send,
        )
    else:
        # 스케줄 실행 (매주 월요일 09:00)
        print(f"⏰ 스케줄 모드 시작 — 매주 {SCHEDULE_DAY} {SCHEDULE_TIME} 자동 실행")
        getattr(schedule.every(), SCHEDULE_DAY).at(SCHEDULE_TIME).do(run_crawl)

        while True:
            schedule.run_pending()
            time.sleep(60)


if __name__ == "__main__":
    main()