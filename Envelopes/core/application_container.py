from repositories.json_account_repository import JsonAccountRepository
from services.account_service import AccountService
from utils.paths import ACCOUNTS_FILE


class ApplicationContainer:
    """
    Creates and owns all repositories and services used
    throughout the application.
    """

    def __init__(self) -> None:

        # ---------- Repositories ----------

        self.account_repository = JsonAccountRepository(
            ACCOUNTS_FILE
        )

        self.account_repository.migrate_legacy_balances()

        # ---------- Services ----------

        self.account_service = AccountService(
            self.account_repository
        )