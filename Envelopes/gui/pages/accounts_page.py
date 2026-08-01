from collections.abc import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from gui.dialogs.account_dialog import AccountDialog
from models.account import Account
from services.account_service import AccountService
from utils.money import format_currency


class AccountsPage(QWidget):
    """Displays and manages the user's financial accounts."""

    def __init__(
        self,
        account_service: AccountService,
    ) -> None:
        super().__init__()

        self.account_service = account_service
        self.account_grid = QGridLayout()

        self.setObjectName("page")

        self._create_interface()
        self.refresh_accounts()

    def _create_interface(self) -> None:
        """Create the accounts page interface."""

        page_title = QLabel("Accounts")
        page_title.setObjectName("pageTitle")

        page_description = QLabel(
            "Create and manage the accounts used by Envelopes."
        )
        page_description.setObjectName("pageDescription")

        add_account_button = QPushButton("+ Add Account")
        add_account_button.setObjectName("primaryButton")
        add_account_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        add_account_button.clicked.connect(
            self._open_add_account_dialog
        )

        heading_text_layout = QVBoxLayout()
        heading_text_layout.setSpacing(4)
        heading_text_layout.addWidget(page_title)
        heading_text_layout.addWidget(page_description)

        heading_layout = QHBoxLayout()
        heading_layout.addLayout(heading_text_layout)
        heading_layout.addStretch()
        heading_layout.addWidget(add_account_button)

        self.account_grid.setContentsMargins(0, 0, 0, 0)
        self.account_grid.setHorizontalSpacing(18)
        self.account_grid.setVerticalSpacing(18)
        self.account_grid.setAlignment(
            Qt.AlignmentFlag.AlignTop
        )

        grid_container = QWidget()
        grid_container.setLayout(self.account_grid)

        scroll_area = QScrollArea()
        scroll_area.setObjectName("accountScrollArea")
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setWidget(grid_container)

        page_layout = QVBoxLayout(self)
        page_layout.setContentsMargins(40, 32, 40, 32)
        page_layout.setSpacing(24)

        page_layout.addLayout(heading_layout)
        page_layout.addWidget(scroll_area, stretch=1)

    def refresh_accounts(self) -> None:
        """Reload and display all accounts."""

        self._clear_account_grid()

        try:
            accounts = self.account_service.get_accounts()
        except RuntimeError as error:
            QMessageBox.critical(
                self,
                "Unable to Load Accounts",
                str(error),
            )
            return

        if not accounts:
            self._show_empty_state()
            return

        columns = 2

        for index, account in enumerate(accounts):
            row = index // columns
            column = index % columns

            account_card = self._create_account_card(
                account
            )

            self.account_grid.addWidget(
                account_card,
                row,
                column,
            )

    def _create_account_card(
        self,
        account: Account,
    ) -> QFrame:
        """Create a visual card for an account."""

        card = QFrame()
        card.setObjectName("accountCard")
        card.setMinimumHeight(160)

        account_name = QLabel(account.name)
        account_name.setObjectName("accountCardName")

        balance_caption = QLabel("Opening balance")
        balance_caption.setObjectName(
            "accountCardCaption"
        )

        balance_label = QLabel(
            format_currency(
                account.opening_balance_cents
            )
        )
        balance_label.setObjectName(
            "accountCardBalance"
        )

        delete_button = QPushButton("Delete")
        delete_button.setObjectName(
            "dangerTextButton"
        )
        delete_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        delete_button.clicked.connect(
            self._create_delete_handler(account)
        )

        action_layout = QHBoxLayout()
        action_layout.addStretch()
        action_layout.addWidget(delete_button)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(
            22,
            20,
            22,
            20,
        )
        card_layout.setSpacing(6)

        card_layout.addWidget(account_name)
        card_layout.addStretch()
        card_layout.addWidget(balance_caption)
        card_layout.addWidget(balance_label)
        card_layout.addLayout(action_layout)

        return card

    def _create_delete_handler(
        self,
        account: Account,
    ) -> Callable[[], None]:
        """Create a delete callback for an account."""

        return lambda: self._confirm_delete(account)

    def _show_empty_state(self) -> None:
        """Display a message when no accounts exist."""

        empty_state = QFrame()
        empty_state.setObjectName("emptyState")

        title_label = QLabel("No accounts yet")
        title_label.setObjectName("emptyStateTitle")
        title_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        description_label = QLabel(
            "Add your first checking, savings, cash, "
            "or credit account to get started."
        )
        description_label.setObjectName(
            "emptyStateDescription"
        )
        description_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        description_label.setWordWrap(True)

        empty_layout = QVBoxLayout(empty_state)
        empty_layout.setContentsMargins(
            40,
            50,
            40,
            50,
        )
        empty_layout.setSpacing(10)

        empty_layout.addWidget(title_label)
        empty_layout.addWidget(description_label)

        self.account_grid.addWidget(
            empty_state,
            0,
            0,
            1,
            2,
        )

    def _open_add_account_dialog(self) -> None:
        """Open the dialog used to create an account."""

        dialog = AccountDialog(self)

        while dialog.exec():
            account_name, opening_balance = (
                dialog.get_account_data()
            )

            try:
                self.account_service.create_account(
                    name=account_name,
                    opening_balance=opening_balance,
                )
            except ValueError as error:
                dialog.show_error(str(error))
                continue
            except RuntimeError as error:
                QMessageBox.critical(
                    self,
                    "Unable to Save Account",
                    str(error),
                )
                return

            self.refresh_accounts()
            break

    def _confirm_delete(
        self,
        account: Account,
    ) -> None:
        """Ask the user to confirm account deletion."""

        response = QMessageBox.question(
            self,
            "Delete Account",
            (
                f'Are you sure you want to delete '
                f'"{account.name}"?'
            ),
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if response != QMessageBox.StandardButton.Yes:
            return

        try:
            self.account_service.delete_account(
                account.account_id
            )
        except (ValueError, RuntimeError) as error:
            QMessageBox.critical(
                self,
                "Unable to Delete Account",
                str(error),
            )
            return

        self.refresh_accounts()

    def _clear_account_grid(self) -> None:
        """Remove all widgets currently displayed in the grid."""

        while self.account_grid.count():
            layout_item = self.account_grid.takeAt(0)
            widget = layout_item.widget()

            if widget is not None:
                widget.deleteLater()