import argparse

from db import connect_with_retry
from generate_events import generate_events
from store_events import insert_events


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate events and store them into MySQL.")
    parser.add_argument("--count", type=int, default=1000, help="number of events")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    events = generate_events(args.count)

    with connect_with_retry() as conn:
        insert_events(conn, events)

    print(f"generated and stored {len(events)} events")


if __name__ == "__main__":
    main()
