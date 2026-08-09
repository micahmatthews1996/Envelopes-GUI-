from datetime import date

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QDialog,
    QFrame,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from gui.dialogs.budget_rollover_dialog import BudgetRolloverDialog
from gui.dialogs.budget_dialog import (
    DELETE_RESULT,
    BudgetDialog,
)
from gui.widgets.budget_card import BudgetCard
from gui.widgets.empty_state import EmptyState
from gui.widgets.page_header import PageHeader
from models.budget import Budget
from services.budget_service import BudgetService
from services.budget_rollover_service import BudgetRolloverService
from services.category_service import CategoryService


class BudgetsPage(QWidget):
    """Displays and manages monthly category budgets."""

    def __init__(
        self,
        budget_service: BudgetService,
        category_service: CategoryService,
        account_service=None,
        transaction_service=None,
        savings_goal_service=None,
        savings_goal_allocation_service=None,
        budget_rollover_service: BudgetRolloverService | None = None,
    ) -> None:
        super().__init__()

        self._budget_service = budget_service
        self._category_service = category_service
        self._account_service = account_service
        self._transaction_service = transaction_service
        self._savings_goal_service = savings_goal_service
        self._savings_goal_allocation_service = savings_goal_allocation_service
        self._budget_rollover_service = budget_rollover_service
        self._selected_month = date(date.today().year, date.today().month, 1)
        self._empty_state: EmptyState | None = None

        self.setObjectName("page")

        self._create_interface()
        self.refresh_budgets()

    def _create_interface(self) -> None:
        """Create the Budgets page interface."""

        add_budget_button = QPushButton(
            "+ Add Budget"
        )
        add_budget_button.setObjectName(
            "primaryButton"
        )
        add_budget_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        add_budget_button.clicked.connect(
            self._open_create_budget_dialog
        )

        page_header = PageHeader(
            title="Budgets",
            description=(
                "Set monthly spending limits and monitor "
                "your progress by category."
            ),
            action_widget=add_budget_button,
        )

        self._budgets_container = QWidget()
        self._budgets_container.setObjectName(
            "budgetsContainer"
        )

        self._budgets_layout = QVBoxLayout(
            self._budgets_container
        )
        self._budgets_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        self._budgets_layout.setSpacing(16)
        self._budgets_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop
        )

        content = QWidget()
        content.setObjectName(
            "budgetsContent"
        )

        content_layout = QVBoxLayout(content)
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

        month_bar = QWidget()
        month_layout = QHBoxLayout(month_bar)
        month_layout.setContentsMargins(0, 0, 0, 0)
        previous_button = QPushButton("‹ Previous")
        previous_button.setObjectName("secondaryButton")
        previous_button.clicked.connect(self._show_previous_month)
        next_button = QPushButton("Next ›")
        next_button.setObjectName("secondaryButton")
        next_button.clicked.connect(self._show_next_month)
        today_button = QPushButton("Today")
        today_button.setObjectName("secondaryButton")
        today_button.clicked.connect(self._show_current_month)
        copy_button = QPushButton("Copy Previous Month")
        copy_button.setObjectName("secondaryButton")
        copy_button.clicked.connect(self._copy_previous_month_budgets)
        rollover_button = QPushButton("Roll Over Previous Month")
        rollover_button.setObjectName("secondaryButton")
        rollover_button.clicked.connect(self._open_rollover_dialog)
        self._month_label = QLabel()
        self._month_label.setObjectName("sectionCardTitle")
        self._month_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        month_layout.addWidget(previous_button)
        month_layout.addWidget(today_button)
        month_layout.addStretch()
        month_layout.addWidget(self._month_label)
        month_layout.addStretch()
        month_layout.addWidget(copy_button)
        month_layout.addWidget(rollover_button)
        month_layout.addWidget(next_button)
        content_layout.addWidget(month_bar)
        content_layout.addWidget(
            self._budgets_container
        )
        content_layout.addStretch()

        scroll_area = QScrollArea()
        scroll_area.setObjectName(
            "budgetsScrollArea"
        )
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(
            QFrame.Shape.NoFrame
        )
        scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        scroll_area.setWidget(content)

        page_layout = QVBoxLayout(self)
        page_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        page_layout.setSpacing(0)
        page_layout.addWidget(scroll_area)

    def refresh_budgets(self) -> None:
        """Reload and display selected-month budget progress."""

        self._month_label.setText(self._selected_month.strftime("%B %Y"))
        self._clear_layout()

        try:
            progress_items = (
                self._budget_service
                .get_all_budget_progress(
                    month=self._selected_month
                )
            )
        except (
            ValueError,
            RuntimeError,
        ) as error:
            QMessageBox.critical(
                self,
                "Unable to Load Budgets",
                str(error),
            )
            return

        if not progress_items:
            self._show_empty_state()
            return

        self._empty_state = None

        for progress in progress_items:
            budget_card = BudgetCard(
                category_name=(
                    progress.category_name
                ),
                category_color=(
                    progress.category_color
                ),
                spent_cents=(
                    progress.spent_cents
                ),
                monthly_limit_cents=(
                    progress.budget
                    .monthly_limit_cents
                ),
                remaining_cents=(
                    progress.remaining_cents
                ),
                progress_percent=(
                    progress.progress_percent
                ),
                is_overspent=(
                    progress.is_overspent
                ),
            )

            budget_card.edit_requested.connect(
                lambda selected_budget=(
                    progress.budget
                ): self._open_edit_budget_dialog(
                    selected_budget
                )
            )

            self._budgets_layout.addWidget(
                budget_card
            )

    def _show_empty_state(self) -> None:
        """Display a message when no active budgets exist."""

        self._empty_state = EmptyState(
            title="No budgets yet",
            description=(
                "Create a monthly spending limit for an "
                "expense category to begin tracking it."
            ),
            action_text="+ Add Budget",
        )

        self._empty_state.action_button().clicked.connect(
            self._open_create_budget_dialog
        )

        self._budgets_layout.addWidget(
            self._empty_state
        )

    def _get_expense_categories(self):
        """Return active expense categories."""

        categories = (
            self._category_service.get_categories()
        )

        return [
            category
            for category in categories
            if category.category_type == "Expense"
        ]

    def _open_create_budget_dialog(self) -> None:
        """Open the dialog for creating a monthly budget."""

        try:
            categories = self._get_expense_categories()
            active_budgets = (
                self._budget_service.get_budgets(month=self._selected_month)
            )
        except RuntimeError as error:
            QMessageBox.critical(
                self,
                "Unable to Open Budget",
                str(error),
            )
            return

        budgeted_category_ids = {
            budget.category_id
            for budget in active_budgets
        }

        available_categories = [
            category
            for category in categories
            if (
                category.category_id
                not in budgeted_category_ids
            )
        ]

        if not available_categories:
            QMessageBox.information(
                self,
                "No Categories Available",
                (
                    "Every active expense category already "
                    "has a monthly budget."
                ),
            )
            return

        dialog = BudgetDialog(
            categories=available_categories,
            parent=self,
        )

        while True:
            result = dialog.exec()

            if result != QDialog.DialogCode.Accepted:
                return

            (
                category_id,
                monthly_limit,
            ) = dialog.get_budget_data()

            try:
                self._budget_service.create_budget(
                    category_id=category_id,
                    monthly_limit=monthly_limit,
                    month=self._selected_month,
                )
            except ValueError as error:
                dialog.show_error(
                    str(error)
                )
                continue
            except RuntimeError as error:
                QMessageBox.critical(
                    self,
                    "Unable to Create Budget",
                    str(error),
                )
                return

            self.refresh_budgets()
            return

    def _open_edit_budget_dialog(
        self,
        budget: Budget,
    ) -> None:
        """Open the dialog for editing or deleting a budget."""

        try:
            categories = self._get_expense_categories()
        except RuntimeError as error:
            QMessageBox.critical(
                self,
                "Unable to Open Budget",
                str(error),
            )
            return

        dialog = BudgetDialog(
            categories=categories,
            parent=self,
            budget=budget,
        )

        while True:
            result = dialog.exec()

            if result == DELETE_RESULT:
                self._archive_budget(
                    budget
                )
                return

            if result != QDialog.DialogCode.Accepted:
                return

            (
                category_id,
                monthly_limit,
            ) = dialog.get_budget_data()

            try:
                self._budget_service.update_budget(
                    budget_id=budget.budget_id,
                    category_id=category_id,
                    monthly_limit=monthly_limit,
                )
            except ValueError as error:
                dialog.show_error(
                    str(error)
                )
                continue
            except RuntimeError as error:
                QMessageBox.critical(
                    self,
                    "Unable to Update Budget",
                    str(error),
                )
                return

            self.refresh_budgets()
            return

    def _archive_budget(
        self,
        budget: Budget,
    ) -> None:
        """Archive a confirmed budget."""

        try:
            self._budget_service.archive_budget(
                budget.budget_id
            )
        except (
            ValueError,
            RuntimeError,
        ) as error:
            QMessageBox.critical(
                self,
                "Unable to Delete Budget",
                str(error),
            )
            return

        self.refresh_budgets()

    def _show_previous_month(self) -> None:
        self._selected_month = self._budget_service.previous_month(self._selected_month)
        self.refresh_budgets()

    def _show_next_month(self) -> None:
        self._selected_month = self._budget_service.next_month(self._selected_month)
        self.refresh_budgets()

    def _show_current_month(self) -> None:
        today = date.today()
        self._selected_month = date(today.year, today.month, 1)
        self.refresh_budgets()

    def _copy_previous_month_budgets(self) -> None:
        """Copy regular budget limits from the previous month."""

        source_month = self._budget_service.previous_month(
            self._selected_month
        )

        try:
            source_budgets = self._budget_service.get_budgets(
                month=source_month
            )
        except RuntimeError as error:
            QMessageBox.critical(
                self,
                "Unable to Copy Budgets",
                str(error),
            )
            return

        if not source_budgets:
            QMessageBox.information(
                self,
                "Nothing to Copy",
                (
                    "No budgets exist for "
                    f"{source_month.strftime('%B %Y')}."
                ),
            )
            return

        confirmation = QMessageBox.question(
            self,
            "Copy Previous Month",
            (
                f"Copy the regular budget amounts from "
                f"{source_month.strftime('%B %Y')} to "
                f"{self._selected_month.strftime('%B %Y')}?\n\n"
                "Existing budgets in the destination month "
                "will be kept and skipped. Unused rollover "
                "amounts are not included."
            ),
            (
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No
            ),
            QMessageBox.StandardButton.No,
        )

        if confirmation != QMessageBox.StandardButton.Yes:
            return

        try:
            copied_count, skipped_count = (
                self._budget_service.copy_previous_month_budgets(
                    self._selected_month
                )
            )
        except (ValueError, RuntimeError) as error:
            QMessageBox.critical(
                self,
                "Unable to Copy Budgets",
                str(error),
            )
            return

        QMessageBox.information(
            self,
            "Budgets Copied",
            (
                f"Copied {copied_count} budget(s) from "
                f"{source_month.strftime('%B %Y')} to "
                f"{self._selected_month.strftime('%B %Y')}.\n"
                f"Skipped {skipped_count} budget(s) that "
                "already existed."
            ),
        )
        self.refresh_budgets()

    def _open_rollover_dialog(self) -> None:
        if any(
            service is None
            for service in (
                self._account_service,
                self._savings_goal_service,
                self._budget_rollover_service,
            )
        ):
            QMessageBox.critical(
                self,
                "Rollover Unavailable",
                "The rollover services are not configured.",
            )
            return

        source_month = self._budget_service.previous_month(
            self._selected_month
        )

        try:
            all_items = self._budget_service.get_rollover_items(
                self._selected_month
            )
            items = self._budget_rollover_service.get_available_items(
                self._selected_month
            )
            accounts = self._account_service.get_accounts()
            goals = self._savings_goal_service.get_goals()
        except (ValueError, RuntimeError) as error:
            QMessageBox.critical(
                self,
                "Unable to Prepare Rollover",
                str(error),
            )
            return

        if not all_items:
            QMessageBox.information(
                self,
                "Nothing to Roll Over",
                (
                    "No budgets exist for "
                    f"{source_month.strftime('%B %Y')}."
                ),
            )
            return

        positive_items = [
            item for item in all_items
            if item.unused_cents > 0
        ]

        if not positive_items:
            QMessageBox.information(
                self,
                "Nothing to Roll Over",
                (
                    "There are no positive unused budget amounts "
                    f"from {source_month.strftime('%B %Y')}."
                ),
            )
            return

        if not items:
            QMessageBox.information(
                self,
                "Rollover Already Complete",
                (
                    "Every positive unused budget amount from "
                    f"{source_month.strftime('%B %Y')} has already "
                    f"been processed for "
                    f"{self._selected_month.strftime('%B %Y')}."
                ),
            )
            return

        processed_count = len(positive_items) - len(items)

        if processed_count > 0:
            QMessageBox.information(
                self,
                "Previously Processed Budgets",
                (
                    f"{processed_count} rollover item(s) were already "
                    "processed and will not be shown again."
                ),
            )

        dialog = BudgetRolloverDialog(
            source_month,
            self._selected_month,
            items,
            accounts,
            goals,
            self,
        )

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        source_account_id, savings_account_id = (
            dialog.get_account_ids()
        )

        try:
            for choice in dialog.get_choices():
                self._budget_rollover_service.process_choice(
                    item=choice.item,
                    destination_month=self._selected_month,
                    destination_type=choice.destination,
                    source_account_id=source_account_id,
                    savings_account_id=savings_account_id,
                    goal_id=choice.goal_id,
                )
        except (ValueError, RuntimeError) as error:
            QMessageBox.critical(
                self,
                "Unable to Apply Rollover",
                str(error),
            )
            self.refresh_budgets()
            return

        QMessageBox.information(
            self,
            "Rollover Complete",
            (
                "Budget rollover into "
                f"{self._selected_month.strftime('%B %Y')} "
                "was applied successfully."
            ),
        )
        self.refresh_budgets()

    def _clear_layout(self) -> None:
        """Remove all currently displayed budget widgets."""

        while self._budgets_layout.count():
            layout_item = (
                self._budgets_layout.takeAt(0)
            )

            widget = layout_item.widget()

            if widget is not None:
                widget.deleteLater()