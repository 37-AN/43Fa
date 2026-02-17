import shutil
import time
from pathlib import Path

import httpx

from app.config import get_settings


def authenticate(client: httpx.Client, base_url: str, username: str, password: str) -> str:
    resp = client.post(
        f"{base_url}/auth/login",
        json={"username": username, "password": password},
        timeout=20.0,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def upload_csv(client: httpx.Client, base_url: str, token: str, csv_path: Path) -> None:
    with csv_path.open("rb") as handle:
        resp = client.post(
            f"{base_url}/datasets/upload",
            files={"file": (csv_path.name, handle, "text/csv")},
            headers={"Authorization": f"Bearer {token}"},
            timeout=120.0,
        )
    resp.raise_for_status()


def run_collector() -> None:
    settings = get_settings()
    input_dir = Path(settings.collector_input_dir)
    archive_dir = Path(settings.collector_archive_dir)
    error_dir = Path(settings.collector_error_dir)

    input_dir.mkdir(parents=True, exist_ok=True)
    archive_dir.mkdir(parents=True, exist_ok=True)
    error_dir.mkdir(parents=True, exist_ok=True)

    with httpx.Client() as client:
        token = ""
        while True:
            for csv_path in sorted(input_dir.glob("*.csv")):
                try:
                    if not token:
                        token = authenticate(
                            client,
                            settings.collector_api_url,
                            settings.collector_admin_username,
                            settings.collector_admin_password,
                        )
                    upload_csv(client, settings.collector_api_url, token, csv_path)
                    shutil.move(str(csv_path), archive_dir / csv_path.name)
                except Exception:
                    token = ""
                    shutil.move(str(csv_path), error_dir / csv_path.name)
            time.sleep(settings.collector_poll_seconds)


if __name__ == "__main__":
    run_collector()
