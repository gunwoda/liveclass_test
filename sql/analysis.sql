-- 1. 이벤트 타입별 발생 횟수
SELECT
    event_type,
    COUNT(*) AS event_count
FROM events
GROUP BY event_type
ORDER BY event_count DESC;

-- 2. 유저별 총 이벤트 수
SELECT
    user_id,
    COUNT(*) AS event_count
FROM events
GROUP BY user_id
ORDER BY event_count DESC
LIMIT 10;

-- 3. 시간대별 이벤트 추이
SELECT
    DATE_FORMAT(created_at, '%Y-%m-%d %H:00:00') AS event_hour,
    COUNT(*) AS event_count
FROM events
GROUP BY event_hour
ORDER BY event_hour;

-- 4. 에러 이벤트 비율
SELECT
    ROUND(
        SUM(CASE WHEN event_type = 'error' THEN 1 ELSE 0 END) / COUNT(*) * 100,
        2
    ) AS error_rate_percent
FROM events;
