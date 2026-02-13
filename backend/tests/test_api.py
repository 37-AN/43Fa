from pathlib import Path

from .conftest import client


def test_upload_and_overview_happy_path():
    file_path = Path("sample_data/sample_shift_a.csv")
    with file_path.open("rb") as f:
        response = client.post(
            "/datasets/upload",
            files={"file": ("sample_shift_a.csv", f, "text/csv")},
        )
    assert response.status_code == 200

    list_resp = client.get("/datasets")
    assert list_resp.status_code == 200
    assert len(list_resp.json()) >= 1

    kpi_resp = client.get("/kpi/overview", params={"date": "2026-01-10"})
    assert kpi_resp.status_code == 200
    assert "availability_proxy" in kpi_resp.json()
