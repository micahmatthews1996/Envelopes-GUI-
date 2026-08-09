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
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from models.account import Account
from models.category import Category
from models.transaction import Transaction
from utils.money import cents_to_dollars


class TransactionDialog(QDialog):
    """Collect information for creating or editing a transaction."""

    def __init__(
        self,
        accounts: list[Account],
        categories: list[Category],
        parent: QWidget | None = None,
        transaction: Transaction | None = None,
    ) -> None:
        super().__init__(parent)

        self._accounts = accounts
        self._categories = categories
        self._transaction = transaction

        self.setModal(True)
        self.setMinimumWidth(500)

        self.account_input = QComboBox()
        self.category_input = QComboBox()

        self.payee_input = QLineEdit()
        self.payee_input.setPlaceholderText(
            "For example: Grocery Store"
        )
        self.payee_input.setMaxLength(100)

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
        self.date_input.setDisplayFormat("MM/dd/yyyy")
        self.date_input.setDate(
            QDate.currentDate()
        )

        self.notes_input = QPlainTextEdit()
        self.notes_input.setPlaceholderText(
            "Optional notes about this transaction"
        )
        self.notes_input.setMaximumHeight(120)

        self.cleared_input = QCheckBox(
            "This transaction has cleared"
        )

        self.error_label = QLabel()
        self.error_label.setObjectName("dialogError")
        self.error_label.setWordWrap(True)
        self.error_label.hide()

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
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
            "Account:",
            self.account_input,
        )
        form_layout.addRow(
            "Category:",
            self.category_input,
        )
        form_layout.addRow(
            "Payee:",
            self.payee_input,
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
            "Notes:",
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

        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.error_label)
        main_layout.addWidget(self.button_box)

        self._populate_accounts()
        self._populate_categories()
        self._configure_mode()

        self.payee_input.setFocus()

    def get_transaction_data(
        self,
    ) -> tuple[
        str,
        str,
        str,
        float,
        date,
        str,
        bool,
    ]:
        """Return the values entered by the user."""

        selected_date = self.date_input.date()

        transaction_date = date(
            selected_date.year(),
            selected_date.month(),
            selected_date.day(),
        )

        return (
            str(self.account_input.currentData()),
            str(self.category_input.currentData()),
            self.payee_input.text().strip(),
            self.amount_input.value(),
            transaction_date,
            self.notes_input.toPlainText().strip(),
            self.cleared_input.isChecked(),
        )

    def show_error(
        self,
        message: str,
    ) -> None:
        """Display a validation error inside the dialog."""

        self.error_label.setText(message)
        self.error_label.show()

    def _populate_accounts(self) -> None:
        """Add available accounts to the account selector."""

        self.account_input.clear()

        for account in self._accounts:
            self.account_input.addItem(
                account.name,
                account.account_id,
            )

    def _populate_categories(self) -> None:
        """Add active categories to the category selector."""

        self.category_input.clear()

        expense_categories = [
            category
            for category in self._categories
            if (
                category.category_type == "Expense"
                and not category.is_archived
            )
        ]

        income_categories = [
            category
            for category in self._categories
            if (
                category.category_type == "Income"
                and not category.is_archived
            )
        ]

        for category in expense_categories:
            self.category_input.addItem(
                f"Expense — {category.name}",
                category.category_id,
            )

        for category in income_categories:
            self.category_input.addItem(
                f"Income — {category.name}",
                category.category_id,
            )

    def _configure_mode(self) -> None:
        """Configure the dialog for creation or editing."""

        save_button = self.button_box.button(
            QDialogButtonBox.StandardButton.Save
        )

        if self._transaction is None:
            self.setWindowTitle("Add Transaction")

            if isinstance(save_button, QPushButton):
                save_button.setText("Create")

            return

        self.setWindowTitle("Edit Transaction")

        account_index = self.account_input.findData(
            self._transaction.account_id
        )

        if account_index >= 0:
            self.account_input.setCurrentIndex(
                account_index
            )

        category_index = self.category_input.findData(
            self._transaction.category_id
        )

        if category_index >= 0:
            self.category_input.setCurrentIndex(
                category_index
            )

        self.payee_input.setText(
            self._transaction.payee
        )

        amount = cents_to_dollars(
            abs(self._transaction.amount_cents)
        )

        self.amount_input.setValue(
            float(amount)
        )

        transaction_date = (
            self._transaction.transaction_date
        )

        self.date_input.setDate(
            QDate(
                transaction_date.year,
                transaction_date.month,
                transaction_date.day,
            )
        )

        self.notes_input.setPlainText(
            self._transaction.notes
        )

        self.cleared_input.setChecked(
            self._transaction.is_cleared
        )

        if isinstance(save_button, QPushButton):
            save_button.setText("Save Changes")

    def _validate(self) -> None:
        """Perform immediate dialog validation."""

        if self.account_input.count() == 0:
            self.show_error(
                "Create an account before adding transactions."
            )
            return

        if self.category_input.count() == 0:
            self.show_error(
                "Create an active category before adding transactions."
            )
            return

        if not self.payee_input.text().strip():
            self.show_error(
                "Please enter a payee."
            )
            self.payee_input.setFocus()
            return

        if self.amount_input.value() <= 0:
            self.show_error(
                "Transaction amount must be greater than zero."
            )
            self.amount_input.setFocus()
            return

        if len(self.notes_input.toPlainText().strip()) > 2000:
            self.show_error(
                "Notes cannot exceed 2,000 characters."
            )
            self.notes_input.setFocus()
            return

        self.accept()