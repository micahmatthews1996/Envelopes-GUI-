from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from models.account import Account
from utils.money import cents_to_dollars


ACCOUNT_TYPES = (
    "Checking",
    "Savings",
    "Cash",
)


class AccountDialog(QDialog):
    """Collect account information for account creation or editing."""

    def __init__(
        self,
        parent: QWidget | None = None,
        account: Account | None = None,
    ) -> None:
        super().__init__(parent)

        self._account = account

        self.setModal(True)
        self.setMinimumWidth(420)

        self.name_input = QLineEdit(self)
        self.name_input.setPlaceholderText(
            "For example: Everyday Checking"
        )
        self.name_input.setMaxLength(50)

        self.account_type_input = QComboBox(self)

        for account_type in ACCOUNT_TYPES:
            self.account_type_input.addItem(
                account_type
            )

        self.balance_input = QDoubleSpinBox(self)
        self.balance_input.setRange(
            -999_999_999.99,
            999_999_999.99,
        )
        self.balance_input.setDecimals(2)
        self.balance_input.setPrefix("$")
        self.balance_input.setSingleStep(10.00)

        self.error_label = QLabel(self)
        self.error_label.setObjectName(
            "dialogError"
        )
        self.error_label.setWordWrap(True)
        self.error_label.hide()

        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        form_layout.addRow(
            "Account name:",
            self.name_input,
        )
        form_layout.addRow(
            "Account type:",
            self.account_type_input,
        )
        form_layout.addRow(
            "Opening balance:",
            self.balance_input,
        )

        self.button_box = QDialogButtonBox(
            (
                QDialogButtonBox.StandardButton.Save
                | QDialogButtonBox.StandardButton.Cancel
            ),
            parent=self,
        )

        self.button_box.accepted.connect(
            self._validate
        )
        self.button_box.rejected.connect(
            self.reject
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

        self._configure_mode()
        self.name_input.setFocus()

    def get_account_data(
        self,
    ) -> tuple[str, str, float]:
        """Return the account values entered by the user."""

        return (
            self.name_input.text().strip(),
            self.account_type_input.currentText(),
            self.balance_input.value(),
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

    def _configure_mode(self) -> None:
        """Configure the dialog for account creation or editing."""

        save_button = self.button_box.button(
            QDialogButtonBox.StandardButton.Save
        )

        if self._account is None:
            self.setWindowTitle(
                "Add Account"
            )

            self.account_type_input.setCurrentText(
                "Checking"
            )

            if isinstance(
                save_button,
                QPushButton,
            ):
                save_button.setText(
                    "Create"
                )

            return

        self.setWindowTitle(
            "Edit Account"
        )

        self.name_input.setText(
            self._account.name
        )

        account_type_index = (
            self.account_type_input.findText(
                self._account.account_type
            )
        )

        if account_type_index >= 0:
            self.account_type_input.setCurrentIndex(
                account_type_index
            )
        else:
            self.account_type_input.setCurrentText(
                "Checking"
            )

        opening_balance = cents_to_dollars(
            self._account.opening_balance_cents
        )

        self.balance_input.setValue(
            float(opening_balance)
        )

        if isinstance(
            save_button,
            QPushButton,
        ):
            save_button.setText(
                "Save Changes"
            )

    def _validate(self) -> None:
        """Perform basic dialog validation."""

        account_name = (
            self.name_input.text().strip()
        )

        if not account_name:
            self.show_error(
                "Please enter an account name."
            )
            self.name_input.setFocus()
            return

        account_type = (
            self.account_type_input.currentText().strip()
        )

        if account_type not in ACCOUNT_TYPES:
            self.show_error(
                "Please select a valid account type."
            )
            self.account_type_input.setFocus()
            return

        self.error_label.hide()
        self.accept()