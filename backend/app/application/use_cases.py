from __future__ import annotations

from datetime import date, timedelta

from app.application.dtos import (
    DayAggregateDTO,
    DriftSignalDTO,
    FailureRiskDTO,
    ForecastDTO,
    InsightDTO,
    KPIOverviewDTO,
    MachineHealthScoreDTO,
    MachineTimeseriesPointDTO,
    ModelMonitoringDTO,
    RecommendationDTO,
    RiskPanelDTO,
    RiskPanelItemDTO,
    ShiftAggregateDTO,
)
from app.application.predictive_engine import PredictiveIntelligenceEngine
from app.domain.services import detect_zscore_anomalies, rolling_forecast
from app.infrastructure.db.models import Anomaly, DailyAggregate
from app.infrastructure.repositories.analytics_repository import AnalyticsRepository


class AnalyticsUseCase:
    SHIFT_PLANNED_PRODUCTION_MINUTES = 8 * 60
    _predictive_engine = PredictiveIntelligenceEngine()
    _predictive_cache_date: date | None = None
    _predictive_cache: dict | None = None

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

    def machine_timeseries(
        self, start: date, end: date, machine_id: str | None = None
    ) -> list[MachineTimeseriesPointDTO]:
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

    def shift_aggregates(
        self, start: date, end: date, machine_id: str | None = None
    ) -> list[ShiftAggregateDTO]:
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
            ForecastDTO(
                machine_id=machine_id,
                metric="downtime",
                values=rolling_forecast(downtime_values, horizon_days),
            ),
            ForecastDTO(
                machine_id=machine_id,
                metric="output",
                values=rolling_forecast(output_values, horizon_days),
            ),
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

    def _predictive_state(self, as_of_date: date) -> dict:
        if self._predictive_cache_date == as_of_date and self._predictive_cache is not None:
            return self._predictive_cache

        start_date = as_of_date - timedelta(days=120)
        shift_start = as_of_date - timedelta(days=30)
        rows = self.repo.get_machine_daily_metrics(start=start_date, end=as_of_date)
        shift_rows = self.repo.get_machine_shift_scrap(start=shift_start, end=as_of_date)

        snapshots = self._predictive_engine.machine_health_scores(rows, shift_rows, as_of_date)
        training_data = self._predictive_engine.build_training_data(rows)
        accuracy, brier = self._predictive_engine.train(training_data, as_of_date)
        risks = self._predictive_engine.infer_machine_risk(snapshots)
        risk_map = {risk.machine_id: risk for risk in risks}
        drift_signals = self._predictive_engine.detect_drift(rows)
        drift_map = {signal.machine_id: signal for signal in drift_signals}

        recommendations: dict[str, list[str]] = {}
        for snapshot in snapshots:
            recommendations[snapshot.machine_id] = self._predictive_engine.recommend(snapshot)

        monitoring = self._predictive_engine.monitoring_snapshot(
            drift_signals=drift_signals,
            accuracy=accuracy,
            brier=brier,
            as_of_date=as_of_date,
        )

        state = {
            "snapshots": snapshots,
            "risk_map": risk_map,
            "drift_map": drift_map,
            "recommendations": recommendations,
            "monitoring": monitoring,
        }
        self.__class__._predictive_cache_date = as_of_date
        self.__class__._predictive_cache = state
        return state

    def machine_health_scores(self, as_of_date: date) -> list[MachineHealthScoreDTO]:
        state = self._predictive_state(as_of_date)
        return [
            MachineHealthScoreDTO(
                machine_id=s.machine_id,
                as_of_date=s.as_of_date,
                rolling_downtime_variance=s.rolling_downtime_variance,
                anomaly_frequency=s.anomaly_frequency,
                output_degradation_trend=s.output_degradation_trend,
                scrap_variance=s.scrap_variance,
                health_score=s.health_score,
            )
            for s in state["snapshots"]
        ]

    def failure_probabilities(self, as_of_date: date) -> list[FailureRiskDTO]:
        state = self._predictive_state(as_of_date)
        risks = sorted(state["risk_map"].values(), key=lambda r: r.failure_probability_next_7_days, reverse=True)
        return [
            FailureRiskDTO(
                machine_id=r.machine_id,
                failure_probability_next_7_days=r.failure_probability_next_7_days,
                confidence_score=r.confidence_score,
            )
            for r in risks
        ]

    def drift_signals(self, as_of_date: date) -> list[DriftSignalDTO]:
        state = self._predictive_state(as_of_date)
        return [
            DriftSignalDTO(
                machine_id=signal.machine_id,
                concept_drift_score=signal.concept_drift_score,
                concept_drift_detected=signal.concept_drift_detected,
                baseline_deviation_detected=signal.baseline_deviation_detected,
                change_point_detected=signal.change_point_detected,
                change_point_date=signal.change_point_date,
            )
            for signal in state["drift_map"].values()
        ]

    def recommendations(self, as_of_date: date) -> list[RecommendationDTO]:
        state = self._predictive_state(as_of_date)
        return [
            RecommendationDTO(machine_id=machine_id, recommendations=recs)
            for machine_id, recs in sorted(state["recommendations"].items())
        ]

    def risk_panel(self, as_of_date: date) -> RiskPanelDTO:
        state = self._predictive_state(as_of_date)
        scored_rows: list[tuple[str, float, float, float, list[str]]] = []

        for snapshot in state["snapshots"]:
            risk = state["risk_map"].get(snapshot.machine_id)
            probability = risk.failure_probability_next_7_days if risk else snapshot.health_score / 100.0
            confidence = risk.confidence_score if risk else 50.0
            risk_score = min(100.0, (0.55 * snapshot.health_score) + (0.45 * probability * 100.0))
            recs = state["recommendations"].get(snapshot.machine_id, [])
            scored_rows.append((snapshot.machine_id, risk_score, probability, confidence, recs))

        scored_rows.sort(key=lambda row: row[1], reverse=True)
        top = scored_rows[:5]

        items = [
            RiskPanelItemDTO(
                machine_id=row[0],
                risk_score=round(row[1], 2),
                failure_probability_next_7_days=round(row[2], 4),
                confidence_score=round(row[3], 2),
                maintenance_urgency_rank=idx + 1,
                recommendations=row[4],
            )
            for idx, row in enumerate(top)
        ]

        return RiskPanelDTO(as_of_date=as_of_date, top_risk_machines=items)

    def model_monitoring(self, as_of_date: date) -> ModelMonitoringDTO:
        state = self._predictive_state(as_of_date)
        monitor = state["monitoring"]
        return ModelMonitoringDTO(
            model_accuracy=monitor.model_accuracy,
            brier_score=monitor.brier_score,
            tracked_drift_machines=monitor.tracked_drift_machines,
            retrain_recommended_on=monitor.retrain_recommended_on,
            last_trained_on=monitor.last_trained_on,
        )
