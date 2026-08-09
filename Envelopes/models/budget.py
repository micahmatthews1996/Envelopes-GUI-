from dataclasses import asdict, dataclass
from datetime import date, datetime


@dataclass(slots=True)
class Budget:
    """Represents a spending budget for one category and calendar month."""

    budget_id: str
    category_id: str
    monthly_limit_cents: int
    budget_month: date
    is_archived: bool
    created_at: datetime
    updated_at: datetime
    origin: str = "manual"

    def to_dictionary(self) -> dict[str, object]:
        budget_data = asdict(self)
        budget_data["budget_month"] = self.budget_month.isoformat()
        budget_data["created_at"] = self.created_at.isoformat()
        budget_data["updated_at"] = self.updated_at.isoformat()
        return budget_data

    @classmethod
    def from_dictionary(cls, budget_data: dict[str, object]) -> "Budget":
        # Legacy GUI budgets had no month. Migrate them to the month in
        # which they were created (or the current month as a fallback).
        stored_month = budget_data.get("budget_month")
        if stored_month:
            parsed = date.fromisoformat(str(stored_month))
            budget_month = date(parsed.year, parsed.month, 1)
        else:
            created = datetime.fromisoformat(str(budget_data["created_at"]))
            budget_month = date(created.year, created.month, 1)

        return cls(
            budget_id=str(budget_data["budget_id"]),
            category_id=str(budget_data["category_id"]),
            monthly_limit_cents=int(budget_data["monthly_limit_cents"]),
            budget_month=budget_month,
            is_archived=bool(budget_data.get("is_archived", False)),
            created_at=datetime.fromisoformat(str(budget_data["created_at"])),
            updated_at=datetime.fromisoformat(str(budget_data["updated_at"])),
            origin=str(budget_data.get("origin", "manual")),
        )
