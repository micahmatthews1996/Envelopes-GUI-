from uuid import uuid4

from models.account import Account
from repositories.json_account_repository import JsonAccountRepository
from utils.money import dollars_to_cents


class AccountService:
    """Provides account-related business operations."""

    def __init__(
        self,
        repository: JsonAccountRepository,
    ) -> None:
        self._repository = repository

    def get_accounts(self) -> list[Account]:
        """Return all accounts sorted alphabetically by name."""

        accounts = self._repository.get_all()

        return sorted(
            accounts,
            key=lambda account: account.name.casefold(),
        )

    def create_account(
        self,
        name: str,
        opening_balance: float,
    ) -> Account:
        """Validate and create a financial account."""

        cleaned_name = name.strip()

        if not cleaned_name:
            raise ValueError("Account name is required.")

        if len(cleaned_name) > 50:
            raise ValueError(
                "Account name cannot exceed 50 characters."
            )

        accounts = self._repository.get_all()

        duplicate_exists = any(
            account.name.casefold() == cleaned_name.casefold()
            for account in accounts
        )

        if duplicate_exists:
            raise ValueError(
                "An account with that name already exists."
            )

        account = Account(
            account_id=str(uuid4()),
            name=cleaned_name,
            opening_balance_cents=dollars_to_cents(
                opening_balance
            ),
        )

        accounts.append(account)
        self._repository.save_all(accounts)

        return account

    def delete_account(self, account_id: str) -> None:
        """Delete an account using its unique identifier."""

        accounts = self._repository.get_all()

        updated_accounts = [
            account
            for account in accounts
            if account.account_id != account_id
        ]

        if len(updated_accounts) == len(accounts):
            raise ValueError(
                "The selected account could not be found."
            )

        self._repository.save_all(updated_accounts)