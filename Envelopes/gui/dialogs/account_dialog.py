from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QWidget,
)


class AccountDialog(QDialog):
    """Dialog used to collect information for a new account."""

    def __init__(
        self,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self.setWindowTitle("Add Account")
        self.setModal(True)
        self.setMinimumWidth(420)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText(
            "For example: Checking"
        )
        self.name_input.setMaxLength(50)

        self.balance_input = QDoubleSpinBox()
        self.balance_input.setRange(
            -999_999_999.99,
            999_999_999.99,
        )
        self.balance_input.setDecimals(2)
        self.balance_input.setPrefix("$")
        self.balance_input.setSingleStep(10.00)

        self.error_label = QLabel()
        self.error_label.setObjectName("dialogError")
        self.error_label.setWordWrap(True)
        self.error_label.hide()

        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        form_layout.addRow(
            "Account name:",
            self.name_input,
        )
        form_layout.addRow(
            "Opening balance:",
            self.balance_input,
        )

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )

        self.button_box.accepted.connect(self._validate)
        self.button_box.rejected.connect(self.reject)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(18)

        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.error_label)
        main_layout.addWidget(self.button_box)

        self.name_input.setFocus()

    def get_account_data(self) -> tuple[str, float]:
        """Return the values entered by the user."""

        return (
            self.name_input.text().strip(),
            self.balance_input.value(),
        )

    def show_error(self, message: str) -> None:
        """Display a validation error in the dialog."""

        self.error_label.setText(message)
        self.error_label.show()

    def _validate(self) -> None:
        """Perform basic dialog validation."""

        account_name = self.name_input.text().strip()

        if not account_name:
            self.show_error("Please enter an account name.")
            self.name_input.setFocus()
            return

        self.accept()