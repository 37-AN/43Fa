from datetime import date

from app.application.dtos import DayAggregateDTO, ForecastDTO, InsightDTO, KPIOverviewDTO, MachineTimeseriesPointDTO, ShiftAggregateDTO
from app.domain.services import detect_zscore_anomalies, rolling_forecast
from app.infrastructure.db.models import Anomaly, DailyAggregate
from app.infrastructure.repositories.analytics_repository import AnalyticsRepository


class AnalyticsUseCase:
    SHIFT_PLANNED_PRODUCTION_MINUTES = 8 * 60

    def __init__(self, repo: AnalyticsRepository) -> None:
        self.repo = repo

    def overview(self, report_date: date) -> KPIOverviewDTO:
        downtime, scrap, output, shift_entries = self.repo.get_overview(report_date)
        downtime = downtime or 0
        scrap = scrap or 0
        output = output or 0
        shift_entries = shift_entries or 0
        planned_minutes = max(shift_entries * self.SHIFT_PLANNED_PRODUCTION_MINUTES, 0)

        availability = 0.0
        if planned_minutes > 0:
            availability = max(0.0, (planned_minutes - downtime) / planned_minutes)

        total_units = output + scrap
        scrap_percent = (scrap / total_units) if total_units > 0 else 0.0
        oee_proxy = availability * (1 - scrap_percent)

        return KPIOverviewDTO(
            date=report_date,
            availability_percent=round(availability * 100, 2),
            scrap_percent=round(scrap_percent * 100, 2),
            downtime_minutes=round(downtime, 2),
            throughput_units=round(output, 2),
            oee_proxy=round(oee_proxy * 100, 2),
        )

    def machine_timeseries(self, start: date, end: date, machine_id: str | None = None) -> list[MachineTimeseriesPointDTO]:
        rows = self.repo.get_machine_timeseries(start=start, end=end, machine_id=machine_id)
        return [
            MachineTimeseriesPointDTO(
                date=row["date"],
                machine_id=row["machine_id"],
                downtime_minutes=round(float(row["downtime_minutes"]), 2),
                throughput_units=round(float(row["throughput_units"]), 2),
                scrap_percent=round(float(row["scrap_percent"]), 2),
            )
            for row in rows
        ]

    def shift_aggregates(self, start: date, end: date, machine_id: str | None = None) -> list[ShiftAggregateDTO]:
        rows = self.repo.get_shift_aggregates(start=start, end=end, machine_id=machine_id)
        return [
            ShiftAggregateDTO(
                date=row["date"],
                shift=row["shift"],
                machine_id=row["machine_id"],
                downtime_minutes=round(float(row["downtime_minutes"]), 2),
                throughput_units=round(float(row["throughput_units"]), 2),
                scrap_percent=round(float(row["scrap_percent"]), 2),
            )
            for row in rows
        ]

    def day_aggregates(self, start: date, end: date, machine_id: str | None = None) -> list[DayAggregateDTO]:
        rows = self.repo.get_day_aggregates(start=start, end=end, machine_id=machine_id)
        return [
            DayAggregateDTO(
                date=row["date"],
                downtime_minutes=round(float(row["downtime_minutes"]), 2),
                throughput_units=round(float(row["throughput_units"]), 2),
                scrap_percent=round(float(row["scrap_percent"]), 2),
            )
            for row in rows
        ]

    def detect_anomalies(self) -> int:
        self.repo.db.query(Anomaly).delete()
        rows = self.repo.db.query(DailyAggregate).all()
        data = [
            {
                "report_date": r.report_date,
                "machine_id": r.machine_code,
                "downtime": r.downtime_minutes,
                "scrap": r.scrap_units,
                "output": r.output_units,
            }
            for r in rows
        ]
        anomalies = detect_zscore_anomalies(data, "downtime") + detect_zscore_anomalies(data, "scrap")
        for a in anomalies:
            self.repo.db.add(
                Anomaly(
                    report_date=a.report_date,
                    machine_code=a.machine_id,
                    metric=a.metric,
                    value=a.value,
                    baseline=a.baseline,
                    z_score=a.z_score,
                    severity=a.severity,
                    insight=f"{a.metric} deviated from baseline by {a.z_score:.2f}σ",
                )
            )
        self.repo.db.commit()
        return len(anomalies)

    def forecast(self, machine_id: str, horizon_days: int) -> list[ForecastDTO]:
        rows = (
            self.repo.db.query(DailyAggregate)
            .filter(DailyAggregate.machine_code == machine_id)
            .order_by(DailyAggregate.report_date)
            .all()
        )
        downtime_values = [r.downtime_minutes for r in rows]
        output_values = [r.output_units for r in rows]
        return [
            ForecastDTO(machine_id=machine_id, metric="downtime", values=rolling_forecast(downtime_values, horizon_days)),
            ForecastDTO(machine_id=machine_id, metric="output", values=rolling_forecast(output_values, horizon_days)),
        ]

    def insights(self, report_date: date) -> InsightDTO:
        overview = self.overview(report_date)
        if overview.downtime_minutes > 600:
            msg = "Downtime is elevated; prioritize maintenance on worst-performing assets."
        elif overview.scrap_percent > 8:
            msg = "Scrap spike detected; review shift handoff quality checks."
        else:
            msg = "Factory performance is stable with no major risk flags."
        return InsightDTO(summary=msg)
