from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from models.budget import Budget
from models.category import Category
from utils.money import cents_to_dollars


DELETE_RESULT = 2


class BudgetDialog(QDialog):
    """Collect information for creating, editing, or deleting a budget."""

    def __init__(
        self,
        categories: list[Category],
        parent: QWidget | None = None,
        budget: Budget | None = None,
    ) -> None:
        super().__init__(parent)

        self._categories = categories
        self._budget = budget

        self.setModal(True)
        self.setMinimumWidth(440)

        self._category_input = QComboBox(self)

        for category in self._categories:
            self._category_input.addItem(
                category.name,
                category.category_id,
            )

        self._monthly_limit_input = QDoubleSpinBox(self)
        self._monthly_limit_input.setRange(
            0.01,
            999_999_999.99,
        )
        self._monthly_limit_input.setDecimals(2)
        self._monthly_limit_input.setPrefix("$")
        self._monthly_limit_input.setSingleStep(10.00)

        self._error_label = QLabel(self)
        self._error_label.setObjectName(
            "dialogError"
        )
        self._error_label.setWordWrap(True)
        self._error_label.hide()

        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        form_layout.addRow(
            "Expense category:",
            self._category_input,
        )
        form_layout.addRow(
            "Monthly limit:",
            self._monthly_limit_input,
        )

        self._button_box = QDialogButtonBox(
            parent=self
        )

        self._save_button = (
            self._button_box.addButton(
                QDialogButtonBox.StandardButton.Save
            )
        )
        self._cancel_button = (
            self._button_box.addButton(
                QDialogButtonBox.StandardButton.Cancel
            )
        )

        self._delete_button: QPushButton | None = None

        if self._budget is not None:
            self._delete_button = (
                self._button_box.addButton(
                    "Delete",
                    QDialogButtonBox.ButtonRole.DestructiveRole,
                )
            )
            self._delete_button.setObjectName(
                "dangerTextButton"
            )
            self._delete_button.setCursor(
                Qt.CursorShape.PointingHandCursor
            )
            self._delete_button.clicked.connect(
                self._delete_requested
            )

        self._save_button.clicked.connect(
            self._validate_and_accept
        )
        self._cancel_button.clicked.connect(
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
        main_layout.addLayout(form_layout)
        main_layout.addWidget(
            self._error_label
        )
        main_layout.addWidget(
            self._button_box
        )

        self._configure_mode()

    def _configure_mode(self) -> None:
        """Configure the dialog for create or edit mode."""

        if self._budget is None:
            self.setWindowTitle(
                "Add Budget"
            )
            self._save_button.setText(
                "Create"
            )
            return

        self.setWindowTitle(
            "Edit Budget"
        )

        category_index = (
            self._category_input.findData(
                self._budget.category_id
            )
        )

        if category_index >= 0:
            self._category_input.setCurrentIndex(
                category_index
            )

        self._monthly_limit_input.setValue(
            float(
                cents_to_dollars(
                    self._budget.monthly_limit_cents
                )
            )
        )

        self._save_button.setText(
            "Save Changes"
        )

    def _validate_and_accept(self) -> None:
        """Validate the entered budget values."""

        if self._category_input.currentData() is None:
            self.show_error(
                "Select an expense category."
            )
            self._category_input.setFocus()
            return

        if self._monthly_limit_input.value() <= 0:
            self.show_error(
                "Monthly budget must be greater than zero."
            )
            self._monthly_limit_input.setFocus()
            return

        self._error_label.hide()
        self.accept()

    def _delete_requested(self) -> None:
        """Confirm deletion of the current budget."""

        if self._budget is None:
            return

        response = QMessageBox.question(
            self,
            "Delete Budget",
            (
                "Delete this monthly budget?\n\n"
                "Existing transactions will not be changed."
            ),
            (
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No
            ),
            QMessageBox.StandardButton.No,
        )

        if response == QMessageBox.StandardButton.Yes:
            self.done(DELETE_RESULT)

    def get_budget_data(
        self,
    ) -> tuple[str, float]:
        """Return the validated budget data."""

        return (
            str(
                self._category_input.currentData()
            ),
            self._monthly_limit_input.value(),
        )

    def show_error(
        self,
        message: str,
    ) -> None:
        """Display a validation error."""

        self._error_label.setText(
            message
        )
        self._error_label.show()