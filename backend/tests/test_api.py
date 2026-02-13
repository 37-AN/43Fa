from pathlib import Path

from .conftest import client


def test_upload_and_overview_happy_path():
def get_token(username: str = "admin", password: str = "admin123") -> str:
    resp = client.post("/auth/login", json={"username": username, "password": password})
    assert resp.status_code == 200
    return resp.json()["access_token"]


def test_login_and_upload_and_overview_happy_path():
    token = get_token()
    file_path = Path("sample_data/sample_shift_a.csv")
    with file_path.open("rb") as f:
        response = client.post(
            "/datasets/upload",
            files={"file": ("sample_shift_a.csv", f, "text/csv")},
            headers={"Authorization": f"Bearer {token}"},
        )
    assert response.status_code == 200

    list_resp = client.get("/datasets")
    assert list_resp.status_code == 200
    assert len(list_resp.json()) >= 1

    kpi_resp = client.get("/kpi/overview", params={"date": "2026-01-10"})
    assert kpi_resp.status_code == 200
    assert "availability_proxy" in kpi_resp.json()
