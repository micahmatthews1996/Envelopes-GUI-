from calendar import monthrange
from dataclasses import dataclass
from datetime import date

from models.dashboard_summary import (
    DashboardCategorySpendingItem,
)
from services.budget_service import (
    BudgetProgress,
    BudgetService,
)
from services.spending_analytics_service import (
    SpendingAnalyticsService,
)
from services.transaction_service import (
    TransactionService,
)


@dataclass(slots=True)
class MonthlyReportSummary:
    """Contains headline totals for one calendar month."""

    month_start: date
    month_end: date
    total_income_cents: int
    total_expense_cents: int
    net_cash_flow_cents: int
    transaction_count: int


class ReportsService:
    """Provides reusable financial reporting calculations."""

    def __init__(
        self,
        transaction_service: TransactionService,
        spending_analytics_service: (
            SpendingAnalyticsService
        ),
        budget_service: BudgetService,
    ) -> None:
        self._transaction_service = (
            transaction_service
        )
        self._spending_analytics_service = (
            spending_analytics_service
        )
        self._budget_service = budget_service

    def get_monthly_summary(
        self,
        month: date | None = None,
    ) -> MonthlyReportSummary:
        """Return income, expenses, and cash flow for a month."""

        month_start, month_end = (
            self._resolve_month_range(
                month
            )
        )

        total_income_cents = 0
        total_expense_cents = 0
        transaction_count = 0

        transactions = (
            self._transaction_service.get_transactions()
        )

        for transaction in transactions:
            if transaction.is_transfer:
                continue

            if not (
                month_start
                <= transaction.transaction_date
                <= month_end
            ):
                continue

            transaction_count += 1

            if transaction.amount_cents > 0:
                total_income_cents += (
                    transaction.amount_cents
                )
            elif transaction.amount_cents < 0:
                total_expense_cents += abs(
                    transaction.amount_cents
                )

        net_cash_flow_cents = (
            total_income_cents
            - total_expense_cents
        )

        return MonthlyReportSummary(
            month_start=month_start,
            month_end=month_end,
            total_income_cents=(
                total_income_cents
            ),
            total_expense_cents=(
                total_expense_cents
            ),
            net_cash_flow_cents=(
                net_cash_flow_cents
            ),
            transaction_count=transaction_count,
        )

    def get_category_spending(
        self,
        month: date | None = None,
        maximum_categories: int = 8,
    ) -> list[DashboardCategorySpendingItem]:
        """Return category spending for one calendar month."""

        month_start, month_end = (
            self._resolve_month_range(
                month
            )
        )

        return (
            self._spending_analytics_service
            .get_category_spending(
                start_date=month_start,
                end_date=month_end,
                maximum_categories=(
                    maximum_categories
                ),
            )
        )

    def get_budget_performance(
        self,
        month: date | None = None,
    ) -> list[BudgetProgress]:
        """Return progress for every active monthly budget."""

        return (
            self._budget_service
            .get_all_budget_progress(
                month=month
            )
        )

    def get_available_months(
        self,
    ) -> list[date]:
        """
        Return months containing normal financial transactions.

        Each returned date represents the first day of a month.
        Transfers are excluded because they do not represent
        income or spending.
        """

        available_months = {
            date(
                transaction.transaction_date.year,
                transaction.transaction_date.month,
                1,
            )
            for transaction
            in self._transaction_service.get_transactions()
            if not transaction.is_transfer
        }

        current_month = date(
            date.today().year,
            date.today().month,
            1,
        )

        available_months.add(
            current_month
        )

        return sorted(
            available_months,
            reverse=True,
        )

    def _resolve_month_range(
        self,
        month: date | None,
    ) -> tuple[date, date]:
        """Return the first and final dates of a month."""

        selected_month = month or date.today()

        month_start = date(
            selected_month.year,
            selected_month.month,
            1,
        )

        final_day = monthrange(
            selected_month.year,
            selected_month.month,
        )[1]

        month_end = date(
            selected_month.year,
            selected_month.month,
            final_day,
        )

        return (
            month_start,
            month_end,
        )