import time
import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.api.routers.analytics import router as analytics_router
from app.api.routers.auth import router as auth_router
from app.api.routers.ingest import router as ingest_router
from app.config import get_settings
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


@app.get("/metrics")
def metrics():
    return PlainTextResponse(generate_latest().decode("utf-8"), media_type=CONTENT_TYPE_LATEST)


app.include_router(auth_router)
app.include_router(ingest_router)
app.include_router(analytics_router)
