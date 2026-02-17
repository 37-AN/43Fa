import time
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import text

from app.config import get_settings
from app.infrastructure.db.session import engine


def write_heartbeat(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(datetime.now(timezone.utc).isoformat(), encoding="utf-8")


def run_worker() -> None:
    settings = get_settings()
    heartbeat = Path(settings.worker_heartbeat_file)
    last_analytics = 0.0

    while True:
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            write_heartbeat(heartbeat)
            now = time.time()
            if now - last_analytics >= settings.worker_analytics_interval_seconds:
                # Placeholder for periodic analytics jobs in OT-safe mode.
                last_analytics = now
        except Exception as exc:
            # Keep process alive; readiness endpoint will report worker/database issues.
            heartbeat.parent.mkdir(parents=True, exist_ok=True)
            (heartbeat.parent / "worker_error").write_text(exc.__class__.__name__, encoding="utf-8")
        time.sleep(settings.worker_heartbeat_interval_seconds)


if __name__ == "__main__":
    run_worker()
