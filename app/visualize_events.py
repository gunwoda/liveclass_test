import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from analyze_events import ANALYSIS_QUERIES, fetch_query_result


def save_event_type_chart(conn, output_dir: Path) -> Path:
    """이벤트 타입별 발생 횟수를 막대그래프로 저장합니다."""

    columns, rows = fetch_query_result(conn, ANALYSIS_QUERIES["event_type_counts"])
    event_type_index = columns.index("event_type")
    count_index = columns.index("event_count")

    event_types = [row[event_type_index] for row in rows]
    event_counts = [row[count_index] for row in rows]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(event_types, event_counts, color=["#2563eb", "#16a34a", "#f97316", "#dc2626"])
    ax.set_title("Event Count by Type")
    ax.set_xlabel("Event Type")
    ax.set_ylabel("Count")
    ax.grid(axis="y", alpha=0.25)

    output_path = output_dir / "event_type_counts.png"
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)
    return output_path


def save_hourly_trend_chart(conn, output_dir: Path) -> Path:
    """시간대별 이벤트 발생 추이를 라인그래프로 저장합니다."""

    columns, rows = fetch_query_result(conn, ANALYSIS_QUERIES["hourly_trend"])
    hour_index = columns.index("event_hour")
    count_index = columns.index("event_count")

    event_hours = [row[hour_index] for row in rows]
    event_counts = [row[count_index] for row in rows]

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(event_hours, event_counts, marker="o", color="#0891b2")
    ax.set_title("Hourly Event Trend")
    ax.set_xlabel("Hour")
    ax.set_ylabel("Count")
    ax.grid(alpha=0.25)
    ax.tick_params(axis="x", rotation=60)

    output_path = output_dir / "hourly_trend.png"
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)
    return output_path


def save_charts(output_dir: Path) -> list[Path]:
    """분석 쿼리 결과를 차트 이미지로 저장합니다."""

    from db import connect_with_retry

    output_dir.mkdir(parents=True, exist_ok=True)

    with connect_with_retry() as conn:
        return [
            save_event_type_chart(conn, output_dir),
            save_hourly_trend_chart(conn, output_dir),
        ]


def parse_args() -> argparse.Namespace:
    """차트 이미지 저장 경로를 입력받습니다."""

    parser = argparse.ArgumentParser(description="Visualize event analysis results.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("output/charts"),
        help="directory for chart image files",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_paths = save_charts(args.output_dir)

    for output_path in output_paths:
        print(f"saved chart: {output_path}")


if __name__ == "__main__":
    main()
