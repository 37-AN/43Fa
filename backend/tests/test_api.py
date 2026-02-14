from pathlib import Path

from app.infrastructure.db.models import DailyAggregate, Dataset, ProductionRecord

from .conftest import TestingSessionLocal, client


def reset_ingest_tables() -> None:
    db = TestingSessionLocal()
    db.query(DailyAggregate).delete()
    db.query(ProductionRecord).delete()
    db.query(Dataset).delete()
    db.commit()
    db.close()


def get_token(username: str = "admin", password: str = "admin123") -> str:
    resp = client.post("/auth/login", json={"username": username, "password": password})
    assert resp.status_code == 200
    return resp.json()["access_token"]


def upload_sample_csv(name: str = "sample_shift_a.csv") -> None:
    token = get_token()
    file_path = Path(__file__).resolve().parents[1] / "sample_data" / name
    with file_path.open("rb") as f:
        response = client.post(
            "/datasets/upload",
            files={"file": (name, f, "text/csv")},
            headers={"Authorization": f"Bearer {token}"},
        )
    assert response.status_code == 200


def test_login_upload_and_overview_returns_new_kpis():
    reset_ingest_tables()
    upload_sample_csv("sample_shift_a.csv")

    kpi_resp = client.get("/kpi/overview", params={"date": "2026-01-10"})
    assert kpi_resp.status_code == 200
    payload = kpi_resp.json()

    assert payload["availability_percent"] == 88.68
    assert payload["scrap_percent"] == 4.58
    assert payload["throughput_units"] == 1465.0
    assert payload["downtime_minutes"] == 127.0
    assert payload["oee_proxy"] == 84.62


def test_machine_kpi_supports_date_range_and_machine_filter():
    reset_ingest_tables()
    upload_sample_csv("sample_shift_b.csv")

    all_rows = client.get("/kpi/machines", params={"from": "2026-01-10", "to": "2026-01-10"})
    assert all_rows.status_code == 200
    assert len(all_rows.json()) >= 3

    filtered = client.get(
        "/kpi/machines",
        params={"from": "2026-01-10", "to": "2026-01-10", "machine_id": "M-100"},
    )
    assert filtered.status_code == 200
    rows = filtered.json()
    assert len(rows) == 1
    assert rows[0]["machine_id"] == "M-100"
    assert rows[0]["date"] == "2026-01-10"
