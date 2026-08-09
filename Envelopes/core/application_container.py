from repositories.json_account_repository import (
    JsonAccountRepository,
)
from repositories.json_budget_repository import (
    JsonBudgetRepository,
)
from repositories.json_budget_rollover_repository import (
    JsonBudgetRolloverRepository,
)
from repositories.json_category_repository import (
    JsonCategoryRepository,
)
from repositories.json_savings_goal_allocation_repository import (
    JsonSavingsGoalAllocationRepository,
)
from repositories.json_savings_goal_repository import (
    JsonSavingsGoalRepository,
)
from repositories.json_transaction_repository import (
    JsonTransactionRepository,
)
from services.account_service import AccountService
from services.balance_service import BalanceService
from services.budget_service import BudgetService
from services.budget_rollover_service import BudgetRolloverService
from services.category_service import CategoryService
from services.dashboard_service import DashboardService
from services.reports_service import ReportsService
from services.savings_goal_allocation_service import (
    SavingsGoalAllocationService,
)
from services.savings_goal_service import (
    SavingsGoalService,
)
from services.spending_analytics_service import (
    SpendingAnalyticsService,
)
from services.transaction_service import (
    TransactionService,
)
from utils.paths import (
    ACCOUNTS_FILE,
    BUDGETS_FILE,
    BUDGET_ROLLOVERS_FILE,
    CATEGORIES_FILE,
    SAVINGS_GOAL_ALLOCATIONS_FILE,
    SAVINGS_GOALS_FILE,
    TRANSACTIONS_FILE,
)


class ApplicationContainer:
    """
    Creates and owns all repositories and services
    used throughout the application.
    """

    def __init__(self) -> None:
        self.account_repository = JsonAccountRepository(
            ACCOUNTS_FILE
        )

        self.budget_repository = JsonBudgetRepository(
            BUDGETS_FILE
        )

        self.budget_rollover_repository = (
            JsonBudgetRolloverRepository(
                BUDGET_ROLLOVERS_FILE
            )
        )

        self.category_repository = JsonCategoryRepository(
            CATEGORIES_FILE
        )

        self.transaction_repository = (
            JsonTransactionRepository(
                TRANSACTIONS_FILE
            )
        )

        self.savings_goal_repository = (
            JsonSavingsGoalRepository(
                SAVINGS_GOALS_FILE
            )
        )

        self.savings_goal_allocation_repository = (
            JsonSavingsGoalAllocationRepository(
                SAVINGS_GOAL_ALLOCATIONS_FILE
            )
        )

        self.account_repository.migrate_legacy_balances()

        self.account_service = AccountService(
            self.account_repository
        )

        self.account_service.seed_default_accounts()

        self.category_service = CategoryService(
            self.category_repository
        )

        self.category_service.seed_default_categories()

        self.transaction_service = TransactionService(
            transaction_repository=(
                self.transaction_repository
            ),
            account_repository=(
                self.account_repository
            ),
            category_repository=(
                self.category_repository
            ),
        )

        self.balance_service = BalanceService(
            self.transaction_repository
        )

        self.budget_service = BudgetService(
            budget_repository=(
                self.budget_repository
            ),
            category_service=(
                self.category_service
            ),
            transaction_service=(
                self.transaction_service
            ),
        )

        self.savings_goal_service = (
            SavingsGoalService(
                self.savings_goal_repository
            )
        )

        self.savings_goal_allocation_service = (
            SavingsGoalAllocationService(
                allocation_repository=(
                    self.savings_goal_allocation_repository
                ),
                savings_goal_service=(
                    self.savings_goal_service
                ),
                account_service=(
                    self.account_service
                ),
                balance_service=(
                    self.balance_service
                ),
                transaction_service=(
                    self.transaction_service
                ),
            )
        )

        self.savings_goal_allocation_service\
            .sync_all_goal_current_amounts()


        self.budget_rollover_service = (
            BudgetRolloverService(
                rollover_repository=(
                    self.budget_rollover_repository
                ),
                budget_service=self.budget_service,
                transaction_service=self.transaction_service,
                savings_goal_allocation_service=(
                    self.savings_goal_allocation_service
                ),
            )
        )

        self.spending_analytics_service = (
            SpendingAnalyticsService(
                transaction_service=(
                    self.transaction_service
                ),
                category_service=(
                    self.category_service
                ),
            )
        )

        self.reports_service = ReportsService(
            transaction_service=(
                self.transaction_service
            ),
            spending_analytics_service=(
                self.spending_analytics_service
            ),
            budget_service=(
                self.budget_service
            ),
        )

        self.dashboard_service = DashboardService(
            account_service=(
                self.account_service
            ),
            balance_service=(
                self.balance_service
            ),
            transaction_service=(
                self.transaction_service
            ),
            category_service=(
                self.category_service
            ),
            spending_analytics_service=(
                self.spending_analytics_service
            ),
            savings_goal_service=(
                self.savings_goal_service
            ),
        )