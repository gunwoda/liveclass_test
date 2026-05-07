import os
import time

import mysql.connector
from mysql.connector import Error


def db_config() -> dict:
    return {
        "host": os.getenv("MYSQL_HOST", "127.0.0.1"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MYSQL_USER", "events_user"),
        "password": os.getenv("MYSQL_PASSWORD", "events_password"),
        "database": os.getenv("MYSQL_DATABASE", "events_db"),
    }


def connect_with_retry(max_attempts: int = 30, delay_seconds: float = 1.0):
    last_error = None
    for _ in range(max_attempts):
        try:
            return mysql.connector.connect(**db_config())
        except Error as exc:
            last_error = exc
            time.sleep(delay_seconds)
    raise RuntimeError("mysql is not ready") from last_error
