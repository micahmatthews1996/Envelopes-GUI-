from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from gui.styles.category_colors import CATEGORY_COLORS
from models.category import Category


DEFAULT_CATEGORY_COLOR = CATEGORY_COLORS[0]


class ColorButton(QPushButton):
    """A selectable color swatch."""

    def __init__(
        self,
        color: str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self.color = color

        self.setCheckable(True)
        self.setFixedSize(28, 28)
        self.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        self._refresh_style()

        self.toggled.connect(
            lambda _: self._refresh_style()
        )

    def _refresh_style(self) -> None:

        border = (
            "3px solid #172033"
            if self.isChecked()
            else "1px solid #CBD2DA"
        )

        self.setStyleSheet(
            f"""
            QPushButton {{
                background:{self.color};
                border:{border};
                border-radius:14px;
            }}

            QPushButton:hover {{
                border:2px solid #2F80ED;
            }}
            """
        )


class CategoryDialog(QDialog):
    """Collect category information."""

    def __init__(
        self,
        parent: QWidget | None = None,
        category: Category | None = None,
    ) -> None:

        super().__init__(parent)

        self._category = category
        self._selected_color = DEFAULT_CATEGORY_COLOR

        self.setWindowTitle("Category")
        self.setModal(True)
        self.setMinimumWidth(450)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText(
            "Groceries"
        )
        self.name_input.setMaxLength(50)

        self.type_input = QComboBox()
        self.type_input.addItems(
            [
                "Expense",
                "Income",
            ]
        )

        self.error_label = QLabel()
        self.error_label.setObjectName(
            "dialogError"
        )
        self.error_label.hide()

        self.color_group = QButtonGroup(self)
        self.color_group.setExclusive(True)

        color_grid = QGridLayout()
        color_grid.setHorizontalSpacing(10)
        color_grid.setVerticalSpacing(10)

        for index, color in enumerate(
            CATEGORY_COLORS
        ):

            button = ColorButton(color)

            self.color_group.addButton(button)

            row = index // 6
            column = index % 6

            color_grid.addWidget(
                button,
                row,
                column,
            )

            if color == DEFAULT_CATEGORY_COLOR:
                button.setChecked(True)

        form_layout = QFormLayout()

        form_layout.addRow(
            "Category Name:",
            self.name_input,
        )

        form_layout.addRow(
            "Category Type:",
            self.type_input,
        )

        color_widget = QWidget()
        color_widget.setLayout(color_grid)

        form_layout.addRow(
            "Category Color:",
            color_widget,
        )

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            |
            QDialogButtonBox.StandardButton.Cancel
        )

        buttons.accepted.connect(
            self._accept
        )

        buttons.rejected.connect(
            self.reject
        )

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            24,
            24,
            24,
            24,
        )

        layout.setSpacing(20)

        layout.addLayout(form_layout)
        layout.addWidget(self.error_label)
        layout.addWidget(buttons)

        self._populate_existing_values()

    def get_category_data(
        self,
    ) -> tuple[str, str, str]:

        return (
            self.name_input.text().strip(),
            self.type_input.currentText(),
            self._selected_color,
        )

    def show_error(
        self,
        message: str,
    ) -> None:

        self.error_label.setText(message)
        self.error_label.show()

    def _populate_existing_values(
        self,
    ) -> None:

        if self._category is None:
            return

        self.setWindowTitle(
            "Edit Category"
        )

        self.name_input.setText(
            self._category.name
        )

        index = self.type_input.findText(
            self._category.category_type
        )

        if index >= 0:
            self.type_input.setCurrentIndex(
                index
            )

        self._selected_color = (
            self._category.color
        )

        for button in self.color_group.buttons():

            color_button = button

            if (
                color_button.color
                ==
                self._selected_color
            ):
                color_button.setChecked(True)
                break

    def _accept(
        self,
    ) -> None:

        name = self.name_input.text().strip()

        if not name:

            self.show_error(
                "Please enter a category name."
            )

            return

        checked = self.color_group.checkedButton()

        if checked is not None:
            self._selected_color = checked.color

        self.accept()