from datetime import date

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
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
from models.transaction import Transaction
from utils.money import cents_to_dollars


class TransferDialog(QDialog):
    """Collect information for creating or editing a transfer."""

    def __init__(
        self,
        accounts: list[Account],
        parent: QWidget | None = None,
        transfer_transaction: Transaction | None = None,
    ) -> None:
        super().__init__(parent)

        self._accounts = accounts
        self._transfer_transaction = transfer_transaction
        self._updating_account_inputs = False

        self.setModal(True)
        self.setMinimumWidth(500)

        self.source_account_input = QComboBox()
        self.destination_account_input = QComboBox()

        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(
            0.01,
            999_999_999.99,
        )
        self.amount_input.setDecimals(2)
        self.amount_input.setPrefix("$")
        self.amount_input.setSingleStep(1.00)

        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDisplayFormat(
            "MM/dd/yyyy"
        )
        self.date_input.setDate(
            QDate.currentDate()
        )

        self.notes_input = QPlainTextEdit()
        self.notes_input.setPlaceholderText(
            "Optional memo for this transfer"
        )
        self.notes_input.setMaximumHeight(120)

        self.cleared_input = QCheckBox(
            "This transfer has cleared"
        )

        self.error_label = QLabel()
        self.error_label.setObjectName(
            "dialogError"
        )
        self.error_label.setWordWrap(True)
        self.error_label.hide()

        self.button_box = QDialogButtonBox(
            (
                QDialogButtonBox.StandardButton.Save
                | QDialogButtonBox.StandardButton.Cancel
            )
        )

        self.button_box.accepted.connect(
            self._validate
        )
        self.button_box.rejected.connect(
            self.reject
        )

        form_layout = QFormLayout()
        form_layout.setSpacing(12)

        form_layout.addRow(
            "From account:",
            self.source_account_input,
        )
        form_layout.addRow(
            "To account:",
            self.destination_account_input,
        )
        form_layout.addRow(
            "Amount:",
            self.amount_input,
        )
        form_layout.addRow(
            "Date:",
            self.date_input,
        )
        form_layout.addRow(
            "Memo:",
            self.notes_input,
        )
        form_layout.addRow(
            "",
            self.cleared_input,
        )

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(
            24,
            24,
            24,
            24,
        )
        main_layout.setSpacing(18)

        main_layout.addLayout(
            form_layout
        )
        main_layout.addWidget(
            self.error_label
        )
        main_layout.addWidget(
            self.button_box
        )

        self.source_account_input.currentIndexChanged.connect(
            self._source_account_changed
        )
        self.destination_account_input.currentIndexChanged.connect(
            self._destination_account_changed
        )

        self._populate_account_inputs()
        self._configure_mode()

    def get_transfer_data(
        self,
    ) -> tuple[
        str,
        str,
        float,
        date,
        str,
        bool,
    ]:
        """Return the values entered by the user."""

        selected_date = self.date_input.date()

        transfer_date = date(
            selected_date.year(),
            selected_date.month(),
            selected_date.day(),
        )

        return (
            str(
                self.source_account_input.currentData()
            ),
            str(
                self.destination_account_input.currentData()
            ),
            self.amount_input.value(),
            transfer_date,
            self.notes_input.toPlainText().strip(),
            self.cleared_input.isChecked(),
        )

    def show_error(
        self,
        message: str,
    ) -> None:
        """Display a validation error inside the dialog."""

        self.error_label.setText(
            message
        )
        self.error_label.show()

    def _populate_account_inputs(self) -> None:
        """Populate both account selectors."""

        self._updating_account_inputs = True

        self.source_account_input.clear()
        self.destination_account_input.clear()

        for account in self._accounts:
            self.source_account_input.addItem(
                account.name,
                account.account_id,
            )

        source_account_id = str(
            self.source_account_input.currentData()
        )

        for account in self._accounts:
            if account.account_id == source_account_id:
                continue

            self.destination_account_input.addItem(
                account.name,
                account.account_id,
            )

        self._updating_account_inputs = False

    def _source_account_changed(self) -> None:
        """Remove the source account from destination choices."""

        if self._updating_account_inputs:
            return

        selected_destination_id = (
            self.destination_account_input.currentData()
        )

        source_account_id = (
            self.source_account_input.currentData()
        )

        self._updating_account_inputs = True

        self.destination_account_input.clear()

        for account in self._accounts:
            if account.account_id == source_account_id:
                continue

            self.destination_account_input.addItem(
                account.name,
                account.account_id,
            )

        destination_index = (
            self.destination_account_input.findData(
                selected_destination_id
            )
        )

        if destination_index >= 0:
            self.destination_account_input.setCurrentIndex(
                destination_index
            )

        self._updating_account_inputs = False

    def _destination_account_changed(self) -> None:
        """Ensure the source and destination remain different."""

        if self._updating_account_inputs:
            return

        source_account_id = (
            self.source_account_input.currentData()
        )
        destination_account_id = (
            self.destination_account_input.currentData()
        )

        if source_account_id != destination_account_id:
            return

        self._source_account_changed()

    def _configure_mode(self) -> None:
        """Configure the dialog for creating or editing."""

        save_button = self.button_box.button(
            QDialogButtonBox.StandardButton.Save
        )

        if self._transfer_transaction is None:
            self.setWindowTitle(
                "Transfer Money"
            )

            if isinstance(
                save_button,
                QPushButton,
            ):
                save_button.setText(
                    "Transfer"
                )

            return

        self.setWindowTitle(
            "Edit Transfer"
        )

        source_transaction = (
            self._transfer_transaction
        )

        source_account_id = (
            source_transaction.account_id
            if source_transaction.amount_cents < 0
            else source_transaction.transfer_account_id
        )

        destination_account_id = (
            source_transaction.transfer_account_id
            if source_transaction.amount_cents < 0
            else source_transaction.account_id
        )

        source_index = (
            self.source_account_input.findData(
                source_account_id
            )
        )

        if source_index >= 0:
            self.source_account_input.setCurrentIndex(
                source_index
            )

        self._source_account_changed()

        destination_index = (
            self.destination_account_input.findData(
                destination_account_id
            )
        )

        if destination_index >= 0:
            self.destination_account_input.setCurrentIndex(
                destination_index
            )

        self.amount_input.setValue(
            cents_to_dollars(
                abs(
                    source_transaction.amount_cents
                )
            )
        )

        self.date_input.setDate(
            QDate(
                source_transaction.transaction_date.year,
                source_transaction.transaction_date.month,
                source_transaction.transaction_date.day,
            )
        )

        self.notes_input.setPlainText(
            source_transaction.notes
        )

        self.cleared_input.setChecked(
            source_transaction.is_cleared
        )

        if isinstance(
            save_button,
            QPushButton,
        ):
            save_button.setText(
                "Save Changes"
            )

    def _validate(self) -> None:
        """Validate the transfer before accepting."""

        if len(self._accounts) < 2:
            self.show_error(
                "At least two accounts are required "
                "to create a transfer."
            )
            return

        source_account_id = (
            self.source_account_input.currentData()
        )
        destination_account_id = (
            self.destination_account_input.currentData()
        )

        if source_account_id is None:
            self.show_error(
                "Select the account sending the money."
            )
            return

        if destination_account_id is None:
            self.show_error(
                "Select the account receiving the money."
            )
            return

        if source_account_id == destination_account_id:
            self.show_error(
                "The source and destination accounts "
                "must be different."
            )
            return

        if self.amount_input.value() <= 0:
            self.show_error(
                "Transfer amount must be greater than zero."
            )
            self.amount_input.setFocus()
            return

        self.error_label.hide()
        self.accept()