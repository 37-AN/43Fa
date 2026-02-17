import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from sqlalchemy import text
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.api.routers.analytics import router as analytics_router
from app.api.routers.auth import router as auth_router
from app.api.routers.ingest import router as ingest_router
from app.config import get_settings
from app.infrastructure.db.session import engine
from app.infrastructure.logging.logger import setup_logging
from app.infrastructure.metrics.prometheus import request_counter

settings = get_settings()
limiter = Limiter(key_func=get_remote_address, default_limits=[settings.rate_limit])
setup_logging()

app = FastAPI(title="ShadowPlant AI", version="0.1.0")
app.state.limiter = limiter
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    req_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    start = time.time()
    response = await call_next(request)
    response.headers["X-Request-ID"] = req_id
    request_counter.labels(request.method, request.url.path, str(response.status_code)).inc()
    response.headers["X-Process-Time"] = str(round(time.time() - start, 5))
    return response


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/healthz", tags=["health"])
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/readyz", tags=["health"])
def readyz() -> dict:
    checks = {"db": "down", "migrations": "pending", "worker": "stale"}
    errors: list[str] = []
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            checks["db"] = "ok"
            row = conn.execute(text("SELECT version_num FROM alembic_version LIMIT 1")).scalar_one_or_none()
            if row is None:
                errors.append("alembic_version_missing")
            elif row != settings.expected_alembic_revision:
                errors.append(
                    f"alembic_version_mismatch(expected={settings.expected_alembic_revision},found={row})"
                )
            else:
                checks["migrations"] = "ok"
    except Exception as exc:
        errors.append(f"db_error:{exc.__class__.__name__}")

    heartbeat_path = Path(settings.worker_heartbeat_file)
    if heartbeat_path.exists():
        age_seconds = time.time() - heartbeat_path.stat().st_mtime
        if age_seconds <= settings.worker_heartbeat_ttl_seconds:
            checks["worker"] = "ok"
        else:
            errors.append(f"worker_heartbeat_stale:{int(age_seconds)}s")
    else:
        errors.append("worker_heartbeat_missing")

    ready = checks["db"] == "ok" and checks["migrations"] == "ok" and checks["worker"] == "ok"
    payload = {
        "status": "ready" if ready else "not_ready",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
        "errors": errors,
    }
    if not ready:
        raise HTTPException(status_code=503, detail=payload)
    return payload


@app.get("/metrics")
def metrics():
    return PlainTextResponse(generate_latest().decode("utf-8"), media_type=CONTENT_TYPE_LATEST)


app.include_router(auth_router)
app.include_router(ingest_router)
app.include_router(analytics_router)
