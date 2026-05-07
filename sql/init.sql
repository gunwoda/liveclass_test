CREATE TABLE IF NOT EXISTS events (
    event_id CHAR(36) PRIMARY KEY,
    user_id INT NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    page VARCHAR(100),
    product_id INT,
    amount DECIMAL(10, 2),
    error_code VARCHAR(50),
    created_at DATETIME NOT NULL,
    INDEX idx_events_event_type (event_type),
    INDEX idx_events_user_id (user_id),
    INDEX idx_events_created_at (created_at)
);
