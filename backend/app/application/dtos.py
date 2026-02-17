from datetime import date

from pydantic import BaseModel


class KPIOverviewDTO(BaseModel):
    date: date
    availability_percent: float
    scrap_percent: float
    downtime_minutes: float
    throughput_units: float
    oee_proxy: float


class MachineTimeseriesPointDTO(BaseModel):
    date: date
    machine_id: str
    downtime_minutes: float
    throughput_units: float
    scrap_percent: float


class ShiftAggregateDTO(BaseModel):
    date: date
    shift: str
    machine_id: str
    downtime_minutes: float
    throughput_units: float
    scrap_percent: float


class DayAggregateDTO(BaseModel):
    date: date
    downtime_minutes: float
    throughput_units: float
    scrap_percent: float


class ForecastDTO(BaseModel):
    machine_id: str
    metric: str
    values: list[float]


class InsightDTO(BaseModel):
    summary: str


class MachineHealthScoreDTO(BaseModel):
    machine_id: str
    as_of_date: date
    rolling_downtime_variance: float
    anomaly_frequency: float
    output_degradation_trend: float
    scrap_variance: float
    health_score: float


class FailureRiskDTO(BaseModel):
    machine_id: str
    failure_probability_next_7_days: float
    confidence_score: float


class DriftSignalDTO(BaseModel):
    machine_id: str
    concept_drift_score: float
    concept_drift_detected: bool
    baseline_deviation_detected: bool
    change_point_detected: bool
    change_point_date: date | None = None


class RecommendationDTO(BaseModel):
    machine_id: str
    recommendations: list[str]


class RiskPanelItemDTO(BaseModel):
    machine_id: str
    risk_score: float
    failure_probability_next_7_days: float
    confidence_score: float
    maintenance_urgency_rank: int
    recommendations: list[str]


class RiskPanelDTO(BaseModel):
    as_of_date: date
    top_risk_machines: list[RiskPanelItemDTO]


class ModelMonitoringDTO(BaseModel):
    model_accuracy: float
    brier_score: float
    tracked_drift_machines: int
    retrain_recommended_on: date
    last_trained_on: date
