from dataclasses import asdict, dataclass

from utils.money import dollars_to_cents


@dataclass(slots=True)
class Account:
    """Represents a financial account."""

    account_id: str
    name: str
    opening_balance_cents: int

    def to_dictionary(self) -> dict[str, str | int]:
        """Convert the account into JSON-compatible data."""

        return asdict(self)

    @classmethod
    def from_dictionary(
        cls,
        account_data: dict[str, object],
    ) -> "Account":
        """
        Create an account from stored JSON data.

        Older account records containing `opening_balance`
        are automatically converted to integer cents.
        """

        if "opening_balance_cents" in account_data:
            opening_balance_cents = int(
                account_data["opening_balance_cents"]
            )
        elif "opening_balance" in account_data:
            opening_balance_cents = dollars_to_cents(
                account_data["opening_balance"]
            )
        else:
            raise KeyError(
                "Account data is missing an opening balance."
            )

        return cls(
            account_id=str(account_data["account_id"]),
            name=str(account_data["name"]),
            opening_balance_cents=opening_balance_cents,
        )