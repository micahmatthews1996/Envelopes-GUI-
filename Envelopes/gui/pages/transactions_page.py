from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QHBoxLayout,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from gui.dialogs.savings_allocation_dialog import (
    SavingsAllocationDialog,
)
from gui.dialogs.transaction_dialog import TransactionDialog
from gui.dialogs.transfer_dialog import TransferDialog
from gui.widgets.empty_state import EmptyState
from gui.widgets.page_header import PageHeader
from gui.widgets.section_card import SectionCard
from models.account import Account
from models.category import Category
from models.transaction import Transaction
from services.account_service import AccountService
from services.category_service import CategoryService
from services.savings_goal_allocation_service import (
    SavingsGoalAllocationService,
)
from services.savings_goal_service import SavingsGoalService
from services.transaction_service import TransactionService
from utils.money import format_currency


class TransactionsPage(QWidget):
    """Displays and manages financial transactions."""

    def __init__(
        self,
        transaction_service: TransactionService,
        account_service: AccountService,
        category_service: CategoryService,
        savings_goal_service: SavingsGoalService,
        savings_goal_allocation_service: (
            SavingsGoalAllocationService
        ),
    ) -> None:
        super().__init__()

        self._transaction_service = transaction_service
        self._account_service = account_service
        self._category_service = category_service
        self._savings_goal_service = savings_goal_service
        self._savings_goal_allocation_service = (
            savings_goal_allocation_service
        )

        self._accounts_by_id: dict[str, Account] = {}
        self._categories_by_id: dict[str, Category] = {}
        self._transactions_by_row: dict[int, Transaction] = {}

        self._empty_state: EmptyState | None = None

        self.setObjectName("page")

        self._create_interface()
        self.refresh_transactions()

    def _create_interface(self) -> None:
        """Create the Transactions page interface."""

        add_transaction_button = QPushButton(
            "+ Add Transaction"
        )
        add_transaction_button.setObjectName(
            "primaryButton"
        )
        add_transaction_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        add_transaction_button.clicked.connect(
            lambda: self._open_transaction_dialog()
        )

        transfer_button = QPushButton(
            "+ Transfer"
        )
        transfer_button.setObjectName(
            "secondaryButton"
        )
        transfer_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        transfer_button.clicked.connect(
            lambda: self._open_transfer_dialog()
        )

        header_actions = QWidget()
        header_actions_layout = QHBoxLayout(
            header_actions
        )
        header_actions_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        header_actions_layout.setSpacing(8)
        header_actions_layout.addWidget(
            transfer_button
        )
        header_actions_layout.addWidget(
            add_transaction_button
        )

        page_header = PageHeader(
            title="Transactions",
            description=(
                "Record and review income, expenses, "
                "and account transfers."
            ),
            action_widget=header_actions,
        )

        self.transaction_table = QTableWidget()
        self.transaction_table.setObjectName(
            "transactionTable"
        )
        self.transaction_table.setColumnCount(6)
        self.transaction_table.setHorizontalHeaderLabels(
            [
                "Date",
                "Payee",
                "Category",
                "Account",
                "Status",
                "Amount",
            ]
        )

        self.transaction_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.transaction_table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self.transaction_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.transaction_table.setAlternatingRowColors(
            True
        )
        self.transaction_table.setShowGrid(False)
        self.transaction_table.setWordWrap(False)
        self.transaction_table.setSortingEnabled(False)

        vertical_header = (
            self.transaction_table.verticalHeader()
        )
        vertical_header.setVisible(False)
        vertical_header.setDefaultSectionSize(56)

        table_header = (
            self.transaction_table.horizontalHeader()
        )
        table_header.setMinimumHeight(46)
        table_header.setHighlightSections(False)
        table_header.setStretchLastSection(False)

        table_header.setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        table_header.setSectionResizeMode(
            1,
            QHeaderView.ResizeMode.Stretch,
        )
        table_header.setSectionResizeMode(
            2,
            QHeaderView.ResizeMode.Stretch,
        )
        table_header.setSectionResizeMode(
            3,
            QHeaderView.ResizeMode.Stretch,
        )
        table_header.setSectionResizeMode(
            4,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        table_header.setSectionResizeMode(
            5,
            QHeaderView.ResizeMode.ResizeToContents,
        )

        self.transaction_table.setColumnWidth(
            0,
            120,
        )
        self.transaction_table.setColumnWidth(
            4,
            100,
        )
        self.transaction_table.setColumnWidth(
            5,
            130,
        )

        self.transaction_table.cellDoubleClicked.connect(
            self._handle_row_double_click
        )

        edit_button = QPushButton("Edit")
        edit_button.setObjectName(
            "secondaryButton"
        )
        edit_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        edit_button.clicked.connect(
            self._edit_selected_transaction
        )

        delete_button = QPushButton("Delete")
        delete_button.setObjectName(
            "dangerTextButton"
        )
        delete_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        delete_button.clicked.connect(
            self._delete_selected_transaction
        )

        action_layout = QHBoxLayout()
        action_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        action_layout.setSpacing(8)
        action_layout.addStretch()
        action_layout.addWidget(edit_button)
        action_layout.addWidget(delete_button)

        self._table_card = SectionCard(
            title="Transaction Register",
            subtitle=(
                "Double-click a transaction to view "
                "or edit its details."
            ),
        )
        self._table_card.add_widget(
            self.transaction_table,
            stretch=1,
        )
        self._table_card.add_layout(
            action_layout
        )

        page_layout = QVBoxLayout(self)
        page_layout.setContentsMargins(
            40,
            32,
            40,
            32,
        )
        page_layout.setSpacing(24)
        page_layout.addWidget(page_header)
        page_layout.addWidget(
            self._table_card,
            stretch=1,
        )

    def refresh_transactions(self) -> None:
        """Reload accounts, categories, and transactions."""

        try:
            accounts = (
                self._account_service.get_accounts()
            )
            categories = (
                self._category_service.get_categories(
                    include_archived=True
                )
            )
            transactions = (
                self._transaction_service.get_transactions()
            )
        except RuntimeError as error:
            QMessageBox.critical(
                self,
                "Unable to Load Transactions",
                str(error),
            )
            return

        self._accounts_by_id = {
            account.account_id: account
            for account in accounts
        }

        self._categories_by_id = {
            category.category_id: category
            for category in categories
        }

        self._transactions_by_row.clear()

        self.transaction_table.clearSelection()
        self.transaction_table.setRowCount(
            len(transactions)
        )

        for row, transaction in enumerate(
            transactions
        ):
            self._transactions_by_row[row] = (
                transaction
            )

            self._populate_transaction_row(
                row=row,
                transaction=transaction,
            )

        if transactions:
            self._hide_empty_state()

            if (
                not self.transaction_table.isVisible()
            ):
                self.transaction_table.setVisible(
                    True
                )

            self.transaction_table.selectRow(
                0
            )
            return

        self.transaction_table.setVisible(False)
        self._show_empty_state()

    def _populate_transaction_row(
        self,
        row: int,
        transaction: Transaction,
    ) -> None:
        """Populate one transaction table row."""

        account = self._accounts_by_id.get(
            transaction.account_id
        )
        category = self._categories_by_id.get(
            transaction.category_id
        )

        account_name = (
            account.name
            if account is not None
            else "Unknown Account"
        )

        if transaction.is_transfer:
            category_name = "Transfer"
        else:
            category_name = (
                category.name
                if category is not None
                else "Unknown Category"
            )

        date_item = QTableWidgetItem(
            transaction.transaction_date.strftime(
                "%m/%d/%Y"
            )
        )

        payee_item = QTableWidgetItem(
            transaction.payee
        )

        category_item = QTableWidgetItem(
            category_name
        )

        if transaction.is_transfer:
            category_item.setForeground(
                QColor("#2F80ED")
            )
        elif category is not None:
            category_item.setForeground(
                QColor(category.color)
            )

        account_item = QTableWidgetItem(
            account_name
        )

        status_item = QTableWidgetItem(
            (
                "Cleared"
                if transaction.is_cleared
                else "Pending"
            )
        )

        amount_item = QTableWidgetItem(
            format_currency(
                transaction.amount_cents
            )
        )

        if transaction.amount_cents < 0:
            amount_item.setForeground(
                QColor("#D64545")
            )
        else:
            amount_item.setForeground(
                QColor("#219653")
            )

        items = [
            date_item,
            payee_item,
            category_item,
            account_item,
            status_item,
            amount_item,
        ]

        for column, item in enumerate(items):
            if column == 5:
                alignment = (
                    Qt.AlignmentFlag.AlignRight
                    | Qt.AlignmentFlag.AlignVCenter
                )
            elif column == 4:
                alignment = (
                    Qt.AlignmentFlag.AlignCenter
                )
            else:
                alignment = (
                    Qt.AlignmentFlag.AlignLeft
                    | Qt.AlignmentFlag.AlignVCenter
                )

            item.setTextAlignment(alignment)

            if transaction.notes:
                item.setToolTip(
                    transaction.notes
                )

            self.transaction_table.setItem(
                row,
                column,
                item,
            )

    def _show_empty_state(self) -> None:
        """Display an empty state inside the transaction card."""

        if self._empty_state is not None:
            self._empty_state.show()
            return

        self._empty_state = EmptyState(
            title="No transactions yet",
            description=(
                "Add your first income or expense "
                "transaction to begin tracking activity."
            ),
            action_text="+ Add Transaction",
        )

        self._empty_state.action_button().clicked.connect(
            lambda: self._open_transaction_dialog()
        )

        self._table_card.add_widget(
            self._empty_state,
            stretch=1,
        )

    def _hide_empty_state(self) -> None:
        """Hide the transaction empty state."""

        if self._empty_state is None:
            return

        self._empty_state.hide()

    def _open_transaction_dialog(
        self,
        transaction: Transaction | None = None,
    ) -> None:
        """Open the transaction dialog in create or edit mode."""

        try:
            accounts = (
                self._account_service.get_accounts()
            )
            categories = (
                self._category_service.get_categories()
            )
        except RuntimeError as error:
            QMessageBox.critical(
                self,
                "Unable to Open Transaction",
                str(error),
            )
            return

        if not accounts:
            QMessageBox.information(
                self,
                "Account Required",
                (
                    "Create at least one account before "
                    "adding a transaction."
                ),
            )
            return

        if not categories:
            QMessageBox.information(
                self,
                "Category Required",
                (
                    "Create at least one active category "
                    "before adding a transaction."
                ),
            )
            return

        dialog = TransactionDialog(
            accounts=accounts,
            categories=categories,
            parent=self,
            transaction=transaction,
        )

        while dialog.exec():
            (
                account_id,
                category_id,
                payee,
                amount,
                transaction_date,
                notes,
                is_cleared,
            ) = dialog.get_transaction_data()

            try:
                if transaction is None:
                    self._transaction_service.create_transaction(
                        account_id=account_id,
                        category_id=category_id,
                        payee=payee,
                        amount=amount,
                        transaction_date=transaction_date,
                        notes=notes,
                        is_cleared=is_cleared,
                    )
                else:
                    self._transaction_service.update_transaction(
                        transaction_id=(
                            transaction.transaction_id
                        ),
                        account_id=account_id,
                        category_id=category_id,
                        payee=payee,
                        amount=amount,
                        transaction_date=transaction_date,
                        notes=notes,
                        is_cleared=is_cleared,
                    )
            except ValueError as error:
                dialog.show_error(str(error))
                continue
            except RuntimeError as error:
                QMessageBox.critical(
                    self,
                    "Unable to Save Transaction",
                    str(error),
                )
                return

            self.refresh_transactions()
            break

    def _open_transfer_dialog(
        self,
        transaction: Transaction | None = None,
    ) -> None:
        """Open the transfer dialog in create or edit mode."""

        try:
            accounts = self._account_service.get_accounts()
        except RuntimeError as error:
            QMessageBox.critical(
                self,
                "Unable to Open Transfer",
                str(error),
            )
            return

        if len(accounts) < 2:
            QMessageBox.information(
                self,
                "Two Accounts Required",
                (
                    "Create at least two accounts before "
                    "transferring money."
                ),
            )
            return

        accounts_by_id = {
            account.account_id: account
            for account in accounts
        }

        dialog = TransferDialog(
            accounts=accounts,
            parent=self,
            transfer_transaction=transaction,
        )

        while dialog.exec():
            (
                source_account_id,
                destination_account_id,
                amount,
                transfer_date,
                notes,
                is_cleared,
            ) = dialog.get_transfer_data()

            try:
                if transaction is None:
                    (
                        source_transaction,
                        destination_transaction,
                    ) = self._transaction_service.create_transfer(
                        source_account_id=source_account_id,
                        destination_account_id=(
                            destination_account_id
                        ),
                        amount=amount,
                        transaction_date=transfer_date,
                        notes=notes,
                        is_cleared=is_cleared,
                    )
                    transfer_id = (
                        source_transaction.transfer_id
                    )
                else:
                    (
                        source_transaction,
                        destination_transaction,
                    ) = self._transaction_service.update_transfer(
                        transfer_id=transaction.transfer_id,
                        source_account_id=source_account_id,
                        destination_account_id=(
                            destination_account_id
                        ),
                        amount=amount,
                        transaction_date=transfer_date,
                        notes=notes,
                        is_cleared=is_cleared,
                    )
                    transfer_id = transaction.transfer_id

                    self._savings_goal_allocation_service\
                        .delete_allocations_for_source(
                            source_type="transfer",
                            source_id=transfer_id,
                        )
                    self._savings_goal_allocation_service\
                        .sync_all_goal_current_amounts()

            except ValueError as error:
                dialog.show_error(str(error))
                continue
            except RuntimeError as error:
                QMessageBox.critical(
                    self,
                    "Unable to Save Transfer",
                    str(error),
                )
                return

            destination_account = accounts_by_id.get(
                destination_account_id
            )

            if (
                destination_account is not None
                and destination_account.account_type
                == "Savings"
            ):
                self._offer_transfer_allocation(
                    transfer_id=transfer_id,
                    transferred_amount_cents=abs(
                        source_transaction.amount_cents
                    ),
                    notes=notes,
                )

            self.refresh_transactions()
            return

    def _offer_transfer_allocation(
        self,
        transfer_id: str,
        transferred_amount_cents: int,
        notes: str,
    ) -> None:
        """Offer to allocate a transfer deposited into Savings."""

        try:
            available_amount_cents = min(
                transferred_amount_cents,
                self._savings_goal_allocation_service
                .get_unallocated_savings_cents(),
            )
            goals = self._savings_goal_service.get_goals()
        except RuntimeError as error:
            QMessageBox.critical(
                self,
                "Unable to Prepare Allocation",
                str(error),
            )
            return

        if (
            available_amount_cents <= 0
            or not any(
                not goal.is_completed
                for goal in goals
            )
        ):
            return

        response = QMessageBox.question(
            self,
            "Allocate Transfer",
            (
                "The transfer into Savings is complete.\n\n"
                "Would you like to allocate some or all "
                "of this transfer to a savings goal?"
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
            savings_goal_service=self._savings_goal_service,
            available_amount_cents=available_amount_cents,
            parent=self,
            initial_amount_cents=available_amount_cents,
            initial_notes=notes,
        )

        while allocation_dialog.exec():
            (
                goal_id,
                amount_cents,
                allocation_notes,
            ) = allocation_dialog.get_allocation_data()

            try:
                self._savings_goal_allocation_service\
                    .create_allocation(
                        goal_id=goal_id,
                        amount_cents=amount_cents,
                        source_type="transfer",
                        source_id=transfer_id,
                        notes=allocation_notes,
                    )
                self._savings_goal_allocation_service\
                    .sync_goal_current_amount(goal_id)
            except ValueError as error:
                allocation_dialog.show_error(str(error))
                continue
            except RuntimeError as error:
                QMessageBox.critical(
                    self,
                    "Unable to Allocate Savings",
                    str(error),
                )
                return

            return

    def _selected_transaction(
        self,
    ) -> Transaction | None:
        """Return the currently selected transaction."""

        selected_row = (
            self.transaction_table.currentRow()
        )

        if selected_row < 0:
            return None

        return self._transactions_by_row.get(
            selected_row
        )

    def _edit_selected_transaction(self) -> None:
        """Open the selected transaction or transfer for editing."""

        transaction = self._selected_transaction()

        if transaction is None:
            QMessageBox.information(
                self,
                "Select a Transaction",
                "Select a transaction to edit.",
            )
            return

        if transaction.is_transfer:
            self._open_transfer_dialog(
                transaction
            )
            return

        self._open_transaction_dialog(
            transaction
        )

    def _delete_selected_transaction(self) -> None:
        """Delete the selected transaction after confirmation."""

        transaction = self._selected_transaction()

        if transaction is None:
            QMessageBox.information(
                self,
                "Select a Transaction",
                "Select a transaction to delete.",
            )
            return

        if transaction.is_transfer:
            dialog_title = "Delete Transfer"
            confirmation_message = (
                "Delete this transfer?\n\n"
                "Both linked transfer entries will be removed. "
                "This action cannot be undone."
            )
        else:
            dialog_title = "Delete Transaction"
            confirmation_message = (
                f'Delete the transaction for '
                f'"{transaction.payee}"?\n\n'
                "This action cannot be undone."
            )

        response = QMessageBox.question(
            self,
            dialog_title,
            confirmation_message,
            (
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No
            ),
            QMessageBox.StandardButton.No,
        )

        if (
            response
            != QMessageBox.StandardButton.Yes
        ):
            return

        try:
            if transaction.is_transfer:
                self._savings_goal_allocation_service\
                    .delete_allocations_for_source(
                        source_type="transfer",
                        source_id=transaction.transfer_id,
                    )
                self._savings_goal_allocation_service\
                    .sync_all_goal_current_amounts()

            self._transaction_service.delete_transaction(
                transaction.transaction_id
            )
        except (
            ValueError,
            RuntimeError,
        ) as error:
            QMessageBox.critical(
                self,
                "Unable to Delete Transaction",
                str(error),
            )
            return

        self.refresh_transactions()

    def _handle_row_double_click(
        self,
        row: int,
        column: int,
    ) -> None:
        """Open a double-clicked transaction or transfer."""

        del column

        transaction = self._transactions_by_row.get(
            row
        )

        if transaction is None:
            return

        if transaction.is_transfer:
            self._open_transfer_dialog(
                transaction
            )
            return

        self._open_transaction_dialog(
            transaction
        )