from datetime import datetime


def parse_event_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def insert_events(conn, events: list[dict]) -> None:
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

    cursor = conn.cursor()
    try:
        cursor.executemany(query, rows)
        conn.commit()
    finally:
        cursor.close()
