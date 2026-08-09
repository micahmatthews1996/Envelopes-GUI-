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
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from gui.dialogs.account_dialog import AccountDialog
from gui.widgets.card import Card
from gui.widgets.empty_state import EmptyState
from gui.widgets.page_header import PageHeader
from models.account import Account
from services.account_service import AccountService
from services.balance_service import BalanceService
from utils.money import format_currency


class AccountsPage(QWidget):
    """Displays and manages the user's financial accounts."""

    def __init__(
        self,
        account_service: AccountService,
        balance_service: BalanceService,
    ) -> None:
        super().__init__()

        self.account_service = account_service
        self.balance_service = balance_service
        self.account_grid = QGridLayout()

        self.setObjectName("page")

        self._create_interface()
        self.refresh_accounts()

    def _create_interface(self) -> None:
        """Create the Accounts page interface."""

        add_account_button = QPushButton(
            "+ Add Account"
        )
        add_account_button.setObjectName(
            "primaryButton"
        )
        add_account_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        add_account_button.clicked.connect(
            lambda: self._open_account_dialog()
        )

        page_header = PageHeader(
            title="Accounts",
            description=(
                "View current balances and manage "
                "your financial accounts."
            ),
            action_widget=add_account_button,
        )

        self.account_grid.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        self.account_grid.setHorizontalSpacing(18)
        self.account_grid.setVerticalSpacing(18)
        self.account_grid.setAlignment(
            Qt.AlignmentFlag.AlignTop
        )

        grid_container = QWidget()
        grid_container.setLayout(
            self.account_grid
        )

        scroll_area = QScrollArea()
        scroll_area.setObjectName(
            "accountScrollArea"
        )
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(
            QFrame.Shape.NoFrame
        )
        scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        scroll_area.setWidget(
            grid_container
        )

        page_layout = QVBoxLayout(self)
        page_layout.setContentsMargins(
            40,
            32,
            40,
            32,
        )
        page_layout.setSpacing(24)

        page_layout.addWidget(
            page_header
        )
        page_layout.addWidget(
            scroll_area,
            stretch=1,
        )

    def refresh_accounts(self) -> None:
        """Reload and display all accounts and current balances."""

        self._clear_account_grid()

        try:
            accounts = (
                self.account_service.get_accounts()
            )
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

            try:
                current_balance_cents = (
                    self.balance_service
                    .get_current_balance_cents(
                        account
                    )
                )
            except RuntimeError as error:
                QMessageBox.critical(
                    self,
                    "Unable to Calculate Balance",
                    str(error),
                )
                return

            account_card = self._create_account_card(
                account=account,
                current_balance_cents=(
                    current_balance_cents
                ),
            )

            self.account_grid.addWidget(
                account_card,
                row,
                column,
            )

    def _create_account_card(
        self,
        account: Account,
        current_balance_cents: int,
    ) -> Card:
        """Create a reusable UI-kit card for an account."""

        card = Card()
        card.setObjectName("accountCard")
        card.setMinimumHeight(210)

        account_name = QLabel(
            account.name
        )
        account_name.setObjectName(
            "accountCardName"
        )
        account_name.setWordWrap(True)
        account_name.setMinimumWidth(0)
        account_name.setSizePolicy(
            QSizePolicy.Policy.Ignored,
            QSizePolicy.Policy.Preferred,
        )

        current_balance_caption = QLabel(
            "Current balance"
        )
        current_balance_caption.setObjectName(
            "accountCardCaption"
        )
        current_balance_caption.setMinimumWidth(0)
        current_balance_caption.setSizePolicy(
            QSizePolicy.Policy.Ignored,
            QSizePolicy.Policy.Preferred,
        )

        current_balance_label = QLabel(
            format_currency(
                current_balance_cents
            )
        )
        current_balance_label.setObjectName(
            "accountCardBalance"
        )
        current_balance_label.setWordWrap(True)
        current_balance_label.setMinimumWidth(0)
        current_balance_label.setSizePolicy(
            QSizePolicy.Policy.Ignored,
            QSizePolicy.Policy.Preferred,
        )

        opening_balance_caption = QLabel(
            "Opening balance"
        )
        opening_balance_caption.setObjectName(
            "accountCardCaption"
        )
        opening_balance_caption.setMinimumWidth(0)
        opening_balance_caption.setSizePolicy(
            QSizePolicy.Policy.Ignored,
            QSizePolicy.Policy.Preferred,
        )

        opening_balance_label = QLabel(
            format_currency(
                account.opening_balance_cents
            )
        )
        opening_balance_label.setObjectName(
            "accountOpeningBalance"
        )
        opening_balance_label.setWordWrap(True)
        opening_balance_label.setMinimumWidth(0)
        opening_balance_label.setSizePolicy(
            QSizePolicy.Policy.Ignored,
            QSizePolicy.Policy.Preferred,
        )

        edit_button = QPushButton("Edit")
        edit_button.setObjectName(
            "secondaryButton"
        )
        edit_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        edit_button.clicked.connect(
            lambda: self._open_account_dialog(
                account
            )
        )

        delete_button = QPushButton("Delete")
        delete_button.setObjectName(
            "dangerTextButton"
        )
        delete_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        delete_button.clicked.connect(
            self._create_delete_handler(
                account
            )
        )

        action_layout = QHBoxLayout()
        action_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        action_layout.setSpacing(8)
        action_layout.addWidget(
            edit_button
        )
        action_layout.addStretch()
        action_layout.addWidget(
            delete_button
        )

        card_layout = card.content_layout()

        if not isinstance(
            card_layout,
            QVBoxLayout,
        ):
            raise RuntimeError(
                "Account cards require a vertical layout."
            )

        card_layout.addWidget(
            account_name
        )
        card_layout.addSpacing(12)
        card_layout.addWidget(
            current_balance_caption
        )
        card_layout.addWidget(
            current_balance_label
        )
        card_layout.addSpacing(10)
        card_layout.addWidget(
            opening_balance_caption
        )
        card_layout.addWidget(
            opening_balance_label
        )
        card_layout.addStretch()
        card_layout.addLayout(
            action_layout
        )

        return card

    def _create_delete_handler(
        self,
        account: Account,
    ) -> Callable[[], None]:
        """Create a delete callback for an account."""

        return lambda: self._confirm_delete(
            account
        )

    def _show_empty_state(self) -> None:
        """Display the reusable account empty state."""

        empty_state = EmptyState(
            title="No accounts yet",
            description=(
                "Add your first checking, savings, "
                "cash, or credit account to get started."
            ),
            action_text="+ Add Account",
        )

        empty_state.action_button().clicked.connect(
            lambda: self._open_account_dialog()
        )

        self.account_grid.addWidget(
            empty_state,
            0,
            0,
            1,
            2,
        )

    def _open_account_dialog(
        self,
        account: Account | None = None,
    ) -> None:
        """Open the account dialog in create or edit mode."""

        dialog = AccountDialog(
            parent=self,
            account=account,
        )

        while dialog.exec():
            (
                account_name,
                account_type,
                opening_balance,
            ) = dialog.get_account_data()

            try:
                if account is None:
                    self.account_service.create_account(
                        name=account_name,
                        account_type=account_type,
                        opening_balance=opening_balance,
                    )
                else:
                    self.account_service.update_account(
                        account_id=account.account_id,
                        name=account_name,
                        account_type=account_type,
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
            self.account_service.delete_account(
                account.account_id
            )
        except (
            ValueError,
            RuntimeError,
        ) as error:
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
            layout_item = (
                self.account_grid.takeAt(0)
            )
            widget = layout_item.widget()

            if widget is not None:
                widget.deleteLater()