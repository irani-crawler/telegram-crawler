from datetime import datetime
from clickhouse_driver import Client

# ClickHouse settings
CH_HOST     = "localhost"
CH_PORT     = 9000
CH_DATABASE = "crawler_logs_db"
CH_USER     = "default"
CH_PASSWORD = ""

_client = None

def _init_client():
    global _client
    if _client is None:
        _client = Client(
            host=CH_HOST,
            port=CH_PORT,
            database=CH_DATABASE,
            user=CH_USER,
            password=CH_PASSWORD
        )
        _client.execute("""
            CREATE TABLE IF NOT EXISTS telegram_fetch_logs (
                timestamp DateTime,
                event     String,
                channel   String,
                details   String
 # utils/ch_logger.py
from datetime import datetime
from clickhouse_driver import Client

# ClickHouse settings
CH_HOST     = "localhost"
CH_PORT     = 9000
CH_DATABASE = "crawler_logs_db"
CH_USER     = "default"
CH_PASSWORD = ""

_client = None

def _init_client():
    global _client
    if _client is None:
        _client = Client(
            host=CH_HOST,
            port=CH_PORT,
            database=CH_DATABASE,
            user=CH_USER,
            password=CH_PASSWORD
        )
        _client.execute("""
            CREATE TABLE IF NOT EXISTS telegram_fetch_logs (
                timestamp DateTime,
                event     String,
                channel   String,
                details   String
            ) ENGINE = MergeTree()
            ORDER BY timestamp
        """)

def log_fetch_event(event: str, channel: str, details: str = ""):
    """
    Log an event to ClickHouse.
    event: e.g. POST_SAVED, POST_ERROR, COMMENTS_SAVED, COMMENTS_ERROR
    channel: channel URL or ID
    details: additional info (post_id, error, count, etc.)
    """
    _init_client()
    now = datetime.now()
    _client.execute(
        "INSERT INTO telegram_fetch_logs (timestamp, event, channel, details) VALUES",
        [(now, event, channel, details)]
    )
           ) ENGINE = MergeTree()
            ORDER BY timestamp
        """)

def log_fetch_event(event: str, channel: str, details: str = ""):
    """
    Log an event to ClickHouse.
    event: e.g. POST_SAVED, POST_ERROR, COMMENTS_SAVED, COMMENTS_ERROR
    channel: channel URL or ID
    details: additional info (post_id, error, count, etc.)
    """
    _init_client()
    now = datetime.now()
    _client.execute(
        "INSERT INTO telegram_fetch_logs (timestamp, event, channel, details) VALUES",
        [(now, event, channel, details)]
    )
