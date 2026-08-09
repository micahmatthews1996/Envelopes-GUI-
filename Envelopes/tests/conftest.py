from datetime import date
from types import SimpleNamespace

import pytest

from repositories.json_account_repository import JsonAccountRepository
from repositories.json_budget_repository import JsonBudgetRepository
from repositories.json_budget_rollover_repository import (
    JsonBudgetRolloverRepository,
)
from repositories.json_category_repository import JsonCategoryRepository
from repositories.json_savings_goal_allocation_repository import (
    JsonSavingsGoalAllocationRepository,
)
from repositories.json_savings_goal_repository import JsonSavingsGoalRepository
from repositories.json_transaction_repository import JsonTransactionRepository
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
from services.savings_goal_service import SavingsGoalService
from services.spending_analytics_service import SpendingAnalyticsService
from services.transaction_service import TransactionService


@pytest.fixture
def app(tmp_path):
    """Create an isolated Envelopes backend for one user workflow test."""

    account_repository = JsonAccountRepository(
        tmp_path / "accounts.json"
    )
    category_repository = JsonCategoryRepository(
        tmp_path / "categories.json"
    )
    transaction_repository = JsonTransactionRepository(
        tmp_path / "transactions.json"
    )
    savings_goal_repository = JsonSavingsGoalRepository(
        tmp_path / "savings_goals.json"
    )
    allocation_repository = JsonSavingsGoalAllocationRepository(
        tmp_path / "savings_goal_allocations.json"
    )
    budget_repository = JsonBudgetRepository(
        tmp_path / "budgets.json"
    )
    budget_rollover_repository = JsonBudgetRolloverRepository(
        tmp_path / "budget_rollovers.json"
    )

    account_service = AccountService(account_repository)
    account_service.seed_default_accounts()

    category_service = CategoryService(category_repository)
    category_service.seed_default_categories()

    transaction_service = TransactionService(
        transaction_repository=transaction_repository,
        account_repository=account_repository,
        category_repository=category_repository,
    )
    balance_service = BalanceService(transaction_repository)
    savings_goal_service = SavingsGoalService(
        savings_goal_repository
    )
    allocation_service = SavingsGoalAllocationService(
        allocation_repository=allocation_repository,
        savings_goal_service=savings_goal_service,
        account_service=account_service,
        balance_service=balance_service,
        transaction_service=transaction_service,
    )
    budget_service = BudgetService(
        budget_repository=budget_repository,
        category_service=category_service,
        transaction_service=transaction_service,
    )
    budget_rollover_service = BudgetRolloverService(
        rollover_repository=budget_rollover_repository,
        budget_service=budget_service,
        transaction_service=transaction_service,
        savings_goal_allocation_service=allocation_service,
    )
    analytics_service = SpendingAnalyticsService(
        transaction_service=transaction_service,
        category_service=category_service,
    )
    reports_service = ReportsService(
        transaction_service=transaction_service,
        spending_analytics_service=analytics_service,
        budget_service=budget_service,
    )
    dashboard_service = DashboardService(
        account_service=account_service,
        balance_service=balance_service,
        transaction_service=transaction_service,
        category_service=category_service,
        spending_analytics_service=analytics_service,
        savings_goal_service=savings_goal_service,
    )

    return SimpleNamespace(
        account_repository=account_repository,
        category_repository=category_repository,
        transaction_repository=transaction_repository,
        savings_goal_repository=savings_goal_repository,
        allocation_repository=allocation_repository,
        budget_repository=budget_repository,
        budget_rollover_repository=budget_rollover_repository,
        accounts=account_service,
        categories=category_service,
        transactions=transaction_service,
        balances=balance_service,
        goals=savings_goal_service,
        allocations=allocation_service,
        budgets=budget_service,
        rollovers=budget_rollover_service,
        analytics=analytics_service,
        reports=reports_service,
        dashboard=dashboard_service,
        today=date.today(),
    )


@pytest.fixture
def account_by_name(app):
    def lookup(name: str):
        return next(
            account
            for account in app.accounts.get_accounts()
            if account.name == name
        )

    return lookup


@pytest.fixture
def category_by_name(app):
    def lookup(name: str, category_type: str | None = None):
        return next(
            category
            for category in app.categories.get_categories(
                include_archived=True
            )
            if (
                category.name == name
                and (
                    category_type is None
                    or category.category_type == category_type
                )
            )
        )

    return lookup
