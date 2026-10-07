"""Oracle SQL is centralized here so column mappings can be updated after schema verification."""

# ESB ACE records must come from ESB_ACE_AUDIT_LOG; DTL records come from ESB_AUDIT_DTL_LOG.
ACE_TABLE = "ESB_ACE_AUDIT_LOG"
DTL_TABLE = "ESB_AUDIT_DTL_LOG"

ACE_COLUMNS = """
    REQREF_NUMBER, SERVICE_NAME, URL, STATUS, ERROR_SOURCE,
    ERROR_CODE, ERROR_DESC, TIMESTAMP
"""
DTL_COLUMNS = "REQREF_NUMBER, LOG_POINT, PAYLOAD, TIMESTAMP"


def _table_name(schema: str, table: str) -> str:
    return f"{schema}.{table}" if schema else table


def ace_recent(schema: str) -> str:
    return f"""
    SELECT {ACE_COLUMNS}
    FROM {_table_name(schema, ACE_TABLE)}
    WHERE TIMESTAMP >= TRUNC(SYSDATE) - (:days - 1)
      AND TIMESTAMP < TRUNC(SYSDATE) + 1
      AND REQREF_NUMBER = :rrn
    ORDER BY TIMESTAMP ASC
"""


def dtl_recent(schema: str) -> str:
    return f"""
    SELECT {DTL_COLUMNS}
    FROM {_table_name(schema, DTL_TABLE)}
    WHERE TIMESTAMP > (SYSDATE - :days) AND REQREF_NUMBER = :rrn
    ORDER BY TIMESTAMP ASC
"""


def ace_custom(schema: str) -> str:
    return f"""
    SELECT {ACE_COLUMNS}
    FROM {_table_name(schema, ACE_TABLE)}
    WHERE TIMESTAMP >= :from_date AND TIMESTAMP < :to_date
      AND REQREF_NUMBER = :rrn
    ORDER BY TIMESTAMP ASC
"""


def dtl_custom(schema: str) -> str:
    return f"""
    SELECT {DTL_COLUMNS}
    FROM {_table_name(schema, DTL_TABLE)}
    WHERE TIMESTAMP >= :from_date AND TIMESTAMP < :to_date
      AND REQREF_NUMBER = :rrn
    ORDER BY TIMESTAMP ASC
"""
