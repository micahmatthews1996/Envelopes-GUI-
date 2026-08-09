from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from models.account import Account
from models.savings_goal import SavingsGoal
from utils.money import cents_to_dollars, format_currency


class GoalFundingDialog(QDialog):
    """Collect account-to-goal funding details."""

    def __init__(
        self,
        goal: SavingsGoal,
        accounts: list[Account],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._goal = goal
        self._accounts = accounts
        self._accounts_by_id = {
            account.account_id: account
            for account in accounts
        }

        self.setWindowTitle("Fund Savings Goal")
        self.setModal(True)
        self.setMinimumWidth(520)

        self._create_interface()
        self._load_accounts()
        self._source_changed()

    def _create_interface(self) -> None:
        goal_label = QLabel(
            (
                f"{self._goal.name}\n"
                f"{format_currency(self._goal.current_amount_cents)} saved of "
                f"{format_currency(self._goal.target_amount_cents)}"
            ),
            self,
        )
        goal_label.setWordWrap(True)

        self._source_input = QComboBox(self)
        self._source_input.currentIndexChanged.connect(
            self._source_changed
        )

        self._savings_input = QComboBox(self)
        self._savings_input.currentIndexChanged.connect(
            self._source_changed
        )

        remaining_cents = max(
            0,
            self._goal.target_amount_cents
            - self._goal.current_amount_cents,
        )
        self._amount_input = QDoubleSpinBox(self)
        self._amount_input.setDecimals(2)
        self._amount_input.setPrefix("$")
        self._amount_input.setSingleStep(10.00)
        self._amount_input.setRange(
            0.01,
            max(
                0.01,
                float(cents_to_dollars(remaining_cents)),
            ),
        )

        self._status_label = QLabel(self)
        self._status_label.setObjectName("listCardSecondaryText")
        self._status_label.setWordWrap(True)

        self._notes_input = QPlainTextEdit(self)
        self._notes_input.setPlaceholderText(
            "Optional note about this contribution"
        )
        self._notes_input.setMaximumHeight(100)

        form = QFormLayout()
        form.setLabelAlignment(
            Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignTop
        )
        form.addRow("Goal:", goal_label)
        form.addRow("From account:", self._source_input)
        form.addRow("Savings account:", self._savings_input)
        form.addRow("", self._status_label)
        form.addRow("Amount:", self._amount_input)
        form.addRow("Notes:", self._notes_input)

        self._error_label = QLabel(self)
        self._error_label.setObjectName("dialogError")
        self._error_label.setWordWrap(True)
        self._error_label.hide()

        self._button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )
        save_button = self._button_box.button(
            QDialogButtonBox.StandardButton.Save
        )
        if isinstance(save_button, QPushButton):
            save_button.setText("Fund Goal")
            save_button.setObjectName("primaryButton")

        self._button_box.accepted.connect(
            self._validate_and_accept
        )
        self._button_box.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)
        layout.addLayout(form)
        layout.addWidget(self._error_label)
        layout.addWidget(self._button_box)

    def _load_accounts(self) -> None:
        for account in sorted(
            self._accounts,
            key=lambda item: item.name.casefold(),
        ):
            self._source_input.addItem(
                f"{account.name} ({account.account_type})",
                account.account_id,
            )

        savings_accounts = [
            account
            for account in self._accounts
            if account.account_type == "Savings"
        ]
        for account in sorted(
            savings_accounts,
            key=lambda item: item.name.casefold(),
        ):
            self._savings_input.addItem(
                account.name,
                account.account_id,
            )

    def _source_changed(self) -> None:
        source_id = self._source_input.currentData()
        savings_id = self._savings_input.currentData()

        if source_id is None or savings_id is None:
            self._status_label.clear()
            return

        if str(source_id) == str(savings_id):
            self._status_label.setText(
                "This money is already in the selected Savings account, "
                "so Envelopes will allocate it directly to the goal."
            )
        else:
            self._status_label.setText(
                "Envelopes will transfer the money into the selected "
                "Savings account and allocate that transfer to the goal."
            )

    def _validate_and_accept(self) -> None:
        if self._source_input.currentData() is None:
            self.show_error("Select a source account.")
            return
        if self._savings_input.currentData() is None:
            self.show_error(
                "Create or select a Savings account to hold goal money."
            )
            return

        amount_cents = round(self._amount_input.value() * 100)
        remaining_cents = max(
            0,
            self._goal.target_amount_cents
            - self._goal.current_amount_cents,
        )

        if amount_cents <= 0:
            self.show_error("Funding amount must be greater than zero.")
            return
        if amount_cents > remaining_cents:
            self.show_error(
                "Funding amount cannot exceed the amount "
                "remaining for this goal."
            )
            return

        self._error_label.hide()
        self.accept()

    def get_funding_data(self) -> tuple[str, str, int, str]:
        return (
            str(self._source_input.currentData()),
            str(self._savings_input.currentData()),
            round(self._amount_input.value() * 100),
            self._notes_input.toPlainText().strip(),
        )

    def show_error(self, message: str) -> None:
        self._error_label.setText(message)
        self._error_label.show()
