from datetime import date

from pydantic import BaseModel


class KPIOverviewDTO(BaseModel):
    date: date
    availability_proxy: float
    downtime_minutes: float
    scrap_units: float
    throughput_units: float


class ForecastDTO(BaseModel):
    machine_id: str
    metric: str
    values: list[float]


class InsightDTO(BaseModel):
    summary: str
