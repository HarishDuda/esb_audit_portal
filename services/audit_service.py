from datetime import datetime, timedelta
import logging

from config import Config
from db.oracle import connection, fetch_rows
from db import queries

logger = logging.getLogger(__name__)

RANGE_DAYS = {"today": 1, "3_days": 3, "7_days": 7}


class InputError(ValueError):
    pass


def _validate(data: dict):
    rrn = str(data.get("rrn", "")).strip()
    environment = str(data.get("environment", "")).strip().upper()
    period = str(data.get("range", "")).strip().lower()
    if not rrn:
        raise InputError("RRN is required.")
    if len(rrn) > 100 or not all(char.isalnum() or char in "-_" for char in rrn):
        raise InputError("RRN contains invalid characters.")
    if environment not in Config.ENVIRONMENTS:
        raise InputError("Select a valid environment.")
    if period in RANGE_DAYS:
        return rrn, environment, period, {"rrn": rrn, "days": RANGE_DAYS[period]}
    if period != "custom":
        raise InputError("Select a valid query range.")
    try:
        start = datetime.fromisoformat(str(data.get("from_date", "")).strip())
        end = datetime.fromisoformat(str(data.get("to_date", "")).strip())
    except ValueError as exc:
        raise InputError("Provide valid From and To dates.") from exc
    if start >= end:
        raise InputError("From Date must be before To Date.")
    if end - start > timedelta(days=31):
        raise InputError("Custom query range cannot exceed 31 days.")
    return rrn, environment, period, {"rrn": rrn, "from_date": start, "to_date": end}


def _services(rows):
    unique, seen = [], set()
    for row in rows:
        key = (row.get("service_name"), row.get("url"))
        if key in seen:
            continue
        seen.add(key)
        unique.append(row)
    return unique


def search(data: dict) -> dict:
    rrn, environment, period, binds = _validate(data)
    settings = Config.oracle_config(environment)
    logger.info("Audit search initiated: environment=%s rrn=%s", environment, rrn)
    recent = period in RANGE_DAYS
    with connection(settings) as conn:
        ace_rows = fetch_rows(conn, queries.ACE_RECENT if recent else queries.ACE_CUSTOM, binds)
        dtl_rows = fetch_rows(conn, queries.DTL_RECENT if recent else queries.DTL_CUSTOM, binds)
    logger.info("Audit query completed: environment=%s rrn=%s ace=%d dtl=%d", environment, rrn, len(ace_rows), len(dtl_rows))
    return {
        "success": True, "rrn": rrn, "environment": environment, "range": period,
        "summary": {"ace_records": len(ace_rows), "dtl_records": len(dtl_rows)},
        "services": _services(ace_rows), "audit_timeline": dtl_rows,
    }
