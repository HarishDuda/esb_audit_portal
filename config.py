"""Application configuration. Database secrets are read only from the environment."""
import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class OracleConfig:
    user: str
    password: str
    host: str
    port: int
    service: str


class Config:
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "development-only-change-me")
    MAX_CONTENT_LENGTH = 16 * 1024
    ENVIRONMENTS = tuple(
        item.strip().upper()
        for item in os.getenv("ESB_ENVIRONMENTS", "UAT,PREPROD").split(",")
        if item.strip()
    )

    @classmethod
    def oracle_config(cls, environment: str) -> OracleConfig:
        prefix = environment.upper()
        try:
            port = int(os.getenv(f"{prefix}_DB_PORT", "1521"))
        except ValueError as exc:
            raise ValueError("Database environment is misconfigured") from exc
        values = {
            "user": os.getenv(f"{prefix}_DB_USER", ""),
            "password": os.getenv(f"{prefix}_DB_PASSWORD", ""),
            "host": os.getenv(f"{prefix}_DB_HOST", ""),
            "service": os.getenv(f"{prefix}_DB_SERVICE", ""),
        }
        if not all(values.values()):
            raise ValueError("Database environment is not configured")
        return OracleConfig(port=port, **values)
