from datetime import date

from models.dashboard_summary import (
    DashboardAccountItem,
    DashboardSavingsGoalItem,
    DashboardSummary,
    DashboardTransactionItem,
)
from services.account_service import AccountService
from services.balance_service import BalanceService
from services.category_service import CategoryService
from services.savings_goal_service import (
    SavingsGoalService,
)
from services.spending_analytics_service import (
    SpendingAnalyticsService,
)
from services.transaction_service import (
    TransactionService,
)


MAX_RECENT_TRANSACTIONS = 5
MAX_DASHBOARD_SAVINGS_GOALS = 3


class DashboardService:
    """Builds all information displayed on the Dashboard."""

    def __init__(
        self,
        account_service: AccountService,
        balance_service: BalanceService,
        transaction_service: TransactionService,
        category_service: CategoryService,
        spending_analytics_service: SpendingAnalyticsService,
        savings_goal_service: SavingsGoalService,
    ) -> None:
        self._account_service = account_service
        self._balance_service = balance_service
        self._transaction_service = transaction_service
        self._category_service = category_service
        self._spending_analytics_service = (
            spending_analytics_service
        )
        self._savings_goal_service = (
            savings_goal_service
        )

    def get_dashboard_summary(
        self,
    ) -> DashboardSummary:
        """Return everything needed by the Dashboard."""

        accounts = (
            self._account_service.get_accounts()
        )

        transactions = (
            self._transaction_service
            .get_transactions()
        )

        categories = (
            self._category_service.get_categories(
                include_archived=True
            )
        )

        savings_goals = (
            self._savings_goal_service.get_goals()
        )

        category_lookup = {
            category.category_id: category
            for category in categories
        }

        net_worth_cents = 0
        total_income_cents = 0
        total_expense_cents = 0
        total_savings_cents = 0

        dashboard_accounts: list[
            DashboardAccountItem
        ] = []

        for account in accounts:
            current_balance_cents = (
                self._balance_service
                .get_current_balance_cents(
                    account
                )
            )

            net_worth_cents += (
                current_balance_cents
            )

            if account.account_type == "Savings":
                total_savings_cents += (
                    current_balance_cents
                )

            dashboard_accounts.append(
                DashboardAccountItem(
                    account_id=account.account_id,
                    account_name=account.name,
                    current_balance_cents=(
                        current_balance_cents
                    ),
                )
            )

        sorted_transactions = sorted(
            transactions,
            key=lambda transaction: (
                transaction.transaction_date,
                transaction.created_at,
            ),
            reverse=True,
        )

        dashboard_transactions: list[
            DashboardTransactionItem
        ] = []

        for transaction in sorted_transactions:
            if not transaction.is_transfer:
                if transaction.amount_cents >= 0:
                    total_income_cents += (
                        transaction.amount_cents
                    )
                else:
                    total_expense_cents += abs(
                        transaction.amount_cents
                    )

            if (
                len(dashboard_transactions)
                >= MAX_RECENT_TRANSACTIONS
            ):
                continue

            if transaction.is_transfer:
                category_name = "Transfer"
            else:
                category = category_lookup.get(
                    transaction.category_id
                )

                category_name = (
                    category.name
                    if category is not None
                    else "Unknown Category"
                )

            dashboard_transactions.append(
                DashboardTransactionItem(
                    transaction_id=(
                        transaction.transaction_id
                    ),
                    payee=transaction.payee,
                    category_name=category_name,
                    transaction_date=(
                        transaction.transaction_date
                    ),
                    amount_cents=(
                        transaction.amount_cents
                    ),
                )
            )

        dashboard_accounts.sort(
            key=lambda account: (
                account.account_name.casefold()
            )
        )

        sorted_savings_goals = sorted(
            savings_goals,
            key=lambda goal: (
                goal.is_completed,
                (
                    goal.target_date
                    if goal.target_date is not None
                    else date.max
                ),
                goal.created_at,
            ),
        )

        dashboard_savings_goals = [
            DashboardSavingsGoalItem(
                goal_id=goal.goal_id,
                name=goal.name,
                current_amount_cents=(
                    goal.current_amount_cents
                ),
                target_amount_cents=(
                    goal.target_amount_cents
                ),
                remaining_amount_cents=(
                    goal.remaining_amount_cents
                ),
                progress_percent=(
                    goal.progress_percent
                ),
                target_date=goal.target_date,
                is_completed=goal.is_completed,
            )
            for goal in sorted_savings_goals[
                :MAX_DASHBOARD_SAVINGS_GOALS
            ]
        ]

        return DashboardSummary(
            net_worth_cents=net_worth_cents,
            total_income_cents=(
                total_income_cents
            ),
            total_expense_cents=(
                total_expense_cents
            ),
            total_savings_cents=(
                total_savings_cents
            ),
            recent_transactions=(
                dashboard_transactions
            ),
            accounts=dashboard_accounts,
            category_spending=(
                self._spending_analytics_service
                .get_category_spending()
            ),
            savings_goals=(
                dashboard_savings_goals
            ),
        )