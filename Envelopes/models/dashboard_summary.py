from dataclasses import dataclass
from datetime import date


@dataclass(slots=True)
class DashboardTransactionItem:
    """One recent transaction displayed on the Dashboard."""

    transaction_id: str
    payee: str
    category_name: str
    transaction_date: date
    amount_cents: int


@dataclass(slots=True)
class DashboardAccountItem:
    """One account balance displayed on the Dashboard."""

    account_id: str
    account_name: str
    current_balance_cents: int


@dataclass(slots=True)
class DashboardCategorySpendingItem:
    """Total spending for one category."""

    category_name: str
    amount_cents: int
    color: str


@dataclass(slots=True)
class DashboardSavingsGoalItem:
    """One savings goal displayed on the Dashboard."""

    goal_id: str
    name: str
    current_amount_cents: int
    target_amount_cents: int
    remaining_amount_cents: int
    progress_percent: int
    target_date: date | None
    is_completed: bool


@dataclass(slots=True)
class DashboardSummary:
    """Summary information displayed on the Dashboard."""

    net_worth_cents: int
    total_income_cents: int
    total_expense_cents: int
    total_savings_cents: int

    recent_transactions: list[
        DashboardTransactionItem
    ]

    accounts: list[
        DashboardAccountItem
    ]

    category_spending: list[
        DashboardCategorySpendingItem
    ]

    savings_goals: list[
        DashboardSavingsGoalItem
    ]