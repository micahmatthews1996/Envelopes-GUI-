from models.account import Account
from repositories.json_transaction_repository import (
    JsonTransactionRepository,
)


class BalanceService:
    """Calculates account balances from opening balances and transactions."""

    def __init__(
        self,
        transaction_repository: JsonTransactionRepository,
    ) -> None:
        self._transaction_repository = (
            transaction_repository
        )

    def get_current_balance_cents(
        self,
        account: Account,
    ) -> int:
        """Return an account's current balance in integer cents."""

        transaction_total_cents = sum(
            transaction.amount_cents
            for transaction in (
                self._transaction_repository.get_all()
            )
            if transaction.account_id == account.account_id
        )

        return (
            account.opening_balance_cents
            + transaction_total_cents
        )

    def get_transaction_total_cents(
        self,
        account_id: str,
    ) -> int:
        """Return the net effect of transactions for an account."""

        return sum(
            transaction.amount_cents
            for transaction in (
                self._transaction_repository.get_all()
            )
            if transaction.account_id == account_id
        )

    def get_total_balance_cents(
        self,
        accounts: list[Account],
    ) -> int:
        """Return the combined current balance of all accounts."""

        return sum(
            self.get_current_balance_cents(account)
            for account in accounts
        )