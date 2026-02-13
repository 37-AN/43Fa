from datetime import date, datetime

from pydantic import BaseModel


class DatasetOut(BaseModel):
    id: int
    name: str
    uploaded_at: datetime
    row_count: int


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserLogin(BaseModel):
    username: str
    password: str


class AnomalyOut(BaseModel):
    report_date: date
    machine_code: str
    metric: str
    value: float
    severity: str
    insight: str
