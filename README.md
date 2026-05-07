# Event Log Pipeline

웹 서비스의 사용자 행동 이벤트를 생성하고, 저장, 분석, 시각화까지 확장하는 데이터 파이프라인 과제입니다.

## 현재 브랜치 범위

`part-2-mysql-storage` 브랜치는 Step 2 로그 저장을 추가합니다.

## 실행 방법

MySQL 접속 정보는 환경 변수로 설정합니다.

```bash
export MYSQL_HOST=127.0.0.1
export MYSQL_PORT=3306
export MYSQL_USER=events_user
export MYSQL_PASSWORD=events_password
export MYSQL_DATABASE=events_db
```

테이블은 [sql/init.sql](./sql/init.sql)의 스키마로 생성합니다.

```bash
mysql -h "$MYSQL_HOST" -P "$MYSQL_PORT" -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE" < sql/init.sql
python3 app/main.py --count 1000
```

`app/main.py`는 이벤트를 메모리에서 생성한 뒤 바로 MySQL에 저장합니다. `app/generate_events.py`의 JSONL 출력 기능은 생성되는 이벤트 샘플을 확인하기 위한 보조 실행 경로입니다.

Docker Compose로 MySQL까지 자동 실행하는 구성은 다음 브랜치에서 추가할 예정입니다.

## 이벤트 설계

| 이벤트 타입 | 설명 |
| --- | --- |
| `page_view` | 사용자가 페이지를 조회한 이벤트 |
| `click` | 사용자가 버튼 또는 영역을 클릭한 이벤트 |
| `purchase` | 사용자가 상품을 구매한 이벤트 |
| `error` | 서비스 사용 중 에러가 발생한 이벤트 |

공통 필드는 `event_id`, `user_id`, `event_type`, `page`, `created_at`으로 구성했습니다. `purchase`는 `product_id`, `amount`를 추가로 사용하고, `error`는 `error_code`를 사용합니다.

이벤트 타입은 웹 서비스에서 기본적으로 확인하는 사용량, 전환, 장애 흐름을 함께 볼 수 있도록 골랐습니다.

## 스키마 설명

저장소는 MySQL을 선택했습니다. 작은 이벤트 로그를 테이블 형태로 저장하고 SQL 집계를 수행하기에 충분하며, Docker Compose에서 앱과 함께 띄우기 쉽고 면접에서 설명하기도 명확합니다.

```sql
CREATE TABLE IF NOT EXISTS events (
    event_id CHAR(36) PRIMARY KEY,
    user_id INT NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    page VARCHAR(100),
    product_id INT,
    amount DECIMAL(10, 2),
    error_code VARCHAR(50),
    created_at DATETIME NOT NULL
);
```

JSON을 통째로 저장하지 않고 이벤트의 주요 필드를 컬럼으로 분리했습니다. 이벤트 타입별 집계, 유저별 집계, 시간대별 집계를 빠르게 수행할 수 있도록 `event_type`, `user_id`, `created_at`에 인덱스를 둡니다.
