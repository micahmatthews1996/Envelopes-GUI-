import json
from json import JSONDecodeError
from pathlib import Path

from models.transaction import Transaction


class JsonTransactionRepository:
    """Stores and retrieves transactions using a JSON file."""

    def __init__(
        self,
        file_path: Path,
    ) -> None:
        self._file_path = file_path
        self._prepare_storage()

    def get_all(self) -> list[Transaction]:
        """Return every valid transaction stored in the JSON file."""

        try:
            file_contents = self._file_path.read_text(
                encoding="utf-8",
            )
            stored_data = json.loads(file_contents)
        except FileNotFoundError:
            return []
        except JSONDecodeError as error:
            raise RuntimeError(
                "The transactions data file contains invalid JSON."
            ) from error
        except OSError as error:
            raise RuntimeError(
                f"Unable to read transactions: {error}"
            ) from error

        if not isinstance(stored_data, list):
            raise RuntimeError(
                "The transactions data file must contain a JSON list."
            )

        transactions: list[Transaction] = []

        for item in stored_data:
            if not isinstance(item, dict):
                continue

            try:
                transaction = Transaction.from_dictionary(
                    item
                )
            except (KeyError, TypeError, ValueError):
                continue

            transactions.append(transaction)

        return transactions

    def get_by_id(
        self,
        transaction_id: str,
    ) -> Transaction | None:
        """Return a transaction by ID, or None when it does not exist."""

        for transaction in self.get_all():
            if (
                transaction.transaction_id
                == transaction_id
            ):
                return transaction

        return None

    def add(
        self,
        transaction: Transaction,
    ) -> None:
        """Add a transaction to storage."""

        transactions = self.get_all()
        transactions.append(transaction)

        self.save_all(transactions)

    def update(
        self,
        updated_transaction: Transaction,
    ) -> None:
        """Replace an existing stored transaction."""

        transactions = self.get_all()
        transaction_found = False

        for index, transaction in enumerate(
            transactions
        ):
            if (
                transaction.transaction_id
                == updated_transaction.transaction_id
            ):
                transactions[index] = (
                    updated_transaction
                )
                transaction_found = True
                break

        if not transaction_found:
            raise ValueError(
                "The transaction being updated could not be found."
            )

        self.save_all(transactions)

    def delete(
        self,
        transaction_id: str,
    ) -> None:
        """Delete a transaction from storage."""

        transactions = self.get_all()

        updated_transactions = [
            transaction
            for transaction in transactions
            if (
                transaction.transaction_id
                != transaction_id
            )
        ]

        if (
            len(updated_transactions)
            == len(transactions)
        ):
            raise ValueError(
                "The transaction being deleted could not be found."
            )

        self.save_all(updated_transactions)

    def save_all(
        self,
        transactions: list[Transaction],
    ) -> None:
        """Replace the stored transaction collection."""

        serialized_transactions = [
            transaction.to_dictionary()
            for transaction in transactions
        ]

        try:
            self._file_path.write_text(
                json.dumps(
                    serialized_transactions,
                    indent=4,
                ),
                encoding="utf-8",
            )
        except OSError as error:
            raise RuntimeError(
                f"Unable to save transactions: {error}"
            ) from error

    def _prepare_storage(self) -> None:
        """Create the data directory and transaction file."""

        try:
            self._file_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            if not self._file_path.exists():
                self._file_path.write_text(
                    "[]",
                    encoding="utf-8",
                )
        except OSError as error:
            raise RuntimeError(
                f"Unable to prepare transaction storage: {error}"
            ) from error