import json
from json import JSONDecodeError
from pathlib import Path

from models.account import Account


class JsonAccountRepository:
    """Stores and retrieves financial accounts using a JSON file."""

    def __init__(self, file_path: Path) -> None:
        self._file_path = file_path
        self._prepare_storage()

    def get_all(self) -> list[Account]:
        """Return every valid account stored in the JSON file."""

        try:
            file_contents = self._file_path.read_text(
                encoding="utf-8",
            )
            stored_data = json.loads(file_contents)
        except FileNotFoundError:
            return []
        except JSONDecodeError as error:
            raise RuntimeError(
                "The accounts data file contains invalid JSON."
            ) from error
        except OSError as error:
            raise RuntimeError(
                f"Unable to read accounts: {error}"
            ) from error

        if not isinstance(stored_data, list):
            raise RuntimeError(
                "The accounts data file must contain a JSON list."
            )

        accounts: list[Account] = []

        for item in stored_data:
            if not isinstance(item, dict):
                continue

            try:
                account = Account.from_dictionary(item)
            except (KeyError, TypeError, ValueError):
                continue

            accounts.append(account)

        return accounts

    def save_all(self, accounts: list[Account]) -> None:
        """Replace the stored account collection."""

        serialized_accounts = [
            account.to_dictionary()
            for account in accounts
        ]

        try:
            self._file_path.write_text(
                json.dumps(
                    serialized_accounts,
                    indent=4,
                ),
                encoding="utf-8",
            )
        except OSError as error:
            raise RuntimeError(
                f"Unable to save accounts: {error}"
            ) from error

    def migrate_legacy_balances(self) -> None:
        """
        Rewrite older account records using integer cents.

        Records containing `opening_balance` are loaded by the
        Account model and saved back as `opening_balance_cents`.
        """

        accounts = self.get_all()
        self.save_all(accounts)

    def _prepare_storage(self) -> None:
        """Create the data directory and file when necessary."""

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
                f"Unable to prepare account storage: {error}"
            ) from error