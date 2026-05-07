import argparse
import json
import random
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path


EVENT_TYPES = ("page_view", "click", "purchase", "error")
PAGES = ("/", "/courses", "/courses/python", "/checkout", "/help")
ERROR_CODES = ("E_TIMEOUT", "E_PAYMENT_FAILED", "E_NOT_FOUND", "E_INTERNAL")


def random_event() -> dict:
    event_type = random.choices(
        EVENT_TYPES,
        weights=(55, 25, 12, 8),
        k=1,
    )[0]
    created_at = datetime.now(timezone.utc) - timedelta(
        hours=random.randint(0, 47),
        minutes=random.randint(0, 59),
        seconds=random.randint(0, 59),
    )

    event = {
        "event_id": str(uuid.uuid4()),
        "user_id": random.randint(1, 100),
        "event_type": event_type,
        "page": random.choice(PAGES),
        "product_id": None,
        "amount": None,
        "error_code": None,
        "created_at": created_at.isoformat(),
    }

    if event_type == "purchase":
        event["product_id"] = random.randint(1000, 1015)
        event["amount"] = round(random.uniform(9.9, 199.9), 2)
        event["page"] = "/checkout"
    elif event_type == "error":
        event["error_code"] = random.choice(ERROR_CODES)

    return event


def generate_events(count: int) -> list[dict]:
    return [random_event() for _ in range(count)]


def write_jsonl(events: list[dict], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        for event in events:
            file.write(json.dumps(event, ensure_ascii=False) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate random web service events.")
    parser.add_argument("--count", type=int, default=1000, help="number of events")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("output/events.jsonl"),
        help="JSONL output path",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    events = generate_events(args.count)
    write_jsonl(events, args.output)
    print(f"generated {len(events)} events at {args.output}")


if __name__ == "__main__":
    main()
