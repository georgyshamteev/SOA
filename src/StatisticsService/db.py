import logging
import time
from datetime import datetime
from clickhouse_driver import Client

logger = logging.getLogger('db')

CLICKHOUSE_HOST = 'clickhouse'
CLICKHOUSE_PORT = 9000
CLICKHOUSE_DB = 'social_network'

def get_clickhouse_client():
    client = Client(
        host=CLICKHOUSE_HOST,
        port=CLICKHOUSE_PORT,
        user='stats_user',
        password='stats_password'
    )

    client.execute(f"CREATE DATABASE IF NOT EXISTS {CLICKHOUSE_DB}")

    return Client(
        host=CLICKHOUSE_HOST,
        port=CLICKHOUSE_PORT,
        database=CLICKHOUSE_DB,
        user='stats_user',
        password='stats_password'
    )

def wait_for_clickhouse():
    max_attempts = 30
    attempts = 0
    while attempts < max_attempts:
        try:
            client = get_clickhouse_client()
            client.execute("SELECT 1")
            logger.info("ClickHouse connection established!")

            client.execute(f"CREATE DATABASE IF NOT EXISTS {CLICKHOUSE_DB}")

            client.execute(f"""
                CREATE TABLE IF NOT EXISTS events (
                    event_type Enum('view', 'like', 'comment'),
                    client_id String,
                    post_id Int64,
                    comment_id Nullable(String),
                    timestamp DateTime
                ) ENGINE = MergeTree()
                PARTITION BY toYYYYMM(timestamp)
                ORDER BY (event_type, post_id, timestamp)
                """)

            return True
        except Exception as e:
            attempts += 1
            logger.warning(f"Waiting for ClickHouse... attempt {attempts}/{max_attempts}: {e}")
            time.sleep(2)

    logger.error("Failed to connect to ClickHouse!")
    return False

def parse_timestamp(iso_date):
    try:
        return datetime.fromisoformat(iso_date)
    except ValueError:
        try:
            return datetime.strptime(iso_date, '%Y-%m-%dT%H:%M:%S.%f')
        except ValueError:
            return datetime.now()
