import json
from datetime import date
from pathlib import Path

from models.budget_rollover_record import BudgetRolloverRecord


class JsonBudgetRolloverRepository:
    """Stores the audit ledger for completed budget rollover decisions."""

    def __init__(self, file_path: Path) -> None:
        self._file_path = file_path
        if not self._file_path.exists():
            self._write_records([])

    def get_all(self) -> list[BudgetRolloverRecord]:
        with open(self._file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        return [
            BudgetRolloverRecord.from_dictionary(item)
            for item in data
        ]

    def get_processed(
        self,
        source_budget_id: str,
        destination_month: date,
    ) -> BudgetRolloverRecord | None:
        for record in self.get_all():
            if (
                record.source_budget_id == source_budget_id
                and record.destination_month.year == destination_month.year
                and record.destination_month.month == destination_month.month
            ):
                return record
        return None

    def add(self, record: BudgetRolloverRecord) -> None:
        if self.get_processed(
            record.source_budget_id,
            record.destination_month,
        ) is not None:
            raise ValueError(
                "This budget rollover has already been processed "
                "for the destination month."
            )
        records = self.get_all()
        records.append(record)
        self._write_records(records)

    def _write_records(
        self,
        records: list[BudgetRolloverRecord],
    ) -> None:
        self._file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._file_path, "w", encoding="utf-8") as file:
            json.dump(
                [record.to_dictionary() for record in records],
                file,
                indent=4,
            )
