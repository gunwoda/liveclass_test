import argparse
import json
import random
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path


# 생성할 이벤트 타입 목록
EVENT_TYPES = ("page_view", "click", "purchase", "error")

# 이벤트가 발생할 수 있는 페이지 목록
PAGES = ("/", "/courses", "/courses/python", "/checkout", "/help")

# error 이벤트 발생 시 사용할 에러 코드 목록
ERROR_CODES = ("E_TIMEOUT", "E_PAYMENT_FAILED", "E_NOT_FOUND", "E_INTERNAL")


def random_event() -> dict:
    """
    랜덤한 웹 서비스 이벤트 1개를 생성한다.
    이벤트 타입에 따라 purchase, error 관련 필드를 추가로 설정한다.
    """

    # 이벤트 타입을 가중치 기반으로 랜덤 선택
    # page_view 55%, click 25%, purchase 12%, error 8% 비율로 생성
    event_type = random.choices(
        EVENT_TYPES,
        weights=(55, 25, 12, 8),
        k=1,
    )[0]

    # 현재 UTC 시간 기준 최근 48시간 이내의 랜덤한 생성 시간 생성
    created_at = datetime.now(timezone.utc) - timedelta(
        hours=random.randint(0, 47),
        minutes=random.randint(0, 59),
        seconds=random.randint(0, 59),
    )

    # 모든 이벤트가 공통으로 가지는 기본 필드 구성
    event = {
        "event_id": str(uuid.uuid4()),          # 이벤트 고유 ID
        "user_id": random.randint(1, 100),      # 사용자 ID
        "event_type": event_type,               # 이벤트 타입
        "page": random.choice(PAGES),           # 이벤트 발생 페이지
        "product_id": None,                     # 구매 이벤트일 때 상품 ID 저장
        "amount": None,                         # 구매 이벤트일 때 결제 금액 저장
        "error_code": None,                     # 에러 이벤트일 때 에러 코드 저장
        "created_at": created_at.isoformat(),   # ISO 형식의 이벤트 생성 시간
    }

    # 구매 이벤트인 경우 상품 ID, 결제 금액, 페이지 정보 설정
    if event_type == "purchase":
        event["product_id"] = random.randint(1000, 1015)
        event["amount"] = round(random.uniform(9.9, 199.9), 2)
        event["page"] = "/checkout"

    # 에러 이벤트인 경우 에러 코드 설정
    elif event_type == "error":
        event["error_code"] = random.choice(ERROR_CODES)

    return event


def generate_events(count: int) -> list[dict]:
    """
    지정한 개수만큼 랜덤 이벤트를 생성한다.
    """

    return [random_event() for _ in range(count)]


def write_jsonl(events: list[dict], output_path: Path) -> None:
    """
    이벤트 목록을 JSONL 파일로 저장한다.
    JSONL은 한 줄에 하나의 JSON 객체를 저장하는 형식이다.
    """

    # 출력 디렉터리가 없으면 생성
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 이벤트를 한 줄씩 JSON 문자열로 변환하여 파일에 기록
    with output_path.open("w", encoding="utf-8") as file:
        for event in events:
            file.write(json.dumps(event, ensure_ascii=False) + "\n")


def parse_args() -> argparse.Namespace:
    """
    커맨드라인 인자를 파싱한다.
    --count: 생성할 이벤트 개수
    --output: 저장할 JSONL 파일 경로
    """

    parser = argparse.ArgumentParser(description="Generate random web service events.")

    # 생성할 이벤트 개수 옵션
    parser.add_argument(
        "--count",
        type=int,
        default=1000,
        help="number of events",
    )

    # JSONL 파일 저장 경로 옵션
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("output/events.jsonl"),
        help="JSONL output path",
    )

    return parser.parse_args()


def main() -> None:
    """
    프로그램의 시작 지점.
    인자를 읽고, 이벤트를 생성한 뒤, JSONL 파일로 저장한다.
    """

    # 커맨드라인 인자 파싱
    args = parse_args()

    # 지정한 개수만큼 이벤트 생성
    events = generate_events(args.count)

    # 생성한 이벤트를 JSONL 파일로 저장
    write_jsonl(events, args.output)

    # 처리 결과 출력
    print(f"generated {len(events)} events at {args.output}")


# 이 파일을 직접 실행했을 때만 main 함수 실행
if __name__ == "__main__":
    main()