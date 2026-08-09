from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from gui.widgets.card import Card


class DashboardSection(Card):
    """Reusable card container for one Dashboard section."""

    def __init__(
        self,
        title: str,
        subtitle: str = "",
        action_text: str = "",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self.setObjectName("dashboardSection")

        self._action_button = QPushButton(
            action_text
        )
        self._action_button.setObjectName(
            "dashboardSectionActionButton"
        )
        self._action_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        if not action_text:
            self._action_button.hide()

        title_label = QLabel(title)
        title_label.setObjectName(
            "dashboardSectionTitle"
        )

        subtitle_label = QLabel(subtitle)
        subtitle_label.setObjectName(
            "dashboardSectionSubtitle"
        )
        subtitle_label.setWordWrap(True)

        if not subtitle:
            subtitle_label.hide()

        title_layout = QVBoxLayout()
        title_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        title_layout.setSpacing(3)
        title_layout.addWidget(
            title_label
        )
        title_layout.addWidget(
            subtitle_label
        )

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        header_layout.setSpacing(12)
        header_layout.addLayout(
            title_layout,
            stretch=1,
        )
        header_layout.addWidget(
            self._action_button,
            alignment=Qt.AlignmentFlag.AlignTop,
        )

        separator = QWidget()
        separator.setObjectName(
            "dashboardSectionSeparator"
        )
        separator.setFixedHeight(1)

        self._section_layout = QVBoxLayout()
        self._section_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        self._section_layout.setSpacing(0)

        card_layout = self.content_layout()

        if not isinstance(
            card_layout,
            QVBoxLayout,
        ):
            raise RuntimeError(
                "DashboardSection requires "
                "a vertical card layout."
            )

        card_layout.addLayout(
            header_layout
        )
        card_layout.addWidget(
            separator
        )
        card_layout.addLayout(
            self._section_layout,
            stretch=1,
        )

    def add_widget(
        self,
        widget: QWidget,
        stretch: int = 0,
        alignment: Qt.AlignmentFlag | None = None,
    ) -> None:
        """Add a widget to the section content area."""

        if alignment is None:
            self._section_layout.addWidget(
                widget,
                stretch,
            )
            return

        self._section_layout.addWidget(
            widget,
            stretch,
            alignment,
        )

    def add_layout(
        self,
        layout: QHBoxLayout | QVBoxLayout,
        stretch: int = 0,
    ) -> None:
        """Add a layout to the section content area."""

        self._section_layout.addLayout(
            layout,
            stretch,
        )

    def clear_content(self) -> None:
        """Remove all widgets and layouts from the section."""

        while self._section_layout.count():
            layout_item = (
                self._section_layout.takeAt(0)
            )

            widget = layout_item.widget()

            if widget is not None:
                widget.deleteLater()
                continue

            child_layout = layout_item.layout()

            if child_layout is not None:
                self._delete_layout(
                    child_layout
                )

    def content_area(
        self,
    ) -> QVBoxLayout:
        """Return the section content layout."""

        return self._section_layout

    def action_button(
        self,
    ) -> QPushButton:
        """Return the optional action button."""

        return self._action_button

    def set_action_text(
        self,
        action_text: str,
    ) -> None:
        """Update or hide the action button."""

        self._action_button.setText(
            action_text
        )

        if action_text:
            self._action_button.show()
        else:
            self._action_button.hide()

    def _delete_layout(
        self,
        layout: QHBoxLayout | QVBoxLayout,
    ) -> None:
        """Delete all widgets and child layouts."""

        while layout.count():
            layout_item = layout.takeAt(0)
            widget = layout_item.widget()

            if widget is not None:
                widget.deleteLater()
                continue

            child_layout = layout_item.layout()

            if child_layout is not None:
                self._delete_layout(
                    child_layout
                )