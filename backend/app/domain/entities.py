from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class KPIOverview:
    report_date: date
    availability_proxy: float
    downtime_minutes: float
    scrap_units: float
    throughput_units: float


@dataclass(frozen=True)
class AnomalyResult:
    machine_id: str
    metric: str
    value: float
    baseline: float
    z_score: float
    severity: str
    report_date: date
