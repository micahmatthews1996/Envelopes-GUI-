from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from gui.widgets.card import Card


class SectionCard(Card):
    """Card with a title, optional subtitle, action, and content area."""

    def __init__(
        self,
        title: str,
        subtitle: str = "",
        action_widget: QWidget | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self.setObjectName("sectionCard")

        self._content_layout = QVBoxLayout()
        self._content_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        self._content_layout.setSpacing(12)

        title_label = QLabel(title)
        title_label.setObjectName("sectionCardTitle")

        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        text_layout.setSpacing(3)
        text_layout.addWidget(title_label)

        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setObjectName(
                "sectionCardSubtitle"
            )
            subtitle_label.setWordWrap(True)
            text_layout.addWidget(subtitle_label)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        header_layout.setSpacing(12)
        header_layout.addLayout(
            text_layout,
            stretch=1,
        )

        if action_widget is not None:
            header_layout.addWidget(
                action_widget,
                alignment=Qt.AlignmentFlag.AlignTop,
            )

        card_layout = self.content_layout()

        if not isinstance(card_layout, QVBoxLayout):
            raise RuntimeError(
                "SectionCard requires a vertical card layout."
            )

        card_layout.addLayout(header_layout)
        card_layout.addWidget(
            self._create_separator()
        )
        card_layout.addLayout(
            self._content_layout,
            stretch=1,
        )

    def add_widget(
        self,
        widget: QWidget,
        stretch: int = 0,
        alignment: Qt.AlignmentFlag | None = None,
    ) -> None:
        """Add a widget to the section's content area."""

        if alignment is None:
            self._content_layout.addWidget(
                widget,
                stretch,
            )
            return

        self._content_layout.addWidget(
            widget,
            stretch,
            alignment,
        )

    def add_layout(
        self,
        layout: QHBoxLayout | QVBoxLayout,
        stretch: int = 0,
    ) -> None:
        """Add a layout to the section's content area."""

        self._content_layout.addLayout(
            layout,
            stretch,
        )

    def section_layout(self) -> QVBoxLayout:
        """Return the section's content layout."""

        return self._content_layout

    def _create_separator(self) -> QWidget:
        """Create the divider beneath the section header."""

        separator = QWidget()
        separator.setObjectName(
            "sectionCardSeparator"
        )
        separator.setFixedHeight(1)

        return separator