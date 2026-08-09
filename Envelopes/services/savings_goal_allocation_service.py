from datetime import date, datetime
from uuid import uuid4

from models.savings_goal import SavingsGoal
from models.savings_goal_allocation import (
    SavingsGoalAllocation,
)
from repositories.json_savings_goal_allocation_repository import (
    JsonSavingsGoalAllocationRepository,
)
from services.account_service import AccountService
from services.balance_service import BalanceService
from services.savings_goal_service import (
    SavingsGoalService,
)
from services.transaction_service import TransactionService


SAVINGS_ACCOUNT_TYPE = "Savings"


class SavingsGoalAllocationService:
    """Manages money allocated from savings to goals."""

    def __init__(
        self,
        allocation_repository: (
            JsonSavingsGoalAllocationRepository
        ),
        savings_goal_service: SavingsGoalService,
        account_service: AccountService,
        balance_service: BalanceService,
        transaction_service: TransactionService,
    ) -> None:
        self._allocation_repository = (
            allocation_repository
        )
        self._savings_goal_service = (
            savings_goal_service
        )
        self._account_service = account_service
        self._balance_service = balance_service
        self._transaction_service = transaction_service

    def get_allocations(
        self,
    ) -> list[SavingsGoalAllocation]:
        """Return all savings-goal allocations."""

        return self._allocation_repository.get_all()

    def get_goal_allocations(
        self,
        goal_id: str,
    ) -> list[SavingsGoalAllocation]:
        """Return all allocations assigned to one goal."""

        self._require_goal(goal_id)

        return self._allocation_repository.get_by_goal_id(
            goal_id
        )

    def get_goal_allocated_cents(
        self,
        goal_id: str,
    ) -> int:
        """Return the total allocated to one savings goal."""

        return sum(
            allocation.amount_cents
            for allocation
            in self.get_goal_allocations(goal_id)
        )

    def get_total_allocated_cents(
        self,
    ) -> int:
        """Return the total allocated across active goals."""

        active_goal_ids = {
            goal.goal_id
            for goal
            in self._savings_goal_service.get_goals()
        }

        return sum(
            allocation.amount_cents
            for allocation
            in self._allocation_repository.get_all()
            if allocation.goal_id in active_goal_ids
        )

    def get_unallocated_savings_cents(
        self,
    ) -> int:
        """Return savings not assigned to a goal."""

        return max(
            0,
            (
                self.get_savings_balance_cents()
                - self.get_total_allocated_cents()
            ),
        )

    def get_savings_balance_cents(
        self,
    ) -> int:
        """Return the combined balance of Savings accounts."""

        return sum(
            self._balance_service
            .get_current_balance_cents(account)
            for account in self._get_savings_accounts()
        )

    def create_allocation(
        self,
        goal_id: str,
        amount_cents: int,
        source_type: str = "manual",
        source_id: str = "",
        notes: str = "",
    ) -> SavingsGoalAllocation:
        """Allocate existing savings money to a goal."""

        goal = self._require_goal(goal_id)

        cleaned_source_type = (
            source_type.strip().casefold()
        )

        if cleaned_source_type not in {
            "manual",
            "transfer",
            "budget_rollover",
            "goal_transfer",
            "goal_release",
            "account_funding",
        }:
            raise ValueError(
                "Allocation source type is invalid."
            )

        if amount_cents <= 0:
            raise ValueError(
                "Allocation amount must be greater than zero."
            )

        remaining_goal_cents = max(
            0,
            (
                goal.target_amount_cents
                - self.get_goal_allocated_cents(
                    goal.goal_id
                )
            ),
        )

        if remaining_goal_cents <= 0:
            raise ValueError(
                "This savings goal is already complete."
            )

        if amount_cents > remaining_goal_cents:
            raise ValueError(
                "Allocation cannot exceed the amount "
                "remaining for this goal."
            )

        if (
            amount_cents
            > self.get_unallocated_savings_cents()
        ):
            raise ValueError(
                "Allocation cannot exceed the available "
                "unallocated savings balance."
            )

        allocation = SavingsGoalAllocation(
            allocation_id=str(uuid4()),
            goal_id=goal.goal_id,
            amount_cents=amount_cents,
            source_type=cleaned_source_type,
            source_id=source_id.strip(),
            notes=notes.strip(),
            created_at=datetime.now().astimezone(),
        )

        self._allocation_repository.add(allocation)

        return allocation

    def fund_goal_from_account(
        self,
        goal_id: str,
        source_account_id: str,
        savings_account_id: str,
        amount_cents: int,
        transaction_date: date,
        notes: str = "",
    ) -> SavingsGoalAllocation:
        """Fund a goal from any account, transferring to Savings when needed."""

        goal = self._require_goal(goal_id)
        accounts = {
            account.account_id: account
            for account in self._account_service.get_accounts()
        }
        source_account = accounts.get(source_account_id)
        savings_account = accounts.get(savings_account_id)

        if source_account is None:
            raise ValueError("The selected source account could not be found.")
        if savings_account is None or savings_account.account_type != "Savings":
            raise ValueError("Select a valid Savings account.")

        if amount_cents <= 0:
            raise ValueError("Funding amount must be greater than zero.")

        remaining_goal_cents = max(
            0,
            goal.target_amount_cents
            - self.get_goal_allocated_cents(goal.goal_id),
        )
        if amount_cents > remaining_goal_cents:
            raise ValueError(
                "Funding amount cannot exceed the amount "
                "remaining for this goal."
            )

        source_balance_cents = self._balance_service.get_current_balance_cents(
            source_account
        )
        if amount_cents > source_balance_cents:
            raise ValueError(
                "Funding amount cannot exceed the source account balance."
            )

        transfer_id = ""
        if source_account.account_id != savings_account.account_id:
            _source_tx, destination_tx = self._transaction_service.create_transfer(
                source_account_id=source_account.account_id,
                destination_account_id=savings_account.account_id,
                amount=amount_cents / 100,
                transaction_date=transaction_date,
                notes=(
                    f"Fund savings goal: {goal.name}"
                    + (f" — {notes.strip()}" if notes.strip() else "")
                ),
                is_cleared=True,
            )
            transfer_id = destination_tx.transfer_id

        try:
            allocation = self.create_allocation(
                goal_id=goal.goal_id,
                amount_cents=amount_cents,
                source_type="account_funding",
                source_id=(
                    transfer_id
                    if transfer_id
                    else savings_account.account_id
                ),
                notes=(
                    f"Funded from {source_account.name} "
                    f"into {savings_account.name}"
                    + (f" — {notes.strip()}" if notes.strip() else "")
                ),
            )
        except Exception:
            if transfer_id:
                self._transaction_service.delete_transfer(transfer_id)
            raise

        self.sync_goal_current_amount(goal.goal_id)
        return allocation

    def transfer_between_goals(
        self,
        source_goal_id: str,
        destination_goal_id: str,
        amount_cents: int,
        notes: str = "",
    ) -> tuple[
        SavingsGoalAllocation,
        SavingsGoalAllocation,
    ]:
        """
        Move allocated savings from one goal to another.

        This does not move money between accounts. It creates
        two linked allocation records so the reallocation has
        a complete audit trail.
        """

        source_goal = self._require_goal(
            source_goal_id
        )
        destination_goal = self._require_goal(
            destination_goal_id
        )

        if (
            source_goal.goal_id
            == destination_goal.goal_id
        ):
            raise ValueError(
                "Select two different savings goals."
            )

        if amount_cents <= 0:
            raise ValueError(
                "Transfer amount must be greater than zero."
            )

        source_allocated_cents = (
            self.get_goal_allocated_cents(
                source_goal.goal_id
            )
        )

        if amount_cents > source_allocated_cents:
            raise ValueError(
                "Transfer amount cannot exceed the money "
                "currently allocated to the source goal."
            )

        destination_allocated_cents = (
            self.get_goal_allocated_cents(
                destination_goal.goal_id
            )
        )

        destination_remaining_cents = max(
            0,
            (
                destination_goal.target_amount_cents
                - destination_allocated_cents
            ),
        )

        if destination_remaining_cents <= 0:
            raise ValueError(
                "The destination savings goal is already complete."
            )

        if amount_cents > destination_remaining_cents:
            raise ValueError(
                "Transfer amount cannot exceed the amount "
                "remaining for the destination goal."
            )

        cleaned_notes = notes.strip()
        transfer_id = str(uuid4())
        created_at = datetime.now().astimezone()

        source_allocation = SavingsGoalAllocation(
            allocation_id=str(uuid4()),
            goal_id=source_goal.goal_id,
            amount_cents=-amount_cents,
            source_type="goal_transfer",
            source_id=transfer_id,
            notes=cleaned_notes,
            created_at=created_at,
        )

        destination_allocation = SavingsGoalAllocation(
            allocation_id=str(uuid4()),
            goal_id=destination_goal.goal_id,
            amount_cents=amount_cents,
            source_type="goal_transfer",
            source_id=transfer_id,
            notes=cleaned_notes,
            created_at=created_at,
        )

        allocations = (
            self._allocation_repository.get_all()
        )

        allocations.extend(
            [
                source_allocation,
                destination_allocation,
            ]
        )

        self._allocation_repository.save_all(
            allocations
        )

        self.sync_goal_current_amount(
            source_goal.goal_id
        )
        self.sync_goal_current_amount(
            destination_goal.goal_id
        )

        return (
            source_allocation,
            destination_allocation,
        )

    def move_goal_money_to_account(
        self,
        source_goal_id: str,
        source_savings_account_id: str,
        destination_account_id: str,
        amount_cents: int,
        transaction_date: date,
        notes: str = "",
    ) -> SavingsGoalAllocation:
        """Move allocated goal money into any account.

        The allocation is reduced first. If the destination differs from
        the Savings account holding the money, Envelopes creates a real
        account transfer. If both accounts are the same, no fake transfer
        is created.
        """

        source_goal = self._require_goal(source_goal_id)

        accounts = {
            account.account_id: account
            for account in self._account_service.get_accounts()
        }

        source_savings_account = accounts.get(
            source_savings_account_id
        )
        destination_account = accounts.get(
            destination_account_id
        )

        if (
            source_savings_account is None
            or source_savings_account.account_type != "Savings"
        ):
            raise ValueError(
                "Select a valid Savings account that holds the goal money."
            )

        if destination_account is None:
            raise ValueError(
                "The selected destination account could not be found."
            )

        if amount_cents <= 0:
            raise ValueError(
                "Transfer amount must be greater than zero."
            )

        source_allocated_cents = self.get_goal_allocated_cents(
            source_goal.goal_id
        )

        if amount_cents > source_allocated_cents:
            raise ValueError(
                "Transfer amount cannot exceed the money "
                "currently allocated to the source goal."
            )

        source_account_balance_cents = (
            self._balance_service.get_current_balance_cents(
                source_savings_account
            )
        )

        if amount_cents > source_account_balance_cents:
            raise ValueError(
                "Transfer amount cannot exceed the selected "
                "Savings account balance."
            )

        release_id = str(uuid4())
        transfer_id = ""
        cleaned_notes = notes.strip()

        release = SavingsGoalAllocation(
            allocation_id=str(uuid4()),
            goal_id=source_goal.goal_id,
            amount_cents=-amount_cents,
            source_type="goal_release",
            source_id=release_id,
            notes=(
                f"Released from goal to {destination_account.name}"
                + (
                    f" — {cleaned_notes}"
                    if cleaned_notes
                    else ""
                )
            ),
            created_at=datetime.now().astimezone(),
        )

        original_allocations = (
            self._allocation_repository.get_all()
        )
        updated_allocations = [
            *original_allocations,
            release,
        ]

        self._allocation_repository.save_all(
            updated_allocations
        )

        try:
            if (
                source_savings_account.account_id
                != destination_account.account_id
            ):
                _source_transaction, destination_transaction = (
                    self._transaction_service.create_transfer(
                        source_account_id=(
                            source_savings_account.account_id
                        ),
                        destination_account_id=(
                            destination_account.account_id
                        ),
                        amount=amount_cents / 100,
                        transaction_date=transaction_date,
                        notes=(
                            f"Move money from savings goal: "
                            f"{source_goal.name}"
                            + (
                                f" — {cleaned_notes}"
                                if cleaned_notes
                                else ""
                            )
                        ),
                        is_cleared=True,
                    )
                )
                transfer_id = (
                    destination_transaction.transfer_id
                )

            self.sync_goal_current_amount(
                source_goal.goal_id
            )

        except Exception:
            self._allocation_repository.save_all(
                original_allocations
            )
            if transfer_id:
                self._transaction_service.delete_transfer(
                    transfer_id
                )
            self.sync_goal_current_amount(
                source_goal.goal_id
            )
            raise

        return release

    def release_goal_money_to_savings_account(
        self,
        source_goal_id: str,
        destination_account_id: str,
        amount_cents: int,
        notes: str = "",
    ) -> SavingsGoalAllocation:
        """Backward-compatible wrapper for release to the same Savings account."""

        return self.move_goal_money_to_account(
            source_goal_id=source_goal_id,
            source_savings_account_id=destination_account_id,
            destination_account_id=destination_account_id,
            amount_cents=amount_cents,
            transaction_date=date.today(),
            notes=notes,
        )

    def replace_source_allocation(
        self,
        goal_id: str | None,
        amount_cents: int,
        source_type: str,
        source_id: str,
        notes: str = "",
    ) -> SavingsGoalAllocation | None:
        """Replace the allocation created by one source."""

        cleaned_source_type = (
            source_type.strip().casefold()
        )
        cleaned_source_id = source_id.strip()

        if not cleaned_source_id:
            raise ValueError(
                "The allocation source could not be identified."
            )

        original_allocations = (
            self._allocation_repository.get_all()
        )

        existing_ids = {
            allocation.allocation_id
            for allocation
            in self._allocation_repository.get_by_source(
                cleaned_source_type,
                cleaned_source_id,
            )
        }

        remaining_allocations = [
            allocation
            for allocation in original_allocations
            if allocation.allocation_id
            not in existing_ids
        ]

        self._allocation_repository.save_all(
            remaining_allocations
        )

        if goal_id is None or amount_cents <= 0:
            return None

        try:
            return self.create_allocation(
                goal_id=goal_id,
                amount_cents=amount_cents,
                source_type=cleaned_source_type,
                source_id=cleaned_source_id,
                notes=notes,
            )
        except Exception:
            self._allocation_repository.save_all(
                original_allocations
            )
            raise

    def delete_allocations_for_source(
        self,
        source_type: str,
        source_id: str,
    ) -> None:
        """Delete allocations created by one source."""

        self._allocation_repository.delete_by_source(
            source_type=source_type.strip().casefold(),
            source_id=source_id.strip(),
        )

    def delete_allocations_for_goal(
        self,
        goal_id: str,
    ) -> None:
        """Delete all allocations assigned to one goal."""

        self._allocation_repository.delete_by_goal_id(
            goal_id
        )

    def sync_goal_current_amount(
        self,
        goal_id: str,
    ) -> SavingsGoal:
        """Sync one goal's stored amount from allocations."""

        goal = self._require_goal(goal_id)

        goal.current_amount_cents = (
            self.get_goal_allocated_cents(goal_id)
        )

        self._savings_goal_service.save_goal(goal)

        return goal

    def sync_all_goal_current_amounts(
        self,
    ) -> None:
        """Sync every active goal from allocation records."""

        for goal in self._savings_goal_service.get_goals():
            self.sync_goal_current_amount(
                goal.goal_id
            )

    def _require_goal(
        self,
        goal_id: str,
    ) -> SavingsGoal:
        """Return a validated active savings goal."""

        goal = self._savings_goal_service.get_goal(
            goal_id
        )

        if goal is None:
            raise ValueError(
                "The selected savings goal could not be found."
            )

        if goal.is_archived:
            raise ValueError(
                "Archived savings goals cannot receive allocations."
            )

        return goal

    def get_all_accounts(self) -> list:
        """Return accounts available as direct goal-funding sources."""

        return self._account_service.get_accounts()

    def get_savings_accounts(self) -> list:
        """Return Savings accounts available as goal-release destinations."""

        return self._get_savings_accounts()

    def _get_savings_accounts(self) -> list:
        """Return accounts whose permanent type is Savings."""

        return [
            account
            for account in self._account_service.get_accounts()
            if account.account_type == SAVINGS_ACCOUNT_TYPE
        ]