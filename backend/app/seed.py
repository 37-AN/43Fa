from datetime import datetime, timedelta
import random

import pandas as pd

from app.infrastructure.db.session import SessionLocal
from app.infrastructure.security.auth import get_password_hash
from app.infrastructure.db.models import User
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
        # ensure default users exist and use current password hash format
        # (migrate legacy bcrypt hashes if found)
        default_users = [
            ("admin", "admin123", "admin"),
            ("viewer", "viewer123", "viewer"),
        ]
        for username, plain_password, role in default_users:
            user = db.query(User).filter(User.username == username).first()
            if not user:
                db.add(User(username=username, hashed_password=get_password_hash(plain_password), role=role))
            elif user.hashed_password and user.hashed_password.startswith("$2"):
                # migrate legacy bcrypt hash to current format
                user.hashed_password = get_password_hash(plain_password)
                db.add(user)
        db.commit()
        df = generate_data()
        IngestRepository(db).ingest_dataframe("synthetic_seed.csv", df)
        AnalyticsRepository(db).recompute_daily_aggregates()
    finally:
        db.close()


if __name__ == "__main__":
    seed()
