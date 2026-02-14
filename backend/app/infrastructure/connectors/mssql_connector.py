from __future__ import annotations

from datetime import datetime
from typing import Any

import structlog
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from app.config import get_settings

logger = structlog.get_logger(__name__)


class MSSQLConnector:
    """Read-only connector for pulling factory data from Microsoft SQL Server."""

    def __init__(
        self,
        database_url: str,
        production_table: str = "production_events",
        machine_master_table: str = "machine_master",
        shift_table: str = "shift_schedule",
    ) -> None:
        if not database_url:
            raise ValueError("MSSQL database URL must be provided")

        self.database_url = database_url
        self.production_table = production_table
        self.machine_master_table = machine_master_table
        self.shift_table = shift_table
        self._engine: Engine = create_engine(self.database_url, pool_pre_ping=True)

        safe_url = self._engine.url.render_as_string(hide_password=True)
        logger.info("mssql_connector_initialized", database_url=safe_url)

    @classmethod
    def from_settings(cls) -> "MSSQLConnector":
        settings = get_settings()
        if not settings.mssql_database_url:
            raise ValueError("MSSQL_DATABASE_URL is not configured")
        return cls(database_url=settings.mssql_database_url)

    def test_connection(self) -> bool:
        rows = self._run_select_query("SELECT 1 AS healthcheck")
        return len(rows) == 1 and rows[0].get("healthcheck") == 1

    def fetch_incremental_production_rows(self, last_timestamp: datetime) -> list[dict[str, Any]]:
        query = f"""
            SELECT
                event_time,
                machine_code,
                operator_code,
                shift_code,
                downtime_minutes,
                scrap_units,
                output_units
            FROM {self.production_table}
            WHERE event_time > :last_timestamp
            ORDER BY event_time ASC
        """
        return self._run_select_query(query, {"last_timestamp": last_timestamp})

    def fetch_machine_master(self) -> list[dict[str, Any]]:
        query = f"""
            SELECT
                machine_code,
                machine_name,
                line_code,
                status
            FROM {self.machine_master_table}
            ORDER BY machine_code ASC
        """
        return self._run_select_query(query)

    def fetch_shift_data(self) -> list[dict[str, Any]]:
        query = f"""
            SELECT
                shift_code,
                shift_name,
                start_time,
                end_time
            FROM {self.shift_table}
            ORDER BY shift_code ASC
        """
        return self._run_select_query(query)

    def _run_select_query(
        self,
        query: str,
        params: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        normalized_query = query.strip()
        if not normalized_query.lower().startswith("select"):
            raise ValueError("Only SELECT queries are allowed for MSSQL connector")

        logger.info("mssql_read_query", query_template=" ".join(normalized_query.split()))

        with self._engine.connect() as connection:
            result = connection.execute(text(normalized_query), params or {})
            return [dict(row) for row in result.mappings().all()]
