from datetime import date

from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QDoubleValidator
from PySide6.QtWidgets import (
    QCalendarWidget,
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from models.savings_goal import SavingsGoal


DELETE_RESULT = 2


class SavingsGoalDialog(QDialog):
    """Creates, edits, or requests deletion of a savings goal."""

    def __init__(
        self,
        parent: QWidget | None = None,
        goal: SavingsGoal | None = None,
    ) -> None:
        super().__init__(parent)

        self._goal = goal
        self._selected_target_date = (
            QDate.currentDate().addMonths(6)
        )

        self.setWindowTitle(
            "Add Savings Goal"
            if goal is None
            else "Edit Savings Goal"
        )
        self.setModal(True)
        self.setMinimumWidth(460)

        self._create_interface()
        self._load_goal()

    def _create_interface(self) -> None:
        """Create the savings goal dialog interface."""

        self._name_input = QLineEdit(self)
        self._name_input.setPlaceholderText(
            "Example: Emergency Fund"
        )
        self._name_input.setMaxLength(80)

        self._target_amount_input = QLineEdit(self)
        self._target_amount_input.setPlaceholderText(
            "0.00"
        )
        self._target_amount_input.setAlignment(
            Qt.AlignmentFlag.AlignRight
        )

        amount_validator = QDoubleValidator(
            0.01,
            999999999.99,
            2,
            self,
        )
        amount_validator.setNotation(
            QDoubleValidator.Notation.StandardNotation
        )

        self._target_amount_input.setValidator(
            amount_validator
        )

        amount_container = QWidget(self)

        amount_layout = QFormLayout(
            amount_container
        )
        amount_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        amount_layout.setHorizontalSpacing(8)
        amount_layout.addRow(
            "$",
            self._target_amount_input,
        )

        self._use_target_date_checkbox = QCheckBox(
            "Include a target date",
            self,
        )
        self._use_target_date_checkbox.setChecked(
            True
        )
        self._use_target_date_checkbox.toggled.connect(
            self._target_date_toggled
        )

        self._target_date_button = QPushButton(self)
        self._target_date_button.setObjectName(
            "secondaryButton"
        )
        self._target_date_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        self._target_date_button.clicked.connect(
            self._open_calendar_dialog
        )

        target_date_container = QWidget(self)

        target_date_layout = QVBoxLayout(
            target_date_container
        )
        target_date_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        target_date_layout.setSpacing(8)
        target_date_layout.addWidget(
            self._use_target_date_checkbox
        )
        target_date_layout.addWidget(
            self._target_date_button
        )

        form_layout = QFormLayout()
        form_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        form_layout.setHorizontalSpacing(18)
        form_layout.setVerticalSpacing(16)
        form_layout.setLabelAlignment(
            Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignTop
        )

        form_layout.addRow(
            "Goal name",
            self._name_input,
        )
        form_layout.addRow(
            "Target amount",
            amount_container,
        )
        form_layout.addRow(
            "Target date",
            target_date_container,
        )

        self._error_label = QLabel(self)
        self._error_label.setObjectName(
            "dialogError"
        )
        self._error_label.setWordWrap(True)
        self._error_label.hide()

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

        if self._goal is not None:
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
        main_layout.addLayout(
            form_layout
        )
        main_layout.addWidget(
            self._error_label
        )
        main_layout.addWidget(
            self._button_box
        )

        self._update_target_date_button()

    def _load_goal(self) -> None:
        """Load an existing goal into the dialog."""

        if self._goal is None:
            self._name_input.setFocus()
            return

        self._name_input.setText(
            self._goal.name
        )

        self._target_amount_input.setText(
            f"{self._goal.target_amount_cents / 100:.2f}"
        )

        if self._goal.target_date is None:
            self._use_target_date_checkbox.setChecked(
                False
            )
        else:
            self._selected_target_date = QDate(
                self._goal.target_date.year,
                self._goal.target_date.month,
                self._goal.target_date.day,
            )

            self._use_target_date_checkbox.setChecked(
                True
            )

        self._update_target_date_button()

        self._name_input.selectAll()
        self._name_input.setFocus()

    def _target_date_toggled(
        self,
        enabled: bool,
    ) -> None:
        """Enable or disable the target-date selector."""

        self._target_date_button.setEnabled(
            enabled
        )

    def _open_calendar_dialog(self) -> None:
        """Open a calendar for selecting the target date."""

        calendar_dialog = QDialog(self)
        calendar_dialog.setWindowTitle(
            "Choose Target Date"
        )
        calendar_dialog.setModal(True)
        calendar_dialog.setMinimumWidth(360)

        calendar = QCalendarWidget(
            calendar_dialog
        )
        calendar.setGridVisible(True)
        calendar.setMinimumDate(
            QDate.currentDate()
        )
        calendar.setSelectedDate(
            self._selected_target_date
        )

        button_box = QDialogButtonBox(
            (
                QDialogButtonBox.StandardButton.Ok
                | QDialogButtonBox.StandardButton.Cancel
            ),
            parent=calendar_dialog,
        )

        button_box.accepted.connect(
            calendar_dialog.accept
        )
        button_box.rejected.connect(
            calendar_dialog.reject
        )

        calendar.activated.connect(
            lambda selected_date: (
                self._select_calendar_date(
                    calendar_dialog,
                    selected_date,
                )
            )
        )

        layout = QVBoxLayout(
            calendar_dialog
        )
        layout.setContentsMargins(
            20,
            20,
            20,
            20,
        )
        layout.setSpacing(16)
        layout.addWidget(
            calendar
        )
        layout.addWidget(
            button_box
        )

        if calendar_dialog.exec():
            self._selected_target_date = (
                calendar.selectedDate()
            )
            self._update_target_date_button()

    def _select_calendar_date(
        self,
        calendar_dialog: QDialog,
        selected_date: QDate,
    ) -> None:
        """Accept a date selected from the calendar."""

        self._selected_target_date = (
            selected_date
        )
        calendar_dialog.accept()

    def _update_target_date_button(self) -> None:
        """Display the selected target date."""

        self._target_date_button.setText(
            self._selected_target_date.toString(
                "MMMM d, yyyy"
            )
        )

        self._target_date_button.setEnabled(
            self._use_target_date_checkbox.isChecked()
        )

    def _validate_and_accept(self) -> None:
        """Validate the entered goal before saving."""

        goal_name = (
            self._name_input.text().strip()
        )

        amount_text = (
            self._target_amount_input
            .text()
            .strip()
        )

        if not goal_name:
            self.show_error(
                "Enter a name for the savings goal."
            )
            self._name_input.setFocus()
            return

        if not amount_text:
            self.show_error(
                "Enter a target amount."
            )
            self._target_amount_input.setFocus()
            return

        try:
            target_amount = float(
                amount_text
            )
        except ValueError:
            self.show_error(
                "Enter a valid target amount."
            )
            self._target_amount_input.setFocus()
            return

        if target_amount <= 0:
            self.show_error(
                "The target amount must be greater than zero."
            )
            self._target_amount_input.setFocus()
            return

        if (
            self._use_target_date_checkbox.isChecked()
            and self._selected_target_date
            < QDate.currentDate()
        ):
            self.show_error(
                "The target date cannot be in the past."
            )
            self._target_date_button.setFocus()
            return

        self._error_label.hide()
        self.accept()

    def _delete_requested(self) -> None:
        """Confirm deletion of the current savings goal."""

        if self._goal is None:
            return

        response = QMessageBox.question(
            self,
            "Delete Savings Goal",
            (
                f'Are you sure you want to delete '
                f'"{self._goal.name}"?\n\n'
                "The goal will be archived. "
                "This will not change any account balances."
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

        self.done(DELETE_RESULT)

    def get_goal_data(
        self,
    ) -> tuple[str, int, date | None]:
        """Return the validated savings goal data."""

        goal_name = (
            self._name_input.text().strip()
        )

        target_amount_cents = round(
            float(
                self._target_amount_input
                .text()
                .strip()
            )
            * 100
        )

        target_date: date | None = None

        if self._use_target_date_checkbox.isChecked():
            target_date = date(
                self._selected_target_date.year(),
                self._selected_target_date.month(),
                self._selected_target_date.day(),
            )

        return (
            goal_name,
            target_amount_cents,
            target_date,
        )

    def show_error(
        self,
        message: str,
    ) -> None:
        """Display an error message inside the dialog."""

        self._error_label.setText(
            message
        )
        self._error_label.show()