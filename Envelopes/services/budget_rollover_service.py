from datetime import date, datetime
from uuid import uuid4

from models.budget_rollover_record import BudgetRolloverRecord
from repositories.json_budget_rollover_repository import (
    JsonBudgetRolloverRepository,
)
from services.budget_service import BudgetRolloverItem, BudgetService
from services.savings_goal_allocation_service import (
    SavingsGoalAllocationService,
)
from services.transaction_service import TransactionService


class BudgetRolloverService:
    """Coordinates rollover actions and prevents duplicate processing."""

    VALID_DESTINATIONS = {
        "budget",
        "goal",
        "savings",
        "unassigned",
    }

    def __init__(
        self,
        rollover_repository: JsonBudgetRolloverRepository,
        budget_service: BudgetService,
        transaction_service: TransactionService,
        savings_goal_allocation_service: SavingsGoalAllocationService,
    ) -> None:
        self._repository = rollover_repository
        self._budget_service = budget_service
        self._transaction_service = transaction_service
        self._allocation_service = savings_goal_allocation_service

    def get_available_items(
        self,
        destination_month: date,
    ) -> list[BudgetRolloverItem]:
        """Return positive rollover items that have not been processed."""
        selected = self._budget_service.normalize_month(destination_month)
        return [
            item
            for item in self._budget_service.get_rollover_items(selected)
            if (
                item.unused_cents > 0
                and not self.is_processed(
                    item.budget.budget_id,
                    selected,
                )
            )
        ]

    def is_processed(
        self,
        source_budget_id: str,
        destination_month: date,
    ) -> bool:
        selected = self._budget_service.normalize_month(destination_month)
        return (
            self._repository.get_processed(
                source_budget_id,
                selected,
            )
            is not None
        )

    def process_choice(
        self,
        item: BudgetRolloverItem,
        destination_month: date,
        destination_type: str,
        source_account_id: str = "",
        savings_account_id: str = "",
        goal_id: str = "",
    ) -> BudgetRolloverRecord:
        """Apply one rollover choice and permanently record the decision."""
        selected = self._budget_service.normalize_month(destination_month)
        source_month = self._budget_service.previous_month(selected)
        destination = destination_type.strip().casefold()

        if destination not in self.VALID_DESTINATIONS:
            raise ValueError("The selected rollover destination is invalid.")

        if item.unused_cents <= 0:
            raise ValueError(
                "Only positive unused budget amounts can be rolled over."
            )

        if item.budget.budget_month != source_month:
            raise ValueError(
                "The rollover source budget does not belong to "
                "the previous month."
            )

        if self.is_processed(item.budget.budget_id, selected):
            raise ValueError(
                f"{item.category_name} has already been processed "
                f"for {selected.strftime('%B %Y')}."
            )

        result_id = ""
        saved_goal_id = ""

        if destination == "budget":
            created_budget = self._budget_service.create_rollover_budget(
                item.budget,
                selected,
                item.unused_cents,
            )
            result_id = created_budget.budget_id

        elif destination in {"savings", "goal"}:
            if not source_account_id or not savings_account_id:
                raise ValueError(
                    "Savings rollover requires a source account "
                    "and a Savings account."
                )

            if destination == "goal" and not goal_id:
                raise ValueError(
                    "A savings goal is required for this rollover."
                )

            _source_transaction, destination_transaction = (
                self._transaction_service.create_transfer(
                    source_account_id=source_account_id,
                    destination_account_id=savings_account_id,
                    amount=item.unused_cents / 100,
                    transaction_date=selected,
                    notes=(
                        "Budget rollover from "
                        f"{item.category_name} "
                        f"({source_month.strftime('%B %Y')})"
                    ),
                    is_cleared=True,
                )
            )
            result_id = destination_transaction.transfer_id

            if destination == "goal":
                self._allocation_service.create_allocation(
                    goal_id=goal_id,
                    amount_cents=item.unused_cents,
                    source_type="budget_rollover",
                    source_id=destination_transaction.transfer_id,
                    notes=(
                        "Budget rollover from "
                        f"{item.category_name} "
                        f"({source_month.strftime('%B %Y')})"
                    ),
                )
                self._allocation_service.sync_goal_current_amount(goal_id)
                saved_goal_id = goal_id

        record = BudgetRolloverRecord(
            rollover_id=str(uuid4()),
            source_budget_id=item.budget.budget_id,
            source_month=source_month,
            destination_month=selected,
            amount_cents=item.unused_cents,
            destination_type=destination,
            goal_id=saved_goal_id,
            result_id=result_id,
            created_at=datetime.now().astimezone(),
        )
        self._repository.add(record)
        return record
