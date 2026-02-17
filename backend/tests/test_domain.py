from datetime import date

from app.domain.services import detect_zscore_anomalies


def test_detect_anomaly_flags_outlier():
    records = [
        {"report_date": date(2026, 1, i + 1), "machine_id": "M-1", "downtime": v}
        for i, v in enumerate([10, 11, 12, 10, 200])
    ]
    anomalies = detect_zscore_anomalies(records, "downtime", z_threshold=1.5)
    assert anomalies
    assert anomalies[0].severity in {"medium", "high"}
