from datetime import datetime

import pandas as pd
from sqlalchemy.orm import Session

from app.infrastructure.db.models import Dataset, Machine, Operator, ProductionRecord


class IngestRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def _get_or_create_machine(self, code: str) -> Machine:
        machine = self.db.query(Machine).filter_by(machine_code=code).first()
        if machine:
            return machine
        machine = Machine(machine_code=code)
        self.db.add(machine)
        self.db.flush()
        return machine

    def _get_or_create_operator(self, code: str) -> Operator:
        operator = self.db.query(Operator).filter_by(operator_code=code).first()
        if operator:
            return operator
        operator = Operator(operator_code=code)
        self.db.add(operator)
        self.db.flush()
        return operator

    def ingest_dataframe(self, name: str, df: pd.DataFrame) -> Dataset:
        dataset = Dataset(name=name, row_count=len(df))
        self.db.add(dataset)
        self.db.flush()
        for row in df.to_dict("records"):
            timestamp = pd.to_datetime(row["timestamp"]).to_pydatetime()
            machine = self._get_or_create_machine(str(row["machine_id"]))
            operator = self._get_or_create_operator(str(row["operator_id"]))
            self.db.add(
                ProductionRecord(
                    dataset_id=dataset.id,
                    machine_id=machine.id,
                    operator_id=operator.id,
                    shift=str(row["shift"]),
                    timestamp=timestamp,
                    report_date=timestamp.date(),
                    downtime_minutes=float(row["downtime"]),
                    scrap_units=float(row["scrap"]),
                    output_units=float(row["output"]),
                )
            )
        self.db.commit()
        self.db.refresh(dataset)
        return dataset

    def list_datasets(self) -> list[Dataset]:
        return self.db.query(Dataset).order_by(Dataset.uploaded_at.desc()).all()
