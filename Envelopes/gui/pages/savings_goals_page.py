from datetime import date

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from gui.dialogs.savings_allocation_dialog import (
    SavingsAllocationDialog,
)
from gui.dialogs.goal_transfer_dialog import (
    GoalTransferDialog,
)
from gui.dialogs.goal_funding_dialog import GoalFundingDialog
from gui.dialogs.savings_goal_dialog import (
    DELETE_RESULT,
    SavingsGoalDialog,
)
from gui.widgets.empty_state import EmptyState
from gui.widgets.page_header import PageHeader
from gui.widgets.savings_goal_card import (
    SavingsGoalCard,
)
from models.savings_goal import SavingsGoal
from services.savings_goal_allocation_service import (
    SavingsGoalAllocationService,
)
from services.savings_goal_service import (
    SavingsGoalService,
)


class SavingsGoalsPage(QWidget):
    """Displays and manages the user's savings goals."""

    def __init__(
        self,
        savings_goal_service: SavingsGoalService,
        savings_goal_allocation_service: (
            SavingsGoalAllocationService
        ),
    ) -> None:
        super().__init__()

        self._service = savings_goal_service
        self._allocation_service = (
            savings_goal_allocation_service
        )

        self.setObjectName("page")

        self._create_interface()
        self.refresh()

    def _create_interface(self) -> None:
        """Create the Savings Goals page interface."""

        add_goal_button = QPushButton(
            "+ Add Savings Goal"
        )
        add_goal_button.setObjectName(
            "primaryButton"
        )
        add_goal_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        add_goal_button.clicked.connect(
            self._open_create_goal_dialog
        )

        page_header = PageHeader(
            title="Savings Goals",
            description=(
                "Create goals and track your progress "
                "toward important financial milestones."
            ),
            action_widget=add_goal_button,
        )

        self._goals_container = QWidget()
        self._goals_container.setObjectName(
            "savingsGoalsContainer"
        )

        self._goals_layout = QVBoxLayout(
            self._goals_container
        )
        self._goals_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        self._goals_layout.setSpacing(16)
        self._goals_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop
        )

        content = QWidget()
        content.setObjectName(
            "savingsGoalsContent"
        )

        content_layout = QVBoxLayout(
            content
        )
        content_layout.setContentsMargins(
            40,
            32,
            40,
            32,
        )
        content_layout.setSpacing(24)
        content_layout.addWidget(
            page_header
        )
        content_layout.addWidget(
            self._goals_container
        )
        content_layout.addStretch()

        scroll_area = QScrollArea()
        scroll_area.setObjectName(
            "savingsGoalsScrollArea"
        )
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(
            QFrame.Shape.NoFrame
        )
        scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        scroll_area.setWidget(
            content
        )

        page_layout = QVBoxLayout(self)
        page_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        page_layout.setSpacing(0)
        page_layout.addWidget(
            scroll_area
        )

    def refresh(self) -> None:
        """Reload and display all active savings goals."""

        self._clear_layout()

        try:
            goals = self._service.get_goals()
        except RuntimeError as error:
            QMessageBox.critical(
                self,
                "Unable to Load Savings Goals",
                str(error),
            )
            return

        if not goals:
            self._show_empty_state()
            return

        for goal in goals:
            goal_card = SavingsGoalCard(
                goal_name=goal.name,
                current_amount_cents=(
                    goal.current_amount_cents
                ),
                target_amount_cents=(
                    goal.target_amount_cents
                ),
                progress_percent=(
                    goal.progress_percent
                ),
            )

            goal_card.fund_goal_requested.connect(
                lambda selected_goal=goal: (
                    self._open_fund_goal_dialog(
                        selected_goal
                    )
                )
            )

            goal_card.edit_requested.connect(
                lambda selected_goal=goal: (
                    self._open_edit_goal_dialog(
                        selected_goal
                    )
                )
            )

            goal_card.move_money_requested.connect(
                lambda selected_goal=goal: (
                    self._open_goal_transfer_dialog(
                        selected_goal
                    )
                )
            )

            self._goals_layout.addWidget(
                goal_card
            )

    def _show_empty_state(self) -> None:
        """Display a message when no savings goals exist."""

        empty_state = EmptyState(
            title="No savings goals yet",
            description=(
                "Create a goal for an emergency fund, "
                "vacation, major purchase, or another "
                "financial priority."
            ),
            action_text="+ Add Savings Goal",
        )

        empty_state.action_button().clicked.connect(
            self._open_create_goal_dialog
        )

        self._goals_layout.addWidget(
            empty_state
        )

    def _open_create_goal_dialog(self) -> None:
        """Open the dialog for creating a savings goal."""

        dialog = SavingsGoalDialog(
            parent=self
        )

        while True:
            result = dialog.exec()

            if result != QDialog.DialogCode.Accepted:
                return

            (
                goal_name,
                target_amount_cents,
                target_date,
            ) = dialog.get_goal_data()

            try:
                created_goal = self._service.create_goal(
                    name=goal_name,
                    target_amount_cents=(
                        target_amount_cents
                    ),
                    target_date=target_date,
                )
            except ValueError as error:
                dialog.show_error(
                    str(error)
                )
                continue
            except RuntimeError as error:
                QMessageBox.critical(
                    self,
                    "Unable to Create Savings Goal",
                    str(error),
                )
                return

            self._offer_existing_savings_allocation(
                created_goal
            )
            self.refresh()
            return

    def _offer_existing_savings_allocation(
        self,
        goal: SavingsGoal,
    ) -> None:
        """Offer to allocate available savings to a new goal."""

        try:
            available_amount_cents = (
                self._allocation_service
                .get_unallocated_savings_cents()
            )
        except RuntimeError as error:
            QMessageBox.critical(
                self,
                "Unable to Check Savings",
                str(error),
            )
            return

        available_amount_cents = min(
            available_amount_cents,
            goal.target_amount_cents,
        )

        if available_amount_cents <= 0:
            return

        response = QMessageBox.question(
            self,
            "Allocate Existing Savings",
            (
                "You have unallocated money available "
                "in your Savings account.\n\n"
                "Would you like to allocate some of it "
                f'to "{goal.name}" now?'
            ),
            (
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No
            ),
            QMessageBox.StandardButton.Yes,
        )

        if response != QMessageBox.StandardButton.Yes:
            return

        allocation_dialog = SavingsAllocationDialog(
            savings_goal_service=self._service,
            available_amount_cents=(
                available_amount_cents
            ),
            parent=self,
            selected_goal_id=goal.goal_id,
            initial_amount_cents=(
                available_amount_cents
            ),
        )

        while allocation_dialog.exec():
            (
                goal_id,
                amount_cents,
                notes,
            ) = allocation_dialog.get_allocation_data()

            try:
                self._allocation_service.create_allocation(
                    goal_id=goal_id,
                    amount_cents=amount_cents,
                    source_type="manual",
                    notes=notes,
                )
                self._allocation_service\
                    .sync_goal_current_amount(
                        goal_id
                    )
            except ValueError as error:
                allocation_dialog.show_error(
                    str(error)
                )
                continue
            except RuntimeError as error:
                QMessageBox.critical(
                    self,
                    "Unable to Allocate Savings",
                    str(error),
                )
                return

            return

    def _open_fund_goal_dialog(
        self,
        goal: SavingsGoal,
    ) -> None:
        """Fund a savings goal directly from an account."""

        try:
            accounts = self._allocation_service.get_all_accounts()
        except RuntimeError as error:
            QMessageBox.critical(
                self,
                "Unable to Load Accounts",
                str(error),
            )
            return

        if not accounts:
            QMessageBox.information(
                self,
                "Account Required",
                "Create an account before funding a savings goal.",
            )
            return

        if not any(
            account.account_type == "Savings"
            for account in accounts
        ):
            QMessageBox.information(
                self,
                "Savings Account Required",
                (
                    "Create a Savings account before funding "
                    "a savings goal."
                ),
            )
            return

        dialog = GoalFundingDialog(
            goal=goal,
            accounts=accounts,
            parent=self,
        )

        while dialog.exec():
            (
                source_account_id,
                savings_account_id,
                amount_cents,
                notes,
            ) = dialog.get_funding_data()

            try:
                self._allocation_service.fund_goal_from_account(
                    goal_id=goal.goal_id,
                    source_account_id=source_account_id,
                    savings_account_id=savings_account_id,
                    amount_cents=amount_cents,
                    transaction_date=date.today(),
                    notes=notes,
                )
            except ValueError as error:
                dialog.show_error(str(error))
                continue
            except RuntimeError as error:
                QMessageBox.critical(
                    self,
                    "Unable to Fund Goal",
                    str(error),
                )
                return

            self.refresh()
            return

    def _open_goal_transfer_dialog(
        self,
        source_goal: SavingsGoal,
    ) -> None:
        """Move allocated savings to another goal or Savings account."""

        try:
            goals = self._service.get_goals()
            accounts = (
                self._allocation_service.get_all_accounts()
            )
        except RuntimeError as error:
            QMessageBox.critical(
                self,
                "Unable to Load Savings Destinations",
                str(error),
            )
            return

        destination_goals = [
            goal
            for goal in goals
            if (
                goal.goal_id != source_goal.goal_id
                and not goal.is_completed
            )
        ]

        if not destination_goals and not accounts:
            QMessageBox.information(
                self,
                "Destination Required",
                (
                    "Create a Savings account or another incomplete "
                    "savings goal before moving money."
                ),
            )
            return

        dialog = GoalTransferDialog(
            goals=goals,
            accounts=accounts,
            source_goal=source_goal,
            parent=self,
        )

        while dialog.exec():
            (
                source_goal_id,
                destination_type,
                source_savings_account_id,
                destination_id,
                amount_cents,
                notes,
            ) = dialog.get_transfer_data()

            try:
                if destination_type == "goal":
                    self._allocation_service.transfer_between_goals(
                        source_goal_id=source_goal_id,
                        destination_goal_id=destination_id,
                        amount_cents=amount_cents,
                        notes=notes,
                    )
                else:
                    self._allocation_service.move_goal_money_to_account(
                        source_goal_id=source_goal_id,
                        source_savings_account_id=(
                            source_savings_account_id
                        ),
                        destination_account_id=destination_id,
                        amount_cents=amount_cents,
                        transaction_date=date.today(),
                        notes=notes,
                    )
            except ValueError as error:
                dialog.show_error(str(error))
                continue
            except RuntimeError as error:
                QMessageBox.critical(
                    self,
                    "Unable to Move Goal Money",
                    str(error),
                )
                return

            self.refresh()
            return

    def _open_edit_goal_dialog(
        self,
        goal: SavingsGoal,
    ) -> None:
        """Open the dialog for editing or deleting a savings goal."""

        dialog = SavingsGoalDialog(
            parent=self,
            goal=goal,
        )

        while True:
            result = dialog.exec()

            if result == DELETE_RESULT:
                self._archive_goal(
                    goal
                )
                return

            if result != QDialog.DialogCode.Accepted:
                return

            (
                goal_name,
                target_amount_cents,
                target_date,
            ) = dialog.get_goal_data()

            goal.name = goal_name
            goal.target_amount_cents = (
                target_amount_cents
            )
            goal.target_date = target_date

            try:
                self._service.save_goal(
                    goal
                )
            except ValueError as error:
                dialog.show_error(
                    str(error)
                )
                continue
            except RuntimeError as error:
                QMessageBox.critical(
                    self,
                    "Unable to Update Savings Goal",
                    str(error),
                )
                return

            self.refresh()
            return

    def _archive_goal(
        self,
        goal: SavingsGoal,
    ) -> None:
        """Archive a confirmed savings goal."""

        try:
            self._allocation_service.delete_allocations_for_goal(
                goal.goal_id
            )
            self._service.archive_goal(
                goal.goal_id
            )
        except ValueError as error:
            QMessageBox.warning(
                self,
                "Unable to Delete Savings Goal",
                str(error),
            )
            return
        except RuntimeError as error:
            QMessageBox.critical(
                self,
                "Unable to Delete Savings Goal",
                str(error),
            )
            return

        self.refresh()

    def _clear_layout(self) -> None:
        """Remove all currently displayed goal widgets."""

        while self._goals_layout.count():
            layout_item = (
                self._goals_layout.takeAt(0)
            )

            widget = layout_item.widget()

            if widget is not None:
                widget.deleteLater()