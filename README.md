# Event Log Pipeline

웹 서비스의 사용자 행동 이벤트를 생성하고, 저장, 분석, 시각화까지 확장하는 데이터 파이프라인 과제입니다.

## 현재 브랜치 범위

`part-1-event-generator` 브랜치는 Step 1 이벤트 생성기만 포함합니다.

## 실행 방법

```bash
python3 app/generate_events.py --count 1000 --output output/events.jsonl
```

실행 결과는 JSON Lines 형식으로 저장됩니다. 다음 브랜치에서 이 이벤트를 PostgreSQL 테이블에 필드별로 저장하도록 확장할 예정입니다.

## 이벤트 설계

| 이벤트 타입 | 설명 |
| --- | --- |
| `page_view` | 사용자가 페이지를 조회한 이벤트 |
| `click` | 사용자가 버튼 또는 영역을 클릭한 이벤트 |
| `purchase` | 사용자가 상품을 구매한 이벤트 |
| `error` | 서비스 사용 중 에러가 발생한 이벤트 |

공통 필드는 `event_id`, `user_id`, `event_type`, `page`, `created_at`으로 구성했습니다. `purchase`는 `product_id`, `amount`를 추가로 사용하고, `error`는 `error_code`를 사용합니다.

이벤트 타입은 웹 서비스에서 기본적으로 확인하는 사용량, 전환, 장애 흐름을 함께 볼 수 있도록 골랐습니다.
