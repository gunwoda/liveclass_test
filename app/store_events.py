import argparse
import json
from datetime import datetime
from pathlib import Path


def parse_event_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def read_events(input_path: Path) -> list[dict]:
    events = []
    with input_path.open("r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                events.append(json.loads(line))
    return events


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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Store generated events into MySQL.")
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("output/events.jsonl"),
        help="input JSONL event file",
    )
    return parser.parse_args()


def main() -> None:
    from db import connect_with_retry

    args = parse_args()
    events = read_events(args.input)

    with connect_with_retry() as conn:
        insert_events(conn, events)

    print(f"stored {len(events)} events from {args.input}")


if __name__ == "__main__":
    main()
