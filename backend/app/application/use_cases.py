from datetime import date

from app.application.dtos import ForecastDTO, InsightDTO, KPIOverviewDTO
from app.domain.services import detect_zscore_anomalies, rolling_forecast
from app.infrastructure.db.models import Anomaly, DailyAggregate
from app.infrastructure.repositories.analytics_repository import AnalyticsRepository


class AnalyticsUseCase:
    def __init__(self, repo: AnalyticsRepository) -> None:
        self.repo = repo

    def overview(self, report_date: date) -> KPIOverviewDTO:
        downtime, scrap, output = self.repo.get_overview(report_date)
        downtime = downtime or 0
        scrap = scrap or 0
        output = output or 0
        availability = max(0.0, 1 - (downtime / (24 * 60)))
        return KPIOverviewDTO(
            date=report_date,
            availability_proxy=round(availability, 3),
            downtime_minutes=round(downtime, 2),
            scrap_units=round(scrap, 2),
            throughput_units=round(output, 2),
        )

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
        elif overview.scrap_units > 500:
            msg = "Scrap spike detected; review shift handoff quality checks."
        else:
            msg = "Factory performance is stable with no major risk flags."
        return InsightDTO(summary=msg)
