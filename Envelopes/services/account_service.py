from uuid import uuid4

from models.account import Account
from repositories.json_account_repository import (
    JsonAccountRepository,
)
from utils.money import dollars_to_cents


VALID_ACCOUNT_TYPES = {
    "Checking",
    "Savings",
    "Cash",
}

DEFAULT_ACCOUNTS = (
    {
        "name": "Checking",
        "account_type": "Checking",
    },
    {
        "name": "Savings",
        "account_type": "Savings",
    },
    {
        "name": "Cash",
        "account_type": "Cash",
    },
)


class AccountService:
    """Provides account-related business operations."""

    def __init__(
        self,
        repository: JsonAccountRepository,
    ) -> None:
        self._repository = repository

    def get_accounts(self) -> list[Account]:
        """Return all accounts sorted alphabetically."""

        accounts = self._repository.get_all()

        return sorted(
            accounts,
            key=lambda account: account.name.casefold(),
        )

    def seed_default_accounts(self) -> None:
        """
        Create starter accounts when no accounts exist.

        The seeded accounts are normal accounts and may be
        renamed, edited, or deleted by the user afterward.
        """

        existing_accounts = self._repository.get_all()

        if existing_accounts:
            self._migrate_default_account_types(
                existing_accounts
            )
            return

        for account_data in DEFAULT_ACCOUNTS:
            account = Account(
                account_id=str(uuid4()),
                name=str(
                    account_data["name"]
                ),
                account_type=str(
                    account_data["account_type"]
                ),
                opening_balance_cents=0,
            )

            self._repository.add(account)

    def _migrate_default_account_types(
        self,
        accounts: list[Account],
    ) -> None:
        """
        Correct legacy seeded accounts that were saved as Checking.

        Older account records did not store an account type, so the
        Account model temporarily defaulted every legacy account to
        Checking. This migration safely corrects only the original
        default account names.
        """

        default_type_by_name = {
            "checking": "Checking",
            "savings": "Savings",
            "cash": "Cash",
        }

        migration_needed = False
        migrated_accounts: list[Account] = []

        for account in accounts:
            expected_type = default_type_by_name.get(
                account.name.strip().casefold()
            )

            if (
                expected_type is not None
                and account.account_type
                != expected_type
            ):
                migrated_accounts.append(
                    Account(
                        account_id=account.account_id,
                        name=account.name,
                        account_type=expected_type,
                        opening_balance_cents=(
                            account.opening_balance_cents
                        ),
                    )
                )
                migration_needed = True
            else:
                migrated_accounts.append(account)

        if migration_needed:
            self._repository.save_all(
                migrated_accounts
            )

    def create_account(
        self,
        name: str,
        account_type: str,
        opening_balance: float,
    ) -> Account:
        """Create a new financial account."""

        cleaned_name = self._validate_name(
            name
        )
        cleaned_account_type = (
            self._validate_account_type(
                account_type
            )
        )

        self._ensure_unique_name(
            cleaned_name
        )

        account = Account(
            account_id=str(uuid4()),
            name=cleaned_name,
            account_type=cleaned_account_type,
            opening_balance_cents=dollars_to_cents(
                opening_balance
            ),
        )

        self._repository.add(account)

        return account

    def update_account(
        self,
        account_id: str,
        name: str,
        account_type: str,
        opening_balance: float,
    ) -> Account:
        """Update an existing account."""

        cleaned_name = self._validate_name(
            name
        )
        cleaned_account_type = (
            self._validate_account_type(
                account_type
            )
        )

        account = self._repository.get_by_id(
            account_id
        )

        if account is None:
            raise ValueError(
                "The selected account could not be found."
            )

        self._ensure_unique_name(
            cleaned_name,
            excluded_account_id=account_id,
        )

        updated_account = Account(
            account_id=account.account_id,
            name=cleaned_name,
            account_type=cleaned_account_type,
            opening_balance_cents=dollars_to_cents(
                opening_balance
            ),
        )

        self._repository.update(
            updated_account
        )

        return updated_account

    def delete_account(
        self,
        account_id: str,
    ) -> None:
        """Delete an account."""

        self._repository.delete(account_id)

    def _validate_name(
        self,
        name: str,
    ) -> str:
        """Validate and normalize an account name."""

        cleaned_name = name.strip()

        if not cleaned_name:
            raise ValueError(
                "Account name is required."
            )

        if len(cleaned_name) > 50:
            raise ValueError(
                "Account name cannot exceed 50 characters."
            )

        return cleaned_name

    def _validate_account_type(
        self,
        account_type: str,
    ) -> str:
        """Validate and normalize an account type."""

        cleaned_account_type = (
            account_type.strip().title()
        )

        if (
            cleaned_account_type
            not in VALID_ACCOUNT_TYPES
        ):
            raise ValueError(
                "Account type must be Checking, "
                "Savings, or Cash."
            )

        return cleaned_account_type

    def _ensure_unique_name(
        self,
        name: str,
        excluded_account_id: str | None = None,
    ) -> None:
        """Ensure account names remain unique."""

        for account in self._repository.get_all():
            if (
                account.account_id
                != excluded_account_id
                and account.name.casefold()
                == name.casefold()
            ):
                raise ValueError(
                    "An account with that name already exists."
                )