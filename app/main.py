import argparse

from db import connect_with_retry
from generate_events import generate_events
from store_events import insert_events


def parse_args() -> argparse.Namespace:
    """DB에 바로 저장할 이벤트 개수를 입력받는다."""

    parser = argparse.ArgumentParser(description="Generate events and store them into MySQL.")
    parser.add_argument("--count", type=int, default=1000, help="number of events")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # 과제의 기본 실행 흐름은 중간 JSON 파일을 만들지 않는다.
    # 생성된 이벤트 dict 목록을 곧바로 MySQL INSERT 함수에 넘긴다.
    events = generate_events(args.count)

    # connect_with_retry는 Docker Compose에서 MySQL이 완전히 뜨기 전 실행되는 상황을 대비한다.
    # 지금 브랜치에서는 수동 실행용이고, Compose 구성은 다음 브랜치에서 추가한다.
    with connect_with_retry() as conn:
        insert_events(conn, events)

    print(f"generated and stored {len(events)} events")


if __name__ == "__main__":
    main()
