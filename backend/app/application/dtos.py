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
