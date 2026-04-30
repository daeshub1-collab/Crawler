import argparse
import json
import schedule
import time
from datetime import datetime
from pathlib import Path

from crawlers import ALL_CRAWLERS
from mailer import send_mail
from sent_log import load_sent_ids
from config import SCHEDULE_DAY, SCHEDULE_TIME


def normalize_item(item: dict) -> dict:
    """
    Dify가 읽기 쉬운 형태로 기사 데이터를 정리합니다.
    각 크롤러마다 필드명이 조금 달라도 최대한 안전하게 처리합니다.
    """

    return {
        "source": item.get("source", ""),
        "date": item.get("date", ""),
        "title": item.get("title", ""),
        "url": item.get("url", ""),
        "summary": (
            item.get("summary")
            or item.get("snippet")
            or item.get("description")
            or item.get("content")
            or ""
        ),
        "region_hint": item.get("region", ""),
        "category_hint": item.get("category", ""),
    }


def save_json_for_dify(items: list, output_path: str) -> None:
    """
    크롤링 결과를 Dify가 가져갈 수 있는 JSON 파일로 저장합니다.
    """

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    normalized_items = [normalize_item(item) for item in items]

    payload = {
        "report_date": datetime.now().strftime("%Y-%m-%d"),
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "project": "Injection Molding Machine North America Market & Tariff Monitor",
        "article_count": len(normalized_items),
        "articles": normalized_items,
    }

    output_file.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"✅ Dify용 JSON 저장 완료: {output_file}")
    print(f"✅ JSON 기사 수: {len(normalized_items)}건")


def run_crawl(
    dry_run: bool = False,
    site: str = None,
    force_send: bool = False,
    export_json: str = None,
    skip_mail: bool = False,
):
    """전체 크롤링 실행 후 이메일 발송 또는 JSON 저장"""
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

            print(
                f"  ✅ {crawler.name}: 수집 {len(items)}건 / 신규 {len(new_items)}건"
            )

        except Exception as e:
            print(f"  ❌ {crawler.name} 오류: {e}")

    print(f"\n{'='*50}")
    print(f"📊 총 수집: {len(all_items)}건 (중복 제거 후)")
    print(f"{'='*50}\n")

    # Dify용 JSON 저장
    if export_json:
        save_json_for_dify(all_items, export_json)

    # 메일 발송 생략 옵션
    if skip_mail:
        print("📭 이메일 발송 생략: --skip-mail 옵션 사용")
        return all_items

    # 기존 Gmail 발송 로직 유지
    send_mail(all_items, dry_run=dry_run)

    return all_items


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

    parser.add_argument(
        "--export-json",
        type=str,
        default=None,
        help="Dify가 가져갈 JSON 파일 경로를 지정합니다. 예: --export-json ../data/latest_articles.json"
    )

    parser.add_argument(
        "--skip-mail",
        action="store_true",
        help="이메일 발송 단계를 생략합니다. Dify 연동용 JSON만 만들 때 사용합니다."
    )

    args = parser.parse_args()

    if args.dry_run or args.once or args.export_json:
        # 1회 실행
        run_crawl(
            dry_run=args.dry_run,
            site=args.site,
            force_send=args.force_send,
            export_json=args.export_json,
            skip_mail=args.skip_mail,
        )
    else:
        # 스케줄 실행
        print(f"⏰ 스케줄 모드 시작 — 매주 {SCHEDULE_DAY} {SCHEDULE_TIME} 자동 실행")
        getattr(schedule.every(), SCHEDULE_DAY).at(SCHEDULE_TIME).do(run_crawl)

        while True:
            schedule.run_pending()
            time.sleep(60)


if __name__ == "__main__":
    main()