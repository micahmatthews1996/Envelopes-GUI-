from calendar import monthrange
from dataclasses import dataclass
from datetime import date, datetime
from uuid import uuid4

from models.budget import Budget
from repositories.json_budget_repository import JsonBudgetRepository
from services.category_service import CategoryService
from services.transaction_service import TransactionService
from utils.money import dollars_to_cents


@dataclass(slots=True)
class BudgetProgress:
    budget: Budget
    category_name: str
    category_color: str
    spent_cents: int
    remaining_cents: int
    progress_percent: int
    is_overspent: bool


@dataclass(slots=True)
class BudgetRolloverItem:
    budget: Budget
    category_name: str
    spent_cents: int
    unused_cents: int


class BudgetService:
    """Provides month-specific budget business operations."""

    def __init__(self, budget_repository: JsonBudgetRepository, category_service: CategoryService, transaction_service: TransactionService) -> None:
        self._budget_repository = budget_repository
        self._category_service = category_service
        self._transaction_service = transaction_service

    @staticmethod
    def normalize_month(month: date | None = None) -> date:
        value = month or date.today()
        return date(value.year, value.month, 1)

    @staticmethod
    def previous_month(month: date) -> date:
        return date(month.year - 1, 12, 1) if month.month == 1 else date(month.year, month.month - 1, 1)

    @staticmethod
    def next_month(month: date) -> date:
        return date(month.year + 1, 1, 1) if month.month == 12 else date(month.year, month.month + 1, 1)

    def get_budgets(self, include_archived: bool = False, month: date | None = None) -> list[Budget]:
        selected = self.normalize_month(month)
        budgets = [b for b in self._budget_repository.get_all() if b.budget_month == selected]
        if not include_archived:
            budgets = [b for b in budgets if not b.is_archived]
        return sorted(budgets, key=lambda b: self._category_name(b.category_id).casefold())

    def get_budget_by_id(self, budget_id: str) -> Budget:
        budget = self._budget_repository.get_by_id(budget_id)
        if budget is None:
            raise ValueError("The selected budget could not be found.")
        return budget

    def create_budget(self, category_id: str, monthly_limit: float, month: date | None = None) -> Budget:
        category = self._require_expense_category(category_id)
        selected = self.normalize_month(month)
        if self._budget_repository.get_by_category_id(category.category_id, selected) is not None:
            raise ValueError("This category already has an active budget for the selected month.")
        now = datetime.now().astimezone()
        budget = Budget(str(uuid4()), category.category_id, self._validate_monthly_limit(monthly_limit), selected, False, now, now, "manual")
        self._budget_repository.add(budget)
        return budget

    def update_budget(self, budget_id: str, category_id: str, monthly_limit: float) -> Budget:
        existing = self.get_budget_by_id(budget_id)
        category = self._require_expense_category(category_id)
        duplicate = self._budget_repository.get_by_category_id(category.category_id, existing.budget_month)
        if duplicate is not None and duplicate.budget_id != existing.budget_id:
            raise ValueError("This category already has an active budget for the selected month.")
        updated = Budget(existing.budget_id, category.category_id, self._validate_monthly_limit(monthly_limit), existing.budget_month, existing.is_archived, existing.created_at, datetime.now().astimezone(), existing.origin)
        self._budget_repository.update(updated)
        return updated

    def archive_budget(self, budget_id: str) -> Budget:
        budget = self.get_budget_by_id(budget_id)
        archived = Budget(budget.budget_id, budget.category_id, budget.monthly_limit_cents, budget.budget_month, True, budget.created_at, datetime.now().astimezone(), budget.origin)
        self._budget_repository.update(archived); return archived

    def restore_budget(self, budget_id: str) -> Budget:
        budget = self.get_budget_by_id(budget_id)
        active = self._budget_repository.get_by_category_id(budget.category_id, budget.budget_month)
        if active is not None and active.budget_id != budget.budget_id:
            raise ValueError("This category already has an active budget for the selected month.")
        restored = Budget(budget.budget_id, budget.category_id, budget.monthly_limit_cents, budget.budget_month, False, budget.created_at, datetime.now().astimezone(), budget.origin)
        self._budget_repository.update(restored); return restored

    def delete_budget(self, budget_id: str) -> None:
        self.get_budget_by_id(budget_id); self._budget_repository.delete(budget_id)

    def get_budget_progress(self, budget: Budget, month: date | None = None) -> BudgetProgress:
        selected = self.normalize_month(month or budget.budget_month)
        category = self._category_service.get_category_by_id(budget.category_id)
        month_start, month_end = self._resolve_month_range(selected)
        spent = 0
        for transaction in self._transaction_service.get_transactions():
            if transaction.is_transfer or transaction.category_id != budget.category_id or transaction.amount_cents >= 0:
                continue
            if month_start <= transaction.transaction_date <= month_end:
                spent += abs(transaction.amount_cents)
        remaining = budget.monthly_limit_cents - spent
        percent = round(spent / budget.monthly_limit_cents * 100) if budget.monthly_limit_cents > 0 else 0
        return BudgetProgress(budget, category.name, category.color, spent, remaining, max(0, percent), spent > budget.monthly_limit_cents)

    def get_all_budget_progress(self, month: date | None = None) -> list[BudgetProgress]:
        selected = self.normalize_month(month)
        return [self.get_budget_progress(b, selected) for b in self.get_budgets(month=selected)]

    def get_rollover_items(self, destination_month: date) -> list[BudgetRolloverItem]:
        source = self.previous_month(self.normalize_month(destination_month))
        items = []
        for budget in self.get_budgets(month=source):
            progress = self.get_budget_progress(budget, source)
            items.append(BudgetRolloverItem(budget, progress.category_name, progress.spent_cents, max(0, progress.remaining_cents)))
        return items

    def create_rollover_budget(
        self,
        source_budget: Budget,
        destination_month: date,
        unused_cents: int,
    ) -> Budget:
        """Create rollover budget or add rollover to a copied budget.

        A copied destination budget may safely receive the unused amount
        because its regular limit came directly from the same previous
        month. Manually created budgets are never changed implicitly.
        """
        selected = self.normalize_month(destination_month)

        if unused_cents < 0:
            raise ValueError("Rollover amount cannot be negative.")

        existing = self._budget_repository.get_by_category_id(
            source_budget.category_id,
            selected,
        )

        if existing is not None:
            if existing.origin != "copied":
                raise ValueError(
                    f"{self._category_name(source_budget.category_id)} "
                    f"already has a budget for "
                    f"{selected.strftime('%B %Y')}. "
                    "Only a budget copied from the previous month can "
                    "receive rollover automatically."
                )

            updated = Budget(
                budget_id=existing.budget_id,
                category_id=existing.category_id,
                monthly_limit_cents=(
                    existing.monthly_limit_cents + unused_cents
                ),
                budget_month=existing.budget_month,
                is_archived=existing.is_archived,
                created_at=existing.created_at,
                updated_at=datetime.now().astimezone(),
                origin="rollover",
            )
            self._budget_repository.update(updated)
            return updated

        now = datetime.now().astimezone()
        budget = Budget(
            budget_id=str(uuid4()),
            category_id=source_budget.category_id,
            monthly_limit_cents=(
                source_budget.monthly_limit_cents + unused_cents
            ),
            budget_month=selected,
            is_archived=False,
            created_at=now,
            updated_at=now,
            origin="rollover",
        )
        self._budget_repository.add(budget)
        return budget

    def copy_previous_month_budgets(
        self,
        destination_month: date,
    ) -> tuple[int, int]:
        """Copy regular budget limits from the previous month.

        Existing active destination-month budgets are left unchanged.
        Returns ``(copied_count, skipped_count)``.
        """
        selected = self.normalize_month(destination_month)
        source = self.previous_month(selected)
        source_budgets = self.get_budgets(month=source)

        copied_count = 0
        skipped_count = 0

        for source_budget in source_budgets:
            existing = self._budget_repository.get_by_category_id(
                source_budget.category_id,
                selected,
            )
            if existing is not None:
                skipped_count += 1
                continue

            now = datetime.now().astimezone()
            copied_budget = Budget(
                budget_id=str(uuid4()),
                category_id=source_budget.category_id,
                monthly_limit_cents=source_budget.monthly_limit_cents,
                budget_month=selected,
                is_archived=False,
                created_at=now,
                updated_at=now,
                origin="copied",
            )
            self._budget_repository.add(copied_budget)
            copied_count += 1

        return copied_count, skipped_count

    def _require_expense_category(self, category_id: str):
        category = self._category_service.get_category_by_id(category_id)
        if category.is_archived: raise ValueError("Archived categories cannot be budgeted.")
        if category.category_type != "Expense": raise ValueError("Budgets can only use expense categories.")
        return category

    def _validate_monthly_limit(self, monthly_limit: float) -> int:
        cents = dollars_to_cents(monthly_limit)
        if cents <= 0: raise ValueError("Monthly budget must be greater than zero.")
        return cents

    def _resolve_month_range(self, month: date | None) -> tuple[date, date]:
        selected = self.normalize_month(month)
        return selected, date(selected.year, selected.month, monthrange(selected.year, selected.month)[1])

    def _category_name(self, category_id: str) -> str:
        try: return self._category_service.get_category_by_id(category_id).name
        except ValueError: return "Unknown Category"
