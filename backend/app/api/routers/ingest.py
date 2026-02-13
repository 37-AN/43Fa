from io import BytesIO

import pandas as pd
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.schemas.common import DatasetOut
from app.config import get_settings
from app.infrastructure.metrics.prometheus import upload_counter
from app.infrastructure.db.session import get_db
from app.infrastructure.repositories.analytics_repository import AnalyticsRepository
from app.infrastructure.repositories.ingest_repository import IngestRepository

router = APIRouter(prefix="/datasets", tags=["datasets"])
settings = get_settings()
REQUIRED_COLUMNS = {"downtime", "scrap", "output", "shift", "machine_id", "operator_id", "timestamp"}


@router.post("/upload", response_model=DatasetOut)
def upload_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> DatasetOut:
    content = file.file.read()
    if len(content) > settings.max_upload_size_mb * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large")
    try:
        df = pd.read_csv(BytesIO(content))
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid CSV") from exc
    if not REQUIRED_COLUMNS.issubset(df.columns):
        raise HTTPException(status_code=400, detail="Missing required columns")
    if len(df) > settings.max_upload_rows:
        raise HTTPException(status_code=400, detail="Row limit exceeded")
    ingest_repo = IngestRepository(db)
    dataset = ingest_repo.ingest_dataframe(file.filename or "upload.csv", df)
    AnalyticsRepository(db).recompute_daily_aggregates()
    upload_counter.inc()
    return DatasetOut.model_validate(dataset, from_attributes=True)


@router.get("", response_model=list[DatasetOut])
def list_datasets(db: Session = Depends(get_db)) -> list[DatasetOut]:
    rows = IngestRepository(db).list_datasets()
    return [DatasetOut.model_validate(row, from_attributes=True) for row in rows]
