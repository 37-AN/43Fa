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


def test_risk_panel_and_monitoring_endpoints():
    reset_ingest_tables()
    upload_sample_csv("sample_shift_a.csv")
    upload_sample_csv("sample_shift_b.csv")

    panel_resp = client.get("/risk/panel", params={"date": "2026-01-10"})
    assert panel_resp.status_code == 200
    panel = panel_resp.json()

    assert panel["as_of_date"] == "2026-01-10"
    assert "top_risk_machines" in panel
    assert len(panel["top_risk_machines"]) >= 1
    assert len(panel["top_risk_machines"]) <= 5

    top_row = panel["top_risk_machines"][0]
    assert "machine_id" in top_row
    assert "risk_score" in top_row
    assert "failure_probability_next_7_days" in top_row
    assert "maintenance_urgency_rank" in top_row
    assert isinstance(top_row["recommendations"], list)

    monitor_resp = client.get("/risk/model-monitoring", params={"date": "2026-01-10"})
    assert monitor_resp.status_code == 200
    monitor = monitor_resp.json()
    assert "model_accuracy" in monitor
    assert "brier_score" in monitor
    assert "tracked_drift_machines" in monitor
    assert monitor["last_trained_on"] == "2026-01-10"
