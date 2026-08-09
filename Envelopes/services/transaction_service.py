from datetime import date, datetime
from uuid import uuid4

from models.transaction import Transaction
from repositories.json_account_repository import (
    JsonAccountRepository,
)
from repositories.json_category_repository import (
    JsonCategoryRepository,
)
from repositories.json_transaction_repository import (
    JsonTransactionRepository,
)
from utils.money import dollars_to_cents


class TransactionService:
    """Provides transaction and transfer business operations."""

    def __init__(
        self,
        transaction_repository: JsonTransactionRepository,
        account_repository: JsonAccountRepository,
        category_repository: JsonCategoryRepository,
    ) -> None:
        self._transaction_repository = (
            transaction_repository
        )
        self._account_repository = account_repository
        self._category_repository = (
            category_repository
        )

    def get_transactions(
        self,
    ) -> list[Transaction]:
        """Return transactions sorted newest first."""

        transactions = (
            self._transaction_repository.get_all()
        )

        return sorted(
            transactions,
            key=lambda transaction: (
                transaction.transaction_date,
                transaction.created_at,
            ),
            reverse=True,
        )

    def get_transaction_by_id(
        self,
        transaction_id: str,
    ) -> Transaction:
        """Return a transaction by ID."""

        transaction = (
            self._transaction_repository.get_by_id(
                transaction_id
            )
        )

        if transaction is None:
            raise ValueError(
                "The selected transaction could not be found."
            )

        return transaction

    def get_transfer_transactions(
        self,
        transfer_id: str,
    ) -> list[Transaction]:
        """Return both transactions belonging to a transfer."""

        cleaned_transfer_id = transfer_id.strip()

        if not cleaned_transfer_id:
            raise ValueError(
                "The transfer could not be identified."
            )

        transfer_transactions = [
            transaction
            for transaction
            in self._transaction_repository.get_all()
            if (
                transaction.is_transfer
                and transaction.transfer_id
                == cleaned_transfer_id
            )
        ]

        if not transfer_transactions:
            raise ValueError(
                "The selected transfer could not be found."
            )

        return transfer_transactions

    def create_transaction(
        self,
        account_id: str,
        category_id: str,
        payee: str,
        amount: float,
        transaction_date: date,
        notes: str = "",
        is_cleared: bool = False,
    ) -> Transaction:
        """Validate and create a normal transaction."""

        cleaned_payee = self._validate_payee(
            payee
        )
        cleaned_notes = self._validate_notes(
            notes
        )

        self._validate_account(
            account_id
        )

        category_type = self._validate_category(
            category_id
        )

        amount_cents = self._prepare_amount_cents(
            amount=amount,
            category_type=category_type,
        )

        current_time = datetime.now().astimezone()

        transaction = Transaction(
            transaction_id=str(uuid4()),
            account_id=account_id,
            category_id=category_id,
            payee=cleaned_payee,
            amount_cents=amount_cents,
            transaction_date=transaction_date,
            notes=cleaned_notes,
            is_cleared=is_cleared,
            is_transfer=False,
            transfer_id="",
            transfer_account_id="",
            created_at=current_time,
            updated_at=current_time,
        )

        self._transaction_repository.add(
            transaction
        )

        return transaction

    def create_transfer(
        self,
        source_account_id: str,
        destination_account_id: str,
        amount: float,
        transaction_date: date,
        notes: str = "",
        is_cleared: bool = False,
    ) -> tuple[Transaction, Transaction]:
        """Create two linked transactions for a transfer."""

        source_account = self._get_account(
            source_account_id
        )
        destination_account = self._get_account(
            destination_account_id
        )

        if (
            source_account.account_id
            == destination_account.account_id
        ):
            raise ValueError(
                "The source and destination accounts "
                "must be different."
            )

        amount_cents = (
            self._prepare_transfer_amount_cents(
                amount
            )
        )

        cleaned_notes = self._validate_notes(
            notes
        )

        transfer_id = str(uuid4())
        current_time = datetime.now().astimezone()

        source_transaction = Transaction(
            transaction_id=str(uuid4()),
            account_id=source_account.account_id,
            category_id="",
            payee=(
                f"Transfer to "
                f"{destination_account.name}"
            ),
            amount_cents=-amount_cents,
            transaction_date=transaction_date,
            notes=cleaned_notes,
            is_cleared=is_cleared,
            is_transfer=True,
            transfer_id=transfer_id,
            transfer_account_id=(
                destination_account.account_id
            ),
            created_at=current_time,
            updated_at=current_time,
        )

        destination_transaction = Transaction(
            transaction_id=str(uuid4()),
            account_id=(
                destination_account.account_id
            ),
            category_id="",
            payee=(
                f"Transfer from "
                f"{source_account.name}"
            ),
            amount_cents=amount_cents,
            transaction_date=transaction_date,
            notes=cleaned_notes,
            is_cleared=is_cleared,
            is_transfer=True,
            transfer_id=transfer_id,
            transfer_account_id=(
                source_account.account_id
            ),
            created_at=current_time,
            updated_at=current_time,
        )

        transactions = (
            self._transaction_repository.get_all()
        )

        transactions.extend(
            [
                source_transaction,
                destination_transaction,
            ]
        )

        self._transaction_repository.save_all(
            transactions
        )

        return (
            source_transaction,
            destination_transaction,
        )

    def update_transaction(
        self,
        transaction_id: str,
        account_id: str,
        category_id: str,
        payee: str,
        amount: float,
        transaction_date: date,
        notes: str = "",
        is_cleared: bool = False,
    ) -> Transaction:
        """Validate and update a normal transaction."""

        existing_transaction = (
            self.get_transaction_by_id(
                transaction_id
            )
        )

        if existing_transaction.is_transfer:
            raise ValueError(
                "Transfers must be edited through "
                "the transfer workflow."
            )

        cleaned_payee = self._validate_payee(
            payee
        )
        cleaned_notes = self._validate_notes(
            notes
        )

        self._validate_account(
            account_id
        )

        category_type = self._validate_category(
            category_id
        )

        amount_cents = self._prepare_amount_cents(
            amount=amount,
            category_type=category_type,
        )

        updated_transaction = Transaction(
            transaction_id=(
                existing_transaction.transaction_id
            ),
            account_id=account_id,
            category_id=category_id,
            payee=cleaned_payee,
            amount_cents=amount_cents,
            transaction_date=transaction_date,
            notes=cleaned_notes,
            is_cleared=is_cleared,
            is_transfer=False,
            transfer_id="",
            transfer_account_id="",
            created_at=(
                existing_transaction.created_at
            ),
            updated_at=datetime.now().astimezone(),
        )

        self._transaction_repository.update(
            updated_transaction
        )

        return updated_transaction

    def update_transfer(
        self,
        transfer_id: str,
        source_account_id: str,
        destination_account_id: str,
        amount: float,
        transaction_date: date,
        notes: str = "",
        is_cleared: bool = False,
    ) -> tuple[Transaction, Transaction]:
        """Update both linked transactions in a transfer."""

        source_account = self._get_account(
            source_account_id
        )
        destination_account = self._get_account(
            destination_account_id
        )

        if (
            source_account.account_id
            == destination_account.account_id
        ):
            raise ValueError(
                "The source and destination accounts "
                "must be different."
            )

        amount_cents = (
            self._prepare_transfer_amount_cents(
                amount
            )
        )

        cleaned_notes = self._validate_notes(
            notes
        )

        transactions = (
            self._transaction_repository.get_all()
        )

        linked_transactions = [
            transaction
            for transaction in transactions
            if (
                transaction.is_transfer
                and transaction.transfer_id
                == transfer_id
            )
        ]

        if len(linked_transactions) != 2:
            raise ValueError(
                "The linked transfer transactions "
                "could not be found."
            )

        source_transaction_id = (
            self._find_transfer_transaction_id(
                linked_transactions,
                negative=True,
            )
        )

        destination_transaction_id = (
            self._find_transfer_transaction_id(
                linked_transactions,
                negative=False,
            )
        )

        source_created_at = (
            self._find_transfer_created_at(
                linked_transactions,
                negative=True,
            )
        )

        destination_created_at = (
            self._find_transfer_created_at(
                linked_transactions,
                negative=False,
            )
        )

        current_time = datetime.now().astimezone()

        source_transaction = Transaction(
            transaction_id=source_transaction_id,
            account_id=source_account.account_id,
            category_id="",
            payee=(
                f"Transfer to "
                f"{destination_account.name}"
            ),
            amount_cents=-amount_cents,
            transaction_date=transaction_date,
            notes=cleaned_notes,
            is_cleared=is_cleared,
            is_transfer=True,
            transfer_id=transfer_id,
            transfer_account_id=(
                destination_account.account_id
            ),
            created_at=source_created_at,
            updated_at=current_time,
        )

        destination_transaction = Transaction(
            transaction_id=(
                destination_transaction_id
            ),
            account_id=(
                destination_account.account_id
            ),
            category_id="",
            payee=(
                f"Transfer from "
                f"{source_account.name}"
            ),
            amount_cents=amount_cents,
            transaction_date=transaction_date,
            notes=cleaned_notes,
            is_cleared=is_cleared,
            is_transfer=True,
            transfer_id=transfer_id,
            transfer_account_id=(
                source_account.account_id
            ),
            created_at=destination_created_at,
            updated_at=current_time,
        )

        linked_transaction_ids = {
            transaction.transaction_id
            for transaction in linked_transactions
        }

        updated_transactions = [
            transaction
            for transaction in transactions
            if (
                transaction.transaction_id
                not in linked_transaction_ids
            )
        ]

        updated_transactions.extend(
            [
                source_transaction,
                destination_transaction,
            ]
        )

        self._transaction_repository.save_all(
            updated_transactions
        )

        return (
            source_transaction,
            destination_transaction,
        )

    def delete_transaction(
        self,
        transaction_id: str,
    ) -> None:
        """Delete one transaction or an entire transfer."""

        transaction = self.get_transaction_by_id(
            transaction_id
        )

        if transaction.is_transfer:
            self.delete_transfer(
                transaction.transfer_id
            )
            return

        self._transaction_repository.delete(
            transaction_id
        )

    def delete_transfer(
        self,
        transfer_id: str,
    ) -> None:
        """Delete both transactions belonging to a transfer."""

        cleaned_transfer_id = transfer_id.strip()

        if not cleaned_transfer_id:
            raise ValueError(
                "The transfer could not be identified."
            )

        transactions = (
            self._transaction_repository.get_all()
        )

        updated_transactions = [
            transaction
            for transaction in transactions
            if not (
                transaction.is_transfer
                and transaction.transfer_id
                == cleaned_transfer_id
            )
        ]

        if (
            len(updated_transactions)
            == len(transactions)
        ):
            raise ValueError(
                "The transfer being deleted could not be found."
            )

        self._transaction_repository.save_all(
            updated_transactions
        )

    def _get_account(
        self,
        account_id: str,
    ):
        """Return a validated account."""

        account = self._account_repository.get_by_id(
            account_id
        )

        if account is None:
            raise ValueError(
                "The selected account could not be found."
            )

        return account

    def _validate_account(
        self,
        account_id: str,
    ) -> None:
        """Ensure the selected account exists."""

        self._get_account(
            account_id
        )

    def _validate_category(
        self,
        category_id: str,
    ) -> str:
        """Ensure the category exists and return its type."""

        category = (
            self._category_repository.get_by_id(
                category_id
            )
        )

        if category is None:
            raise ValueError(
                "The selected category could not be found."
            )

        if category.is_archived:
            raise ValueError(
                "Archived categories cannot be used "
                "for new transactions."
            )

        if category.category_type not in {
            "Expense",
            "Income",
        }:
            raise ValueError(
                "The selected category type is invalid."
            )

        return category.category_type

    def _prepare_amount_cents(
        self,
        amount: float,
        category_type: str,
    ) -> int:
        """Convert and sign a normal transaction amount."""

        amount_cents = dollars_to_cents(
            abs(amount)
        )

        if amount_cents == 0:
            raise ValueError(
                "Transaction amount must be greater than zero."
            )

        if category_type == "Expense":
            return -amount_cents

        return amount_cents

    def _prepare_transfer_amount_cents(
        self,
        amount: float,
    ) -> int:
        """Convert and validate a transfer amount."""

        amount_cents = dollars_to_cents(
            abs(amount)
        )

        if amount_cents == 0:
            raise ValueError(
                "Transfer amount must be greater than zero."
            )

        return amount_cents

    def _validate_payee(
        self,
        payee: str,
    ) -> str:
        """Validate and normalize a payee."""

        cleaned_payee = payee.strip()

        if not cleaned_payee:
            raise ValueError(
                "Payee is required."
            )

        if len(cleaned_payee) > 100:
            raise ValueError(
                "Payee cannot exceed 100 characters."
            )

        return cleaned_payee

    def _validate_notes(
        self,
        notes: str,
    ) -> str:
        """Validate and normalize optional notes."""

        cleaned_notes = notes.strip()

        if len(cleaned_notes) > 2000:
            raise ValueError(
                "Notes cannot exceed 2,000 characters."
            )

        return cleaned_notes

    def _find_transfer_transaction_id(
        self,
        transactions: list[Transaction],
        negative: bool,
    ) -> str:
        """Return the ID for one half of a transfer."""

        for transaction in transactions:
            if (
                negative
                and transaction.amount_cents < 0
            ):
                return transaction.transaction_id

            if (
                not negative
                and transaction.amount_cents > 0
            ):
                return transaction.transaction_id

        raise ValueError(
            "The transfer contains invalid linked transactions."
        )

    def _find_transfer_created_at(
        self,
        transactions: list[Transaction],
        negative: bool,
    ) -> datetime:
        """Return the original creation time for one transfer half."""

        for transaction in transactions:
            if (
                negative
                and transaction.amount_cents < 0
            ):
                return transaction.created_at

            if (
                not negative
                and transaction.amount_cents > 0
            ):
                return transaction.created_at

        raise ValueError(
            "The transfer contains invalid linked transactions."
        )