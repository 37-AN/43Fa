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
            func.count(DailyAggregate.id),
        ).where(DailyAggregate.report_date == report_date)
        return self.db.execute(stmt).one()

    def get_machine_timeseries(self, start: date, end: date, machine_id: str | None = None):
        scrap_percent_expr = (func.sum(DailyAggregate.scrap_units) * 100.0) / func.nullif(
            func.sum(DailyAggregate.scrap_units + DailyAggregate.output_units),
            0,
        )
        stmt = (
            select(
                DailyAggregate.report_date,
                DailyAggregate.machine_code,
                func.sum(DailyAggregate.downtime_minutes),
                func.sum(DailyAggregate.output_units),
                scrap_percent_expr,
            )
            .where(and_(DailyAggregate.report_date >= start, DailyAggregate.report_date <= end))
        )
        if machine_id:
            stmt = stmt.where(DailyAggregate.machine_code == machine_id)

        stmt = (
            stmt.group_by(DailyAggregate.report_date, DailyAggregate.machine_code)
            .order_by(DailyAggregate.report_date, DailyAggregate.machine_code)
        )

        return [
            dict(
                date=r[0],
                machine_id=r[1],
                downtime_minutes=r[2] or 0.0,
                throughput_units=r[3] or 0.0,
                scrap_percent=r[4] or 0.0,
            )
            for r in self.db.execute(stmt)
        ]

    def get_shift_aggregates(self, start: date, end: date, machine_id: str | None = None):
        scrap_percent_expr = (func.sum(DailyAggregate.scrap_units) * 100.0) / func.nullif(
            func.sum(DailyAggregate.scrap_units + DailyAggregate.output_units),
            0,
        )
        stmt = (
            select(
                DailyAggregate.report_date,
                DailyAggregate.shift,
                DailyAggregate.machine_code,
                func.sum(DailyAggregate.downtime_minutes),
                func.sum(DailyAggregate.output_units),
                scrap_percent_expr,
            )
            .where(and_(DailyAggregate.report_date >= start, DailyAggregate.report_date <= end))
        )
        if machine_id:
            stmt = stmt.where(DailyAggregate.machine_code == machine_id)

        stmt = (
            stmt.group_by(DailyAggregate.report_date, DailyAggregate.shift, DailyAggregate.machine_code)
            .order_by(DailyAggregate.report_date, DailyAggregate.shift, DailyAggregate.machine_code)
        )
        return [
            dict(
                date=r[0],
                shift=r[1],
                machine_id=r[2],
                downtime_minutes=r[3] or 0.0,
                throughput_units=r[4] or 0.0,
                scrap_percent=r[5] or 0.0,
            )
            for r in self.db.execute(stmt)
        ]

    def get_day_aggregates(self, start: date, end: date, machine_id: str | None = None):
        scrap_percent_expr = (func.sum(DailyAggregate.scrap_units) * 100.0) / func.nullif(
            func.sum(DailyAggregate.scrap_units + DailyAggregate.output_units),
            0,
        )
        stmt = (
            select(
                DailyAggregate.report_date,
                func.sum(DailyAggregate.downtime_minutes),
                func.sum(DailyAggregate.output_units),
                scrap_percent_expr,
            )
            .where(and_(DailyAggregate.report_date >= start, DailyAggregate.report_date <= end))
        )
        if machine_id:
            stmt = stmt.where(DailyAggregate.machine_code == machine_id)

        stmt = stmt.group_by(DailyAggregate.report_date).order_by(DailyAggregate.report_date)
        return [
            dict(
                date=r[0],
                downtime_minutes=r[1] or 0.0,
                throughput_units=r[2] or 0.0,
                scrap_percent=r[3] or 0.0,
            )
            for r in self.db.execute(stmt)
        ]

    def list_anomalies(self, start: date, end: date, severity: str | None, limit: int, offset: int):
        query = self.db.query(Anomaly).filter(and_(Anomaly.report_date >= start, Anomaly.report_date <= end))
        if severity:
            query = query.filter(Anomaly.severity == severity)
        return query.order_by(Anomaly.report_date.desc()).limit(limit).offset(offset).all()
