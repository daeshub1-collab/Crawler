"""
사출기(IMM) 북미 시장 모니터링 — 메인 실행 파일

사용법:
  python main.py                        # 매주 월요일 09:00 자동 실행
  python main.py --once                 # 1회 즉시 실행
  python main.py --dry-run              # 이메일/기록 없이 결과만 출력
  python main.py --site ustr            # 특정 크롤러만 실행
  python main.py --force-send           # sent_ids.txt 무시하고 전체 발송
  python main.py --once --dry-run       # 옵션 조합 가능
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

# injection_monitor/ 디렉터리를 sys.path 맨 앞에 추가
# → 상위 디렉터리에서 실행해도 crawlers, filter, mailer, sent_log를 찾을 수 있게 함
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))


def _banner():
    print()
    print("=" * 62)
    print("   사출기(IMM) 북미 시장 모니터링 시스템")
    print(f"   실행 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 62)


def run(args: argparse.Namespace) -> None:
    from crawlers import get_all_crawlers
    from filter import filter_items
    from sent_log import load_sent_ids, save_sent_id, update_html_log, make_id
    from mailer import send_mail

    _banner()

    # ── 1. 크롤링 ─────────────────────────────────────────────────────────────
    print("\n[1/4] 크롤링 시작")
    try:
        crawlers = get_all_crawlers(site=args.site)
    except ValueError as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

    all_items: list = []
    for crawler in crawlers:
        try:
            results = crawler.parse()
            src = results[0]["source"] if results else crawler.__class__.__name__
            print(f"  {src:30s} {len(results):>4}건")
            all_items.extend(results)
        except Exception as e:
            print(f"  [ERROR] {crawler.__class__.__name__}: {e}")

    print(f"  {'합계':30s} {len(all_items):>4}건")

    # ── 2. 필터링 ─────────────────────────────────────────────────────────────
    print("\n[2/4] 키워드 필터링")
    filtered = filter_items(all_items)
    print(f"  필터 통과: {len(filtered)}건")

    cat_summary = {}
    for item in filtered:
        cat_summary[item["category"]] = cat_summary.get(item["category"], 0) + 1
    for cat, cnt in cat_summary.items():
        print(f"    [{cat}] {cnt}건")

    # ── 3. 신규 공고 선별 ─────────────────────────────────────────────────────
    print("\n[3/4] 신규 공고 선별")
    if args.force_send:
        new_items = filtered
        print(f"  --force-send: 전체 {len(new_items)}건 강제 발송")
    else:
        sent_ids = load_sent_ids()
        new_items = [item for item in filtered if make_id(item) not in sent_ids]
        print(f"  신규: {len(new_items)}건  (기발송 제외)")

    # ── dry-run ───────────────────────────────────────────────────────────────
    if args.dry_run:
        print("\n[DRY-RUN] 이메일 발송 및 기록 건너뜀. 대상 공고 목록:")
        if new_items:
            for item in new_items:
                print(f"  [{item['category']:6}] {item['title'][:60]}  ({item['source']})")
        else:
            print("  (없음)")
        print("=" * 62)
        return

    # ── 4. 이메일 발송 + 이력 업데이트 ───────────────────────────────────────
    print("\n[4/4] 이메일 발송")
    success = send_mail(new_items)

    if new_items and (success or args.force_send):
        for item in new_items:
            save_sent_id(make_id(item))
        update_html_log(new_items)
        print(f"  이력 업데이트 완료 (sent_ids.txt + sent_log.html, {len(new_items)}건)")

    print("=" * 62)
    print()


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="사출기(IMM) 북미 시장 모니터링",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument(
        "--once",
        action="store_true",
        help="1회 즉시 실행 (스케줄러 없이)",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        dest="dry_run",
        help="이메일 발송 없이 결과만 출력 (sent_ids.txt 기록 안 함)",
    )
    p.add_argument(
        "--site",
        type=str,
        metavar="CODE",
        help="특정 크롤러만 실행 (ustr / cbp / federalregister / plasticsnews / mexicobusiness / canplastics / kotra / kita)",
    )
    p.add_argument(
        "--force-send",
        action="store_true",
        dest="force_send",
        help="sent_ids.txt를 무시하고 필터 통과 전체를 발송",
    )
    return p


def main() -> None:
    args = _build_parser().parse_args()

    # --once / --dry-run / --site / --force-send 중 하나라도 있으면 즉시 실행
    if args.once or args.dry_run or args.site or args.force_send:
        run(args)
        return

    # 아무 옵션 없음 → 스케줄러 모드
    try:
        import schedule
        import time
    except ImportError:
        print("[ERROR] schedule 패키지 미설치 — pip install schedule")
        sys.exit(1)

    print(f"[SCHEDULER] 매주 월요일 09:00 자동 실행 대기 중... (Ctrl+C로 종료)")
    schedule.every().monday.at("09:00").do(run, args=args)

    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    main()
