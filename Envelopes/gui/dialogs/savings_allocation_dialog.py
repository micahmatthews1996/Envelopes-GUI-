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

from models.savings_goal import SavingsGoal
from services.savings_goal_service import (
    SavingsGoalService,
)
from utils.money import (
    cents_to_dollars,
    format_currency,
)


class SavingsAllocationDialog(QDialog):
    """Collect information for allocating savings to a goal."""

    def __init__(
        self,
        savings_goal_service: SavingsGoalService,
        available_amount_cents: int,
        parent: QWidget | None = None,
        selected_goal_id: str | None = None,
        initial_amount_cents: int = 0,
        initial_notes: str = "",
    ) -> None:
        super().__init__(parent)

        self._savings_goal_service = (
            savings_goal_service
        )
        self._available_amount_cents = max(
            0,
            available_amount_cents,
        )
        self._goals_by_id: dict[
            str,
            SavingsGoal
        ] = {}

        self.setWindowTitle(
            "Allocate Savings"
        )
        self.setModal(True)
        self.setMinimumWidth(480)

        self._create_interface()
        self._load_goals(
            selected_goal_id
        )
        self._load_initial_values(
            initial_amount_cents=(
                initial_amount_cents
            ),
            initial_notes=initial_notes,
        )

    def _create_interface(self) -> None:
        """Create the savings-allocation interface."""

        available_caption = QLabel(
            "Available savings",
            self,
        )
        available_caption.setObjectName(
            "listCardSecondaryText"
        )

        self._available_amount_label = QLabel(
            format_currency(
                self._available_amount_cents
            ),
            self,
        )
        self._available_amount_label.setObjectName(
            "listCardTrailingText"
        )

        available_layout = QVBoxLayout()
        available_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        available_layout.setSpacing(4)
        available_layout.addWidget(
            available_caption
        )
        available_layout.addWidget(
            self._available_amount_label
        )

        self._goal_input = QComboBox(self)
        self._goal_input.currentIndexChanged.connect(
            self._goal_changed
        )

        self._goal_progress_label = QLabel(self)
        self._goal_progress_label.setObjectName(
            "listCardSecondaryText"
        )
        self._goal_progress_label.setWordWrap(True)

        goal_container = QWidget(self)
        goal_layout = QVBoxLayout(
            goal_container
        )
        goal_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        goal_layout.setSpacing(6)
        goal_layout.addWidget(
            self._goal_input
        )
        goal_layout.addWidget(
            self._goal_progress_label
        )

        self._amount_input = QDoubleSpinBox(self)
        self._amount_input.setDecimals(2)
        self._amount_input.setPrefix("$")
        self._amount_input.setSingleStep(10.00)
        self._amount_input.setRange(
            0.01,
            max(
                0.01,
                float(
                    cents_to_dollars(
                        self._available_amount_cents
                    )
                ),
            ),
        )

        self._notes_input = QPlainTextEdit(self)
        self._notes_input.setPlaceholderText(
            "Optional note about this allocation"
        )
        self._notes_input.setMaximumHeight(100)

        form_layout = QFormLayout()
        form_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        form_layout.setHorizontalSpacing(18)
        form_layout.setVerticalSpacing(14)
        form_layout.setLabelAlignment(
            Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignTop
        )

        form_layout.addRow(
            "Savings goal:",
            goal_container,
        )
        form_layout.addRow(
            "Amount:",
            self._amount_input,
        )
        form_layout.addRow(
            "Notes:",
            self._notes_input,
        )

        self._error_label = QLabel(self)
        self._error_label.setObjectName(
            "dialogError"
        )
        self._error_label.setWordWrap(True)
        self._error_label.hide()

        self._button_box = QDialogButtonBox(
            (
                QDialogButtonBox.StandardButton.Save
                | QDialogButtonBox.StandardButton.Cancel
            ),
            parent=self,
        )

        allocate_button = self._button_box.button(
            QDialogButtonBox.StandardButton.Save
        )

        if isinstance(
            allocate_button,
            QPushButton,
        ):
            allocate_button.setText(
                "Allocate"
            )
            allocate_button.setObjectName(
                "primaryButton"
            )

        self._button_box.accepted.connect(
            self._validate_and_accept
        )
        self._button_box.rejected.connect(
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
            available_layout
        )
        main_layout.addLayout(
            form_layout
        )
        main_layout.addWidget(
            self._error_label
        )
        main_layout.addWidget(
            self._button_box
        )

    def _load_goals(
        self,
        selected_goal_id: str | None,
    ) -> None:
        """Load active, incomplete savings goals."""

        goals = (
            self._savings_goal_service.get_goals()
        )

        incomplete_goals = [
            goal
            for goal in goals
            if not goal.is_completed
        ]

        incomplete_goals.sort(
            key=lambda goal: (
                goal.name.casefold()
            )
        )

        self._goal_input.clear()
        self._goals_by_id.clear()

        for goal in incomplete_goals:
            self._goals_by_id[
                goal.goal_id
            ] = goal

            self._goal_input.addItem(
                goal.name,
                goal.goal_id,
            )

        if selected_goal_id is not None:
            selected_index = (
                self._goal_input.findData(
                    selected_goal_id
                )
            )

            if selected_index >= 0:
                self._goal_input.setCurrentIndex(
                    selected_index
                )

        has_goals = (
            self._goal_input.count() > 0
        )

        self._goal_input.setEnabled(
            has_goals
        )
        self._amount_input.setEnabled(
            has_goals
            and self._available_amount_cents > 0
        )

        allocate_button = self._button_box.button(
            QDialogButtonBox.StandardButton.Save
        )

        if allocate_button is not None:
            allocate_button.setEnabled(
                has_goals
                and self._available_amount_cents > 0
            )

        if not has_goals:
            self.show_error(
                "There are no active savings goals "
                "available for allocation."
            )
            self._goal_progress_label.setText(
                "Create a savings goal before "
                "allocating savings."
            )
            return

        if self._available_amount_cents <= 0:
            self.show_error(
                "There is no unallocated savings "
                "available."
            )

        self._goal_changed()

    def _load_initial_values(
        self,
        initial_amount_cents: int,
        initial_notes: str,
    ) -> None:
        """Load optional initial allocation values."""

        if initial_amount_cents > 0:
            maximum_cents = (
                self._maximum_allowed_cents()
            )

            amount_cents = min(
                initial_amount_cents,
                maximum_cents,
            )

            self._amount_input.setValue(
                float(
                    cents_to_dollars(
                        amount_cents
                    )
                )
            )
        elif (
            self._goal_input.count() > 0
            and self._available_amount_cents > 0
        ):
            maximum_cents = (
                self._maximum_allowed_cents()
            )

            self._amount_input.setValue(
                float(
                    cents_to_dollars(
                        maximum_cents
                    )
                )
            )

        self._notes_input.setPlainText(
            initial_notes
        )

    def _goal_changed(self) -> None:
        """Update limits when the selected goal changes."""

        goal = self._selected_goal()

        if goal is None:
            self._goal_progress_label.clear()
            return

        remaining_amount_cents = max(
            0,
            (
                goal.target_amount_cents
                - goal.current_amount_cents
            ),
        )

        self._goal_progress_label.setText(
            (
                f"{format_currency(goal.current_amount_cents)} "
                f"saved of "
                f"{format_currency(goal.target_amount_cents)}"
                f" — "
                f"{format_currency(remaining_amount_cents)} "
                "remaining"
            )
        )

        maximum_cents = (
            self._maximum_allowed_cents()
        )

        maximum_dollars = max(
            0.01,
            float(
                cents_to_dollars(
                    maximum_cents
                )
            ),
        )

        self._amount_input.setMaximum(
            maximum_dollars
        )

        if (
            self._amount_input.value()
            > maximum_dollars
        ):
            self._amount_input.setValue(
                maximum_dollars
            )

    def _selected_goal(
        self,
    ) -> SavingsGoal | None:
        """Return the currently selected savings goal."""

        goal_id = self._goal_input.currentData()

        if goal_id is None:
            return None

        return self._goals_by_id.get(
            str(goal_id)
        )

    def _maximum_allowed_cents(self) -> int:
        """Return the maximum allowed allocation."""

        goal = self._selected_goal()

        if goal is None:
            return 0

        remaining_goal_cents = max(
            0,
            (
                goal.target_amount_cents
                - goal.current_amount_cents
            ),
        )

        return min(
            self._available_amount_cents,
            remaining_goal_cents,
        )

    def _validate_and_accept(self) -> None:
        """Validate the allocation before closing."""

        goal = self._selected_goal()

        if goal is None:
            self.show_error(
                "Select a savings goal."
            )
            self._goal_input.setFocus()
            return

        amount_cents = round(
            self._amount_input.value()
            * 100
        )

        if amount_cents <= 0:
            self.show_error(
                "Allocation amount must be "
                "greater than zero."
            )
            self._amount_input.setFocus()
            return

        if (
            amount_cents
            > self._available_amount_cents
        ):
            self.show_error(
                "Allocation cannot exceed the "
                "available savings balance."
            )
            self._amount_input.setFocus()
            return

        remaining_goal_cents = max(
            0,
            (
                goal.target_amount_cents
                - goal.current_amount_cents
            ),
        )

        if amount_cents > remaining_goal_cents:
            self.show_error(
                "Allocation cannot exceed the amount "
                "remaining for this goal."
            )
            self._amount_input.setFocus()
            return

        self._error_label.hide()
        self.accept()

    def get_allocation_data(
        self,
    ) -> tuple[str, int, str]:
        """Return the validated allocation data."""

        goal_id = str(
            self._goal_input.currentData()
        )

        amount_cents = round(
            self._amount_input.value()
            * 100
        )

        notes = (
            self._notes_input
            .toPlainText()
            .strip()
        )

        return (
            goal_id,
            amount_cents,
            notes,
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