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


class GoalTransferDialog(QDialog):
    """Move goal money to another goal or any account."""

    def __init__(
        self,
        goals: list[SavingsGoal],
        accounts: list[Account],
        source_goal: SavingsGoal,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._source_goal = source_goal
        self._goals_by_id = {goal.goal_id: goal for goal in goals}
        self._accounts_by_id = {
            account.account_id: account
            for account in accounts
        }
        self._savings_accounts = [
            account
            for account in accounts
            if account.account_type == "Savings"
        ]

        self.setWindowTitle("Move Savings Goal Money")
        self.setModal(True)
        self.setMinimumWidth(540)

        self._create_interface()
        self._load_destination_types()
        self._destination_type_changed()

    def _create_interface(self) -> None:
        source_name = QLabel(self._source_goal.name, self)
        source_name.setObjectName("listCardPrimaryText")
        source_balance = QLabel(
            f"{format_currency(self._source_goal.current_amount_cents)} available",
            self,
        )
        source_balance.setObjectName("listCardSecondaryText")

        source_container = QWidget(self)
        source_layout = QVBoxLayout(source_container)
        source_layout.setContentsMargins(0, 0, 0, 0)
        source_layout.setSpacing(4)
        source_layout.addWidget(source_name)
        source_layout.addWidget(source_balance)

        self._destination_type_input = QComboBox(self)
        self._destination_type_input.currentIndexChanged.connect(
            self._destination_type_changed
        )

        self._source_savings_input = QComboBox(self)
        for account in sorted(
            self._savings_accounts,
            key=lambda item: item.name.casefold(),
        ):
            self._source_savings_input.addItem(
                account.name,
                account.account_id,
            )
        self._source_savings_input.hide()

        self._destination_input = QComboBox(self)
        self._destination_input.currentIndexChanged.connect(
            self._destination_changed
        )

        self._destination_status_label = QLabel(self)
        self._destination_status_label.setObjectName("listCardSecondaryText")
        self._destination_status_label.setWordWrap(True)

        destination_container = QWidget(self)
        destination_layout = QVBoxLayout(destination_container)
        destination_layout.setContentsMargins(0, 0, 0, 0)
        destination_layout.setSpacing(6)
        destination_layout.addWidget(self._destination_input)
        destination_layout.addWidget(self._destination_status_label)

        self._amount_input = QDoubleSpinBox(self)
        self._amount_input.setDecimals(2)
        self._amount_input.setPrefix("$")
        self._amount_input.setSingleStep(10.00)
        self._amount_input.setRange(
            0.01,
            max(
                0.01,
                float(cents_to_dollars(self._source_goal.current_amount_cents)),
            ),
        )

        self._notes_input = QPlainTextEdit(self)
        self._notes_input.setPlaceholderText("Optional note about this move")
        self._notes_input.setMaximumHeight(100)

        self._form = QFormLayout()
        self._form.setContentsMargins(0, 0, 0, 0)
        self._form.setHorizontalSpacing(18)
        self._form.setVerticalSpacing(14)
        self._form.setLabelAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop
        )
        self._form.addRow("From goal:", source_container)
        self._form.addRow("Move to:", self._destination_type_input)
        self._source_savings_label = QLabel("Money held in:")
        self._form.addRow(self._source_savings_label, self._source_savings_input)
        self._form.addRow("Destination:", destination_container)
        self._form.addRow("Amount:", self._amount_input)
        self._form.addRow("Notes:", self._notes_input)

        self._error_label = QLabel(self)
        self._error_label.setObjectName("dialogError")
        self._error_label.setWordWrap(True)
        self._error_label.hide()

        self._button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )
        move_button = self._button_box.button(
            QDialogButtonBox.StandardButton.Save
        )
        if isinstance(move_button, QPushButton):
            move_button.setText("Move Money")
            move_button.setObjectName("primaryButton")

        self._button_box.accepted.connect(self._validate_and_accept)
        self._button_box.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)
        layout.addLayout(self._form)
        layout.addWidget(self._error_label)
        layout.addWidget(self._button_box)

    def _load_destination_types(self) -> None:
        if self._destination_goals():
            self._destination_type_input.addItem(
                "Another Savings Goal",
                "goal",
            )
        if self._accounts_by_id:
            self._destination_type_input.addItem(
                "Account",
                "account",
            )

    def _destination_goals(self) -> list[SavingsGoal]:
        return sorted(
            [
                goal
                for goal in self._goals_by_id.values()
                if (
                    goal.goal_id != self._source_goal.goal_id
                    and not goal.is_archived
                    and not goal.is_completed
                )
            ],
            key=lambda goal: goal.name.casefold(),
        )

    def _destination_type_changed(self) -> None:
        self._destination_input.clear()
        destination_type = self.destination_type()
        account_mode = destination_type == "account"

        self._source_savings_input.setVisible(account_mode)
        self._source_savings_label.setVisible(account_mode)

        if destination_type == "goal":
            for goal in self._destination_goals():
                self._destination_input.addItem(goal.name, goal.goal_id)
        elif destination_type == "account":
            for account in sorted(
                self._accounts_by_id.values(),
                key=lambda item: item.name.casefold(),
            ):
                self._destination_input.addItem(
                    f"{account.name} ({account.account_type})",
                    account.account_id,
                )

        has_destination = self._destination_input.count() > 0
        self._destination_input.setEnabled(has_destination)
        self._amount_input.setEnabled(has_destination)

        move_button = self._button_box.button(
            QDialogButtonBox.StandardButton.Save
        )
        if move_button is not None:
            move_button.setEnabled(has_destination)

        self._destination_changed()

    def _destination_changed(self) -> None:
        destination_type = self.destination_type()

        if destination_type == "goal":
            goal = self._selected_destination_goal()
            if goal is None:
                self._destination_status_label.clear()
                return
            remaining = max(
                0,
                goal.target_amount_cents - goal.current_amount_cents,
            )
            maximum = min(
                self._source_goal.current_amount_cents,
                remaining,
            )
            self._destination_status_label.setText(
                f"{format_currency(goal.current_amount_cents)} saved of "
                f"{format_currency(goal.target_amount_cents)} — "
                f"{format_currency(remaining)} remaining"
            )

        elif destination_type == "account":
            account = self._selected_destination_account()
            maximum = self._source_goal.current_amount_cents

            if account is None:
                self._destination_status_label.clear()
                return

            if account.account_type == "Savings":
                self._destination_status_label.setText(
                    f"Money will be released from the goal into {account.name}."
                )
            else:
                self._destination_status_label.setText(
                    "Envelopes will release the goal allocation and transfer "
                    f"the money from the selected Savings account to {account.name}."
                )
        else:
            maximum = 0
            self._destination_status_label.clear()

        maximum_dollars = max(
            0.01,
            float(cents_to_dollars(maximum)),
        )
        self._amount_input.setMaximum(maximum_dollars)
        if maximum > 0:
            self._amount_input.setValue(maximum_dollars)

    def destination_type(self) -> str:
        data = self._destination_type_input.currentData()
        return "" if data is None else str(data)

    def _selected_destination_goal(self) -> SavingsGoal | None:
        if self.destination_type() != "goal":
            return None
        goal_id = self._destination_input.currentData()
        return None if goal_id is None else self._goals_by_id.get(str(goal_id))

    def _selected_destination_account(self) -> Account | None:
        if self.destination_type() != "account":
            return None
        account_id = self._destination_input.currentData()
        return (
            None
            if account_id is None
            else self._accounts_by_id.get(str(account_id))
        )

    def _validate_and_accept(self) -> None:
        destination_type = self.destination_type()
        if destination_type not in {"goal", "account"}:
            self.show_error("Select where the money should go.")
            return

        if self._destination_input.currentData() is None:
            self.show_error("Select a destination.")
            return

        amount_cents = round(self._amount_input.value() * 100)

        if amount_cents <= 0:
            self.show_error("Transfer amount must be greater than zero.")
            return

        if amount_cents > self._source_goal.current_amount_cents:
            self.show_error(
                "Transfer amount cannot exceed the money "
                "available in the source goal."
            )
            return

        if destination_type == "goal":
            goal = self._selected_destination_goal()
            if goal is None:
                self.show_error("Select a destination savings goal.")
                return
            remaining = max(
                0,
                goal.target_amount_cents - goal.current_amount_cents,
            )
            if amount_cents > remaining:
                self.show_error(
                    "Transfer amount cannot exceed the amount "
                    "remaining for the destination goal."
                )
                return

        if destination_type == "account":
            if self._source_savings_input.currentData() is None:
                self.show_error(
                    "Select the Savings account that currently holds this money."
                )
                return

        self._error_label.hide()
        self.accept()

    def get_transfer_data(
        self,
    ) -> tuple[str, str, str, str, int, str]:
        return (
            self._source_goal.goal_id,
            self.destination_type(),
            str(self._source_savings_input.currentData() or ""),
            str(self._destination_input.currentData()),
            round(self._amount_input.value() * 100),
            self._notes_input.toPlainText().strip(),
        )

    def show_error(self, message: str) -> None:
        self._error_label.setText(message)
        self._error_label.show()
