"""Oracle SQL is centralized here so column mappings can be updated after schema verification."""

# These names reflect the supplied ESB audit schema and should be verified against Oracle.
ACE_COLUMNS = """
    REQREF_NUMBER, SERVICE_NAME, URL, STATUS, ERROR_SOURCE,
    ERROR_CODE, ERROR_DESC, TIMESTAMP
"""
DTL_COLUMNS = "REQREF_NUMBER, LOG_POINT, PAYLOAD, TIMESTAMP"

ACE_RECENT = f"""
    SELECT {ACE_COLUMNS}
    FROM ESB_ACE_AUDIT_LOG
    WHERE TIMESTAMP > (SYSDATE - :days) AND REQREF_NUMBER = :rrn
    ORDER BY TIMESTAMP ASC
"""
DTL_RECENT = f"""
    SELECT {DTL_COLUMNS}
    FROM ESB_AUDIT_DTL_LOG
    WHERE TIMESTAMP > (SYSDATE - :days) AND REQREF_NUMBER = :rrn
    ORDER BY TIMESTAMP ASC
"""
ACE_CUSTOM = f"""
    SELECT {ACE_COLUMNS}
    FROM ESB_ACE_AUDIT_LOG
    WHERE TIMESTAMP >= :from_date AND TIMESTAMP < :to_date
      AND REQREF_NUMBER = :rrn
    ORDER BY TIMESTAMP ASC
"""
DTL_CUSTOM = f"""
    SELECT {DTL_COLUMNS}
    FROM ESB_AUDIT_DTL_LOG
    WHERE TIMESTAMP >= :from_date AND TIMESTAMP < :to_date
      AND REQREF_NUMBER = :rrn
    ORDER BY TIMESTAMP ASC
"""
