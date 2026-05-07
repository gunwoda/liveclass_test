from datetime import datetime


def parse_event_time(value: str) -> datetime:
    """이벤트 생성기가 만든 ISO 문자열을 MySQL DATETIME에 넣을 datetime으로 바꿉니다."""

    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def insert_events(conn, events: list[dict]) -> None:
    """
    생성된 이벤트 dict 목록을 MySQL events 테이블에 저장합니다.

    JSON 전체를 한 컬럼에 넣지 않고, 과제 요구사항에 맞게 각 필드를 테이블 컬럼에
    매핑합니다. purchase/error 전용 값이 없는 이벤트는 None이 들어가며 MySQL에는
    NULL로 저장됩니다.
    """

    # executemany에 넘기기 위해 dict를 테이블 컬럼 순서와 같은 tuple로 변환합니다.
    rows = [
        (
            event["event_id"],
            event["user_id"],
            event["event_type"],
            event.get("page"),
            event.get("product_id"),
            event.get("amount"),
            event.get("error_code"),
            parse_event_time(event["created_at"]),
        )
        for event in events
    ]

    query = """
        INSERT INTO events (
            event_id,
            user_id,
            event_type,
            page,
            product_id,
            amount,
            error_code,
            created_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    # 여러 이벤트를 한 번에 insert하고 하나의 트랜잭션으로 commit합니다.
    cursor = conn.cursor()
    try:
        cursor.executemany(query, rows)
        conn.commit()
    finally:
        cursor.close()
