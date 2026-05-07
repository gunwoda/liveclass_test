# MySQL events 테이블에 저장된 로그를 과제 요구사항 기준으로 집계하는 쿼리 모음입니다.
# Step 5 시각화에서도 같은 집계 결과를 재사용할 수 있게 이름을 붙여 관리합니다.
ANALYSIS_QUERIES = {
    "event_type_counts": """
        SELECT
            event_type,
            COUNT(*) AS event_count
        FROM events
        GROUP BY event_type
        ORDER BY event_count DESC;
    """,
    "top_users": """
        SELECT
            user_id,
            COUNT(*) AS event_count
        FROM events
        GROUP BY user_id
        ORDER BY event_count DESC
        LIMIT 10;
    """,
    "hourly_trend": """
        SELECT
            DATE_FORMAT(created_at, '%Y-%m-%d %H:00:00') AS event_hour,
            COUNT(*) AS event_count
        FROM events
        GROUP BY event_hour
        ORDER BY event_hour;
    """,
    "error_rate": """
        SELECT
            ROUND(
                SUM(CASE WHEN event_type = 'error' THEN 1 ELSE 0 END) / COUNT(*) * 100,
                2
            ) AS error_rate_percent
        FROM events;
    """,
}


def fetch_query_result(conn, query: str) -> tuple[list[str], list[tuple]]:
    """쿼리를 실행하고, 출력에 필요한 컬럼명과 row 목록을 함께 반환합니다."""

    cursor = conn.cursor()
    try:
        cursor.execute(query)
        columns = [column[0] for column in cursor.description]
        rows = cursor.fetchall()
        return columns, rows
    finally:
        cursor.close()


def print_table(title: str, columns: list[str], rows: list[tuple]) -> None:
    """터미널에서 바로 확인할 수 있도록 집계 결과를 간단한 표 형태로 출력합니다."""

    print(f"\n[{title}]")
    print(" | ".join(columns))
    print("-" * max(20, len(" | ".join(columns))))

    if not rows:
        print("(no rows)")
        return

    for row in rows:
        print(" | ".join(str(value) for value in row))


def run_analysis() -> None:
    # db.py는 app 디렉터리에서 스크립트로 실행할 때 import되므로 실행 시점에 불러옵니다.
    from db import connect_with_retry

    with connect_with_retry() as conn:
        for title, query in ANALYSIS_QUERIES.items():
            columns, rows = fetch_query_result(conn, query)
            print_table(title, columns, rows)


if __name__ == "__main__":
    run_analysis()
