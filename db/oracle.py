"""Read-only Oracle connection and query execution helpers."""
from contextlib import contextmanager
from datetime import date, datetime
import logging

import oracledb

from config import OracleConfig

logger = logging.getLogger(__name__)


@contextmanager
def connection(settings: OracleConfig):
    dsn = oracledb.makedsn(settings.host, settings.port, service_name=settings.service)
    conn = None
    try:
        conn = oracledb.connect(user=settings.user, password=settings.password, dsn=dsn)
        yield conn
    finally:
        if conn is not None:
            conn.close()


def _value(value):
    """Convert Oracle LOBs and dates to response-safe native values."""
    if hasattr(value, "read"):
        return value.read()
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return value


def fetch_rows(conn, statement: str, binds: dict) -> list[dict]:
    """Execute a fixed, parameterized SELECT and return lower-case keyed rows."""
    with conn.cursor() as cursor:
        cursor.execute(statement, binds)
        columns = [item[0].lower() for item in cursor.description]
        return [dict(zip(columns, (_value(value) for value in row))) for row in cursor]
