import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib import font_manager

from analyze_events import ANALYSIS_QUERIES, fetch_query_result


def configure_korean_font() -> None:
    """차트의 한국어 제목과 축 라벨이 깨지지 않도록 한글 폰트를 설정합니다."""

    font_candidates = [
        "Noto Sans CJK KR",
        "Noto Sans CJK JP",
        "NanumGothic",
        "AppleGothic",
        "Malgun Gothic",
    ]
    available_fonts = {font.name for font in font_manager.fontManager.ttflist}

    for font_name in font_candidates:
        if font_name in available_fonts:
            plt.rcParams["font.family"] = font_name
            break

    plt.rcParams["axes.unicode_minus"] = False


def format_hour_label(value) -> str:
    """시간대 라벨을 월-일-시 형식으로 줄여 표시합니다."""

    if hasattr(value, "strftime"):
        return value.strftime("%m-%d %H시")

    value_text = str(value)
    try:
        return value_text[5:10] + " " + value_text[11:13] + "시"
    except IndexError:
        return value_text


def save_event_type_chart(conn, output_dir: Path) -> Path:
    """이벤트 타입별 발생 횟수를 막대그래프로 저장합니다."""

    columns, rows = fetch_query_result(conn, ANALYSIS_QUERIES["event_type_counts"])
    event_type_index = columns.index("event_type")
    count_index = columns.index("event_count")

    event_types = [row[event_type_index] for row in rows]
    event_counts = [row[count_index] for row in rows]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(event_types, event_counts, color=["#2563eb", "#16a34a", "#f97316", "#dc2626"])
    ax.set_title("이벤트 타입별 발생 횟수")
    ax.set_xlabel("이벤트 타입")
    ax.set_ylabel("발생 횟수")
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

    event_hours = [format_hour_label(row[hour_index]) for row in rows]
    event_counts = [row[count_index] for row in rows]

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(event_hours, event_counts, marker="o", color="#0891b2")
    ax.set_title("시간대별 이벤트 추이")
    ax.set_xlabel("시간")
    ax.set_ylabel("발생 횟수")
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

    configure_korean_font()
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
