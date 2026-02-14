from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.schemas.common import AnomalyOut
from app.application.dtos import DayAggregateDTO, KPIOverviewDTO, MachineTimeseriesPointDTO, ShiftAggregateDTO
from app.application.use_cases import AnalyticsUseCase
from app.infrastructure.db.session import get_db
from app.infrastructure.repositories.analytics_repository import AnalyticsRepository

router = APIRouter(tags=["analytics"])


@router.get("/kpi/overview", response_model=KPIOverviewDTO)
def kpi_overview(date: date, db: Session = Depends(get_db)):
    return AnalyticsUseCase(AnalyticsRepository(db)).overview(date)


@router.get("/kpi/machines", response_model=list[MachineTimeseriesPointDTO])
def machine_kpis(
    from_date: date = Query(alias="from"),
    to_date: date = Query(alias="to"),
    machine_id: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    use_case = AnalyticsUseCase(AnalyticsRepository(db))
    return use_case.machine_timeseries(start=from_date, end=to_date, machine_id=machine_id)


@router.get("/kpi/shifts", response_model=list[ShiftAggregateDTO])
def shift_kpis(
    from_date: date = Query(alias="from"),
    to_date: date = Query(alias="to"),
    machine_id: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    use_case = AnalyticsUseCase(AnalyticsRepository(db))
    return use_case.shift_aggregates(start=from_date, end=to_date, machine_id=machine_id)


@router.get("/kpi/days", response_model=list[DayAggregateDTO])
def day_kpis(
    from_date: date = Query(alias="from"),
    to_date: date = Query(alias="to"),
    machine_id: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    use_case = AnalyticsUseCase(AnalyticsRepository(db))
    return use_case.day_aggregates(start=from_date, end=to_date, machine_id=machine_id)


@router.get("/anomalies", response_model=list[AnomalyOut])
def anomalies(
    from_date: date = Query(alias="from"),
    to_date: date = Query(alias="to"),
    severity: str | None = None,
    limit: int = Query(default=50, le=200),
    offset: int = 0,
    db: Session = Depends(get_db),
):
    use_case = AnalyticsUseCase(AnalyticsRepository(db))
    use_case.detect_anomalies()
    rows = AnalyticsRepository(db).list_anomalies(from_date, to_date, severity, limit, offset)
    return rows


@router.get("/forecasts")
def forecasts(machine_id: str, horizon_days: int = Query(default=1, ge=1, le=7), db: Session = Depends(get_db)):
    return AnalyticsUseCase(AnalyticsRepository(db)).forecast(machine_id, horizon_days)


@router.get("/insights")
def insights(date: date, db: Session = Depends(get_db)):
    return AnalyticsUseCase(AnalyticsRepository(db)).insights(date)
