from __future__ import annotations

from collections.abc import Iterable
from statistics import mean, pstdev

from app.domain.entities import AnomalyResult


def detect_zscore_anomalies(data: Iterable[dict], metric: str, z_threshold: float = 2.0) -> list[AnomalyResult]:
    records = list(data)
    if len(records) < 5:
        return []
    values = [float(r[metric]) for r in records]
    mu = mean(values)
    sigma = pstdev(values) or 1.0
    results: list[AnomalyResult] = []
    for r in records:
        value = float(r[metric])
        z_score = (value - mu) / sigma
        if abs(z_score) >= z_threshold:
            severity = "high" if abs(z_score) >= 3 else "medium"
            results.append(
                AnomalyResult(
                    machine_id=r["machine_id"],
                    metric=metric,
                    value=value,
                    baseline=mu,
                    z_score=z_score,
                    severity=severity,
                    report_date=r["report_date"],
                )
            )
    return results


def rolling_forecast(values: list[float], horizon_days: int = 1) -> list[float]:
    if not values:
        return [0.0] * horizon_days
    window = values[-7:] if len(values) >= 7 else values
    baseline = sum(window) / len(window)
    trend = (window[-1] - window[0]) / max(len(window) - 1, 1)
    return [max(0.0, baseline + trend * (i + 1)) for i in range(horizon_days)]
