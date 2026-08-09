from dataclasses import asdict, dataclass
from datetime import datetime


@dataclass(slots=True)
class SavingsGoalAllocation:
    """Represents savings money allocated to one savings goal."""

    allocation_id: str
    goal_id: str
    amount_cents: int
    source_type: str
    source_id: str
    notes: str
    created_at: datetime

    def to_dictionary(
        self,
    ) -> dict[str, object]:
        """Convert the allocation into JSON-compatible data."""

        allocation_data = asdict(self)

        allocation_data["created_at"] = (
            self.created_at.isoformat()
        )

        return allocation_data

    @classmethod
    def from_dictionary(
        cls,
        allocation_data: dict[str, object],
    ) -> "SavingsGoalAllocation":
        """Create an allocation from stored JSON data."""

        return cls(
            allocation_id=str(
                allocation_data["allocation_id"]
            ),
            goal_id=str(
                allocation_data["goal_id"]
            ),
            amount_cents=int(
                allocation_data["amount_cents"]
            ),
            source_type=str(
                allocation_data.get(
                    "source_type",
                    "manual",
                )
            ),
            source_id=str(
                allocation_data.get(
                    "source_id",
                    "",
                )
            ),
            notes=str(
                allocation_data.get(
                    "notes",
                    "",
                )
            ),
            created_at=datetime.fromisoformat(
                str(
                    allocation_data["created_at"]
                )
            ),
        )