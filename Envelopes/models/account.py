from dataclasses import asdict, dataclass

from utils.money import dollars_to_cents


DEFAULT_ACCOUNT_TYPE = "Checking"


@dataclass(slots=True)
class Account:
    """Represents a financial account."""

    account_id: str
    name: str
    account_type: str
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

        Older records without an account type default to
        Checking so they remain compatible.
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

        account_type = str(
            account_data.get(
                "account_type",
                DEFAULT_ACCOUNT_TYPE,
            )
        ).strip()

        if not account_type:
            account_type = DEFAULT_ACCOUNT_TYPE

        return cls(
            account_id=str(
                account_data["account_id"]
            ),
            name=str(
                account_data["name"]
            ),
            account_type=account_type,
            opening_balance_cents=(
                opening_balance_cents
            ),
        )