from datetime import datetime

import pytest
from sqlalchemy import text

from app.infrastructure.connectors.mssql_connector import MSSQLConnector


def _seed_sqlite(connector: MSSQLConnector) -> None:
    with connector._engine.begin() as connection:
        connection.execute(
            text(
                """
                CREATE TABLE production_events (
                    event_time TEXT,
                    machine_code TEXT,
                    operator_code TEXT,
                    shift_code TEXT,
                    downtime_minutes REAL,
                    scrap_units REAL,
                    output_units REAL
                )
                """
            )
        )
        connection.execute(
            text(
                """
                CREATE TABLE machine_master (
                    machine_code TEXT,
                    machine_name TEXT,
                    line_code TEXT,
                    status TEXT
                )
                """
            )
        )
        connection.execute(
            text(
                """
                CREATE TABLE shift_schedule (
                    shift_code TEXT,
                    shift_name TEXT,
                    start_time TEXT,
                    end_time TEXT
                )
                """
            )
        )

        connection.execute(
            text(
                """
                INSERT INTO production_events VALUES
                    ('2026-01-01 08:00:00', 'M-100', 'OP-1', 'A', 10.0, 1.0, 100.0),
                    ('2026-01-01 09:00:00', 'M-200', 'OP-2', 'A', 5.0, 0.0, 120.0)
                """
            )
        )
        connection.execute(
            text("INSERT INTO machine_master VALUES ('M-100', 'Press 1', 'LINE-1', 'RUNNING')")
        )
        connection.execute(
            text("INSERT INTO shift_schedule VALUES ('A', 'Morning', '06:00:00', '14:00:00')")
        )


def test_mssql_connector_read_methods() -> None:
    connector = MSSQLConnector(database_url="sqlite+pysqlite:///:memory:")
    _seed_sqlite(connector)

    assert connector.test_connection() is True

    rows = connector.fetch_incremental_production_rows(datetime(2026, 1, 1, 8, 30, 0))
    assert len(rows) == 1
    assert rows[0]["machine_code"] == "M-200"

    machines = connector.fetch_machine_master()
    assert machines[0]["machine_code"] == "M-100"

    shifts = connector.fetch_shift_data()
    assert shifts[0]["shift_code"] == "A"


def test_mssql_connector_blocks_non_select_query() -> None:
    connector = MSSQLConnector(database_url="sqlite+pysqlite:///:memory:")

    with pytest.raises(ValueError, match="Only SELECT queries"):
        connector._run_select_query("DELETE FROM production_events")
