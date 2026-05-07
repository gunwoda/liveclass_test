import argparse
import json
import random
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path


# 실제 웹 서비스에서 흔히 남기는 사용자 행동을 단순화한 이벤트 타입입니다.
# 메인 파이프라인(app/main.py)은 이 값들로 이벤트를 만든 뒤 바로 MySQL에 저장합니다.
EVENT_TYPES = ("page_view", "click", "purchase", "error")

# page_view, click, error 이벤트가 발생할 수 있는 샘플 페이지 목록입니다.
PAGES = ("/", "/courses", "/courses/python", "/checkout", "/help")

# error 이벤트를 분석할 때 단순 집계가 가능하도록 에러 코드를 몇 가지로 제한합니다.
ERROR_CODES = ("E_TIMEOUT", "E_PAYMENT_FAILED", "E_NOT_FOUND", "E_INTERNAL")


def random_event() -> dict:
    """
    랜덤한 웹 서비스 이벤트 1개를 생성합니다.

    모든 이벤트는 같은 dict 구조를 가집니다. 이벤트 타입에 따라 사용하지 않는
    필드는 None으로 두고, MySQL 저장 시 이 값들이 NULL 컬럼으로 들어갑니다.
    """

    # 이벤트 타입은 가중치 기반으로 랜덤 선택합니다.
    # page_view 55%, click 25%, purchase 12%, error 8% 비율로 생성합니다.
    event_type = random.choices(
        EVENT_TYPES,
        weights=(55, 25, 12, 8),
        k=1,
    )[0]

    # 시간대별 분석을 할 수 있도록 최근 48시간 안에서 발생 시간을 분산합니다.
    created_at = datetime.now(timezone.utc) - timedelta(
        hours=random.randint(0, 47),
        minutes=random.randint(0, 59),
        seconds=random.randint(0, 59),
    )

    # 단일 events 테이블에 넣기 위해 모든 이벤트가 같은 필드 세트를 갖게 합니다.
    event = {
        "event_id": str(uuid.uuid4()),          # 이벤트 고유 ID입니다.
        "user_id": random.randint(1, 100),      # 사용자 ID입니다.
        "event_type": event_type,               # 이벤트 타입입니다.
        "page": random.choice(PAGES),           # 이벤트 발생 페이지입니다.
        "product_id": None,                     # 구매 이벤트일 때 상품 ID를 저장합니다.
        "amount": None,                         # 구매 이벤트일 때 결제 금액을 저장합니다.
        "error_code": None,                     # 에러 이벤트일 때 에러 코드를 저장합니다.
        "created_at": created_at.isoformat(),   # ISO 형식의 이벤트 생성 시간입니다.
    }

    # 구매 이벤트는 매출/전환 분석에 필요한 상품 ID와 결제 금액을 채웁니다.
    if event_type == "purchase":
        event["product_id"] = random.randint(1000, 1015)
        event["amount"] = round(random.uniform(9.9, 199.9), 2)
        event["page"] = "/checkout"

    # 에러 이벤트는 장애 비율과 에러 코드별 집계를 할 수 있도록 error_code를 채웁니다.
    elif event_type == "error":
        event["error_code"] = random.choice(ERROR_CODES)

    return event


def generate_events(count: int) -> list[dict]:
    """
    지정한 개수만큼 랜덤 이벤트를 생성합니다.
    """

    return [random_event() for _ in range(count)]


def write_jsonl(events: list[dict], output_path: Path) -> None:
    """
    테스트/샘플 확인용으로 이벤트 목록을 JSONL 파일에 저장합니다.

    실제 과제 파이프라인은 app/main.py에서 생성한 이벤트를 바로 MySQL에 저장합니다.
    이 함수는 DB 없이 이벤트 모양을 빠르게 확인하거나 테스트 데이터를 눈으로
    검토할 때만 사용하는 보조 기능입니다.
    """

    # 출력 디렉터리가 없으면 생성합니다.
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # JSONL은 한 줄에 이벤트 하나를 저장해서 샘플 확인과 diff 확인이 쉽습니다.
    with output_path.open("w", encoding="utf-8") as file:
        for event in events:
            file.write(json.dumps(event, ensure_ascii=False) + "\n")


def parse_args() -> argparse.Namespace:
    """
    테스트용 JSONL 생성 커맨드의 인자를 파싱합니다.

    DB 저장까지 수행하려면 이 파일이 아니라 app/main.py를 실행합니다.
    --count: 생성할 이벤트 개수입니다.
    --output: 테스트/샘플용 JSONL 파일 경로입니다.
    """

    parser = argparse.ArgumentParser(description="Generate random web service events.")

    # 생성할 이벤트 개수 옵션입니다.
    parser.add_argument(
        "--count",
        type=int,
        default=1000,
        help="number of events",
    )

    # JSONL 파일 저장 경로 옵션입니다.
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("output/events.jsonl"),
        help="sample JSONL output path for testing",
    )

    return parser.parse_args()


def main() -> None:
    """
    테스트용 샘플 이벤트 파일을 만듭니다.

    이 진입점은 DB 저장용이 아닙니다. 실제 파이프라인 실행은 app/main.py가 담당합니다.
    """

    # 커맨드라인 인자를 파싱합니다.
    args = parse_args()

    # 지정한 개수만큼 이벤트를 생성합니다.
    events = generate_events(args.count)

    # 생성한 이벤트를 JSONL 파일로 저장합니다.
    write_jsonl(events, args.output)

    # 처리 결과를 출력합니다.
    print(f"generated {len(events)} events at {args.output}")


# 이 파일을 직접 실행했을 때만 main 함수를 실행합니다.
if __name__ == "__main__":
    main()
