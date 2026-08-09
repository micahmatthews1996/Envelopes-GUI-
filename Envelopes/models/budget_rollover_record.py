from dataclasses import asdict, dataclass
from datetime import date, datetime


@dataclass(slots=True)
class BudgetRolloverRecord:
    """Records one completed rollover decision for one source budget."""

    rollover_id: str
    source_budget_id: str
    source_month: date
    destination_month: date
    amount_cents: int
    destination_type: str
    goal_id: str
    result_id: str
    created_at: datetime

    def to_dictionary(self) -> dict[str, object]:
        data = asdict(self)
        data["source_month"] = self.source_month.isoformat()
        data["destination_month"] = self.destination_month.isoformat()
        data["created_at"] = self.created_at.isoformat()
        return data

    @classmethod
    def from_dictionary(
        cls,
        data: dict[str, object],
    ) -> "BudgetRolloverRecord":
        return cls(
            rollover_id=str(data["rollover_id"]),
            source_budget_id=str(data["source_budget_id"]),
            source_month=date.fromisoformat(str(data["source_month"])),
            destination_month=date.fromisoformat(str(data["destination_month"])),
            amount_cents=int(data["amount_cents"]),
            destination_type=str(data["destination_type"]),
            goal_id=str(data.get("goal_id", "")),
            result_id=str(data.get("result_id", "")),
            created_at=datetime.fromisoformat(str(data["created_at"])),
        )
