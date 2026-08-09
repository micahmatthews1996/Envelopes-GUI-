import json
from datetime import date
from pathlib import Path

from models.budget import Budget


class JsonBudgetRepository:
    """Stores monthly budgets in a JSON file."""

    def __init__(self, file_path: Path) -> None:
        self._file_path = file_path
        if not self._file_path.exists():
            self._write_budgets([])

    def get_all(self) -> list[Budget]:
        with open(self._file_path, "r", encoding="utf-8") as file:
            budget_data = json.load(file)
        budgets = [Budget.from_dictionary(item) for item in budget_data]
        # Persist legacy month migration immediately.
        if any(("budget_month" not in item or "origin" not in item) for item in budget_data):
            self._write_budgets(budgets)
        return budgets

    def get_by_id(self, budget_id: str) -> Budget | None:
        return next((b for b in self.get_all() if b.budget_id == budget_id), None)

    def get_by_category_id(self, category_id: str, month: date | None = None) -> Budget | None:
        selected = month or date.today()
        for budget in self.get_all():
            if (budget.category_id == category_id and not budget.is_archived
                    and budget.budget_month.year == selected.year
                    and budget.budget_month.month == selected.month):
                return budget
        return None

    def add(self, budget: Budget) -> None:
        budgets = self.get_all(); budgets.append(budget); self._write_budgets(budgets)

    def update(self, updated_budget: Budget) -> None:
        budgets = self.get_all()
        for index, budget in enumerate(budgets):
            if budget.budget_id == updated_budget.budget_id:
                budgets[index] = updated_budget; self._write_budgets(budgets); return
        raise ValueError("The selected budget could not be found.")

    def delete(self, budget_id: str) -> None:
        budgets = self.get_all()
        remaining = [b for b in budgets if b.budget_id != budget_id]
        if len(remaining) == len(budgets):
            raise ValueError("The selected budget could not be found.")
        self._write_budgets(remaining)

    def save_all(self, budgets: list[Budget]) -> None:
        self._write_budgets(budgets)

    def _write_budgets(self, budgets: list[Budget]) -> None:
        self._file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._file_path, "w", encoding="utf-8") as file:
            json.dump([b.to_dictionary() for b in budgets], file, indent=4)
