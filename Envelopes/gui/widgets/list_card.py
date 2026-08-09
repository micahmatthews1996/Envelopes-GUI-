from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from gui.widgets.section_card import SectionCard


class ListCard(SectionCard):
    """Displays a reusable vertical list inside a section card."""

    def __init__(
        self,
        title: str,
        subtitle: str = "",
        action_text: str = "",
        parent: QWidget | None = None,
    ) -> None:
        self._action_button = QPushButton(action_text)
        self._action_button.setObjectName(
            "listCardActionButton"
        )
        self._action_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        self._action_button.setVisible(
            bool(action_text)
        )

        super().__init__(
            title=title,
            subtitle=subtitle,
            action_widget=self._action_button,
            parent=parent,
        )

        self.setObjectName("listCard")

        self._row_count = 0
        self._empty_widget: QWidget | None = None

    def add_row(
        self,
        primary_text: str,
        secondary_text: str = "",
        trailing_text: str = "",
        row_data: object | None = None,
    ) -> QFrame:
        """Add one text-based row to the list."""

        self._remove_empty_widget()

        row = QFrame()
        row.setObjectName("listCardRow")

        if row_data is not None:
            row.setProperty(
                "row_data",
                row_data,
            )

        primary_label = QLabel(primary_text)
        primary_label.setObjectName(
            "listCardPrimaryText"
        )

        secondary_label = QLabel(
            secondary_text
        )
        secondary_label.setObjectName(
            "listCardSecondaryText"
        )
        secondary_label.setWordWrap(True)
        secondary_label.setVisible(
            bool(secondary_text)
        )

        trailing_label = QLabel(
            trailing_text
        )
        trailing_label.setObjectName(
            "listCardTrailingText"
        )
        trailing_label.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignVCenter
        )
        trailing_label.setVisible(
            bool(trailing_text)
        )

        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        text_layout.setSpacing(3)
        text_layout.addWidget(
            primary_label
        )
        text_layout.addWidget(
            secondary_label
        )

        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(
            14,
            12,
            14,
            12,
        )
        row_layout.setSpacing(14)
        row_layout.addLayout(
            text_layout,
            stretch=1,
        )
        row_layout.addWidget(
            trailing_label
        )

        if self._row_count > 0:
            self.section_layout().addWidget(
                self._create_row_separator()
            )

        self.section_layout().addWidget(row)
        self._row_count += 1

        return row

    def add_custom_row(
        self,
        row_widget: QWidget,
    ) -> None:
        """Add a fully custom row widget."""

        self._remove_empty_widget()

        if self._row_count > 0:
            self.section_layout().addWidget(
                self._create_row_separator()
            )

        self.section_layout().addWidget(
            row_widget
        )
        self._row_count += 1

    def set_empty_state(
        self,
        title: str,
        description: str,
    ) -> None:
        """Show an empty-state message when the list has no rows."""

        self.clear_rows()

        empty_widget = QWidget()
        empty_widget.setObjectName(
            "listCardEmptyState"
        )

        title_label = QLabel(title)
        title_label.setObjectName(
            "listCardEmptyTitle"
        )
        title_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        description_label = QLabel(
            description
        )
        description_label.setObjectName(
            "listCardEmptyDescription"
        )
        description_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        description_label.setWordWrap(True)

        empty_layout = QVBoxLayout(
            empty_widget
        )
        empty_layout.setContentsMargins(
            24,
            30,
            24,
            30,
        )
        empty_layout.setSpacing(8)
        empty_layout.addWidget(
            title_label
        )
        empty_layout.addWidget(
            description_label
        )

        self.section_layout().addWidget(
            empty_widget
        )

        self._empty_widget = empty_widget

    def clear_rows(self) -> None:
        """Remove all list rows and separators."""

        layout = self.section_layout()

        while layout.count():
            layout_item = layout.takeAt(0)
            widget = layout_item.widget()

            if widget is not None:
                widget.deleteLater()

        self._row_count = 0
        self._empty_widget = None

    def action_button(self) -> QPushButton:
        """Return the optional section action button."""

        return self._action_button

    def row_count(self) -> int:
        """Return the number of visible list rows."""

        return self._row_count

    def _remove_empty_widget(self) -> None:
        """Remove the current empty state before adding rows."""

        if self._empty_widget is None:
            return

        self.section_layout().removeWidget(
            self._empty_widget
        )
        self._empty_widget.deleteLater()
        self._empty_widget = None

    def _create_row_separator(self) -> QWidget:
        """Create a divider between list rows."""

        separator = QWidget()
        separator.setObjectName(
            "listCardRowSeparator"
        )
        separator.setFixedHeight(1)

        return separator