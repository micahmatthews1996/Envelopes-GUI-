from dataclasses import asdict, dataclass
from datetime import date, datetime


@dataclass(slots=True)
class SavingsGoal:
    """Represents a financial savings goal."""

    goal_id: str
    name: str
    target_amount_cents: int
    current_amount_cents: int
    target_date: date | None
    is_archived: bool
    celebration_shown: bool
    created_at: datetime
    updated_at: datetime

    @property
    def remaining_amount_cents(self) -> int:
        """Return the amount still needed to complete the goal."""

        return max(
            0,
            (
                self.target_amount_cents
                - self.current_amount_cents
            ),
        )

    @property
    def progress_percent(self) -> int:
        """Return goal progress as a percentage from zero to one hundred."""

        if self.target_amount_cents <= 0:
            return 0

        percentage = (
            self.current_amount_cents
            / self.target_amount_cents
            * 100
        )

        return max(
            0,
            min(
                100,
                round(percentage),
            ),
        )

    @property
    def is_completed(self) -> bool:
        """Return whether the goal has reached its target amount."""

        return (
            self.current_amount_cents
            >= self.target_amount_cents
        )

    def to_dictionary(
        self,
    ) -> dict[str, object]:
        """Convert the savings goal into JSON-compatible data."""

        goal_data = asdict(self)

        goal_data["target_date"] = (
            self.target_date.isoformat()
            if self.target_date is not None
            else None
        )

        goal_data["created_at"] = (
            self.created_at.isoformat()
        )

        goal_data["updated_at"] = (
            self.updated_at.isoformat()
        )

        return goal_data

    @classmethod
    def from_dictionary(
        cls,
        goal_data: dict[str, object],
    ) -> "SavingsGoal":
        """Create a savings goal from stored JSON data."""

        stored_target_date = goal_data.get(
            "target_date"
        )

        target_date = (
            date.fromisoformat(
                str(stored_target_date)
            )
            if stored_target_date
            else None
        )

        return cls(
            goal_id=str(
                goal_data["goal_id"]
            ),
            name=str(
                goal_data["name"]
            ),
            target_amount_cents=int(
                goal_data["target_amount_cents"]
            ),
            current_amount_cents=int(
                goal_data.get(
                    "current_amount_cents",
                    0,
                )
            ),
            target_date=target_date,
            is_archived=bool(
                goal_data.get(
                    "is_archived",
                    False,
                )
            ),
            celebration_shown=bool(
                goal_data.get(
                    "celebration_shown",
                    False,
                )
            ),
            created_at=datetime.fromisoformat(
                str(
                    goal_data["created_at"]
                )
            ),
            updated_at=datetime.fromisoformat(
                str(
                    goal_data["updated_at"]
                )
            ),
        )