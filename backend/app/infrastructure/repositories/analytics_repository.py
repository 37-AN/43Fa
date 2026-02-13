from datetime import date

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.infrastructure.db.models import Anomaly, DailyAggregate, Machine, ProductionRecord


class AnalyticsRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def recompute_daily_aggregates(self) -> None:
        self.db.query(DailyAggregate).delete()
        stmt = (
            select(
                ProductionRecord.report_date,
                Machine.machine_code,
                ProductionRecord.shift,
                func.sum(ProductionRecord.downtime_minutes),
                func.sum(ProductionRecord.scrap_units),
                func.sum(ProductionRecord.output_units),
            )
            .join(Machine, Machine.id == ProductionRecord.machine_id)
            .group_by(ProductionRecord.report_date, Machine.machine_code, ProductionRecord.shift)
        )
        for row in self.db.execute(stmt):
            self.db.add(
                DailyAggregate(
                    report_date=row[0],
                    machine_code=row[1],
                    shift=row[2],
                    downtime_minutes=row[3],
                    scrap_units=row[4],
                    output_units=row[5],
                )
            )
        self.db.commit()

    def get_overview(self, report_date: date):
        stmt = select(
            func.sum(DailyAggregate.downtime_minutes),
            func.sum(DailyAggregate.scrap_units),
            func.sum(DailyAggregate.output_units),
        ).where(DailyAggregate.report_date == report_date)
        return self.db.execute(stmt).one()

    def get_machine_timeseries(self, start: date, end: date):
        stmt = (
            select(
                DailyAggregate.report_date,
                DailyAggregate.machine_code,
                func.sum(DailyAggregate.output_units),
                func.sum(DailyAggregate.downtime_minutes),
                func.sum(DailyAggregate.scrap_units),
            )
            .where(and_(DailyAggregate.report_date >= start, DailyAggregate.report_date <= end))
            .group_by(DailyAggregate.report_date, DailyAggregate.machine_code)
            .order_by(DailyAggregate.report_date)
        )
        return [dict(report_date=r[0], machine_id=r[1], output=r[2], downtime=r[3], scrap=r[4]) for r in self.db.execute(stmt)]

    def list_anomalies(self, start: date, end: date, severity: str | None, limit: int, offset: int):
        query = self.db.query(Anomaly).filter(and_(Anomaly.report_date >= start, Anomaly.report_date <= end))
        if severity:
            query = query.filter(Anomaly.severity == severity)
        return query.order_by(Anomaly.report_date.desc()).limit(limit).offset(offset).all()
