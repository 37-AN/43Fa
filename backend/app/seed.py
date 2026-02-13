from datetime import datetime, timedelta
import random

import pandas as pd

from app.infrastructure.db.session import SessionLocal
from app.infrastructure.repositories.ingest_repository import IngestRepository
from app.infrastructure.repositories.analytics_repository import AnalyticsRepository


def generate_data(days: int = 180) -> pd.DataFrame:
    base = datetime.utcnow() - timedelta(days=days)
    rows = []
    for d in range(days):
        for machine in ["M-100", "M-200", "M-300", "M-400"]:
            for shift in ["A", "B", "C"]:
                ts = base + timedelta(days=d, hours=random.choice([0, 8, 16]))
                rows.append(
                    {
                        "timestamp": ts.isoformat(),
                        "machine_id": machine,
                        "operator_id": f"OP-{random.randint(1,20):02d}",
                        "shift": shift,
                        "downtime": max(0, random.gauss(45, 18) + (40 if random.random() < 0.03 else 0)),
                        "scrap": max(0, random.gauss(25, 10) + (35 if random.random() < 0.04 else 0)),
                        "output": max(10, random.gauss(500, 60) - (80 if random.random() < 0.03 else 0)),
                    }
                )
    return pd.DataFrame(rows)


def seed() -> None:
    db = SessionLocal()
    try:
        df = generate_data()
        IngestRepository(db).ingest_dataframe("synthetic_seed.csv", df)
        AnalyticsRepository(db).recompute_daily_aggregates()
    finally:
        db.close()


if __name__ == "__main__":
    seed()
