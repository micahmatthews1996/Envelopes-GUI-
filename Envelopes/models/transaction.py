from dataclasses import asdict, dataclass
from datetime import date, datetime


@dataclass(slots=True)
class Transaction:
    """Represents a financial transaction."""

    transaction_id: str
    account_id: str
    category_id: str
    payee: str
    amount_cents: int
    transaction_date: date
    notes: str
    is_cleared: bool

    is_transfer: bool
    transfer_id: str
    transfer_account_id: str

    created_at: datetime
    updated_at: datetime

    def to_dictionary(self) -> dict[str, object]:
        """Convert the transaction into JSON-compatible data."""

        transaction_data = asdict(self)

        transaction_data["transaction_date"] = (
            self.transaction_date.isoformat()
        )

        transaction_data["created_at"] = (
            self.created_at.isoformat()
        )

        transaction_data["updated_at"] = (
            self.updated_at.isoformat()
        )

        return transaction_data

    @classmethod
    def from_dictionary(
        cls,
        transaction_data: dict[str, object],
    ) -> "Transaction":
        """Create a transaction from stored JSON data."""

        return cls(
            transaction_id=str(
                transaction_data["transaction_id"]
            ),
            account_id=str(
                transaction_data["account_id"]
            ),
            category_id=str(
                transaction_data["category_id"]
            ),
            payee=str(
                transaction_data.get(
                    "payee",
                    "",
                )
            ),
            amount_cents=int(
                transaction_data["amount_cents"]
            ),
            transaction_date=date.fromisoformat(
                str(
                    transaction_data[
                        "transaction_date"
                    ]
                )
            ),
            notes=str(
                transaction_data.get(
                    "notes",
                    "",
                )
            ),
            is_cleared=bool(
                transaction_data.get(
                    "is_cleared",
                    False,
                )
            ),

            is_transfer=bool(
                transaction_data.get(
                    "is_transfer",
                    False,
                )
            ),

            transfer_id=str(
                transaction_data.get(
                    "transfer_id",
                    "",
                )
            ),

            transfer_account_id=str(
                transaction_data.get(
                    "transfer_account_id",
                    "",
                )
            ),

            created_at=datetime.fromisoformat(
                str(
                    transaction_data["created_at"]
                )
            ),

            updated_at=datetime.fromisoformat(
                str(
                    transaction_data["updated_at"]
                )
            ),
        )