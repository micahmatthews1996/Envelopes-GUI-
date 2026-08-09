from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class EmptyState(QWidget):
    """Displays an empty-state message with an optional action."""

    def __init__(
        self,
        title: str,
        description: str,
        action_text: str = "",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self.setObjectName("emptyStateWidget")

        self._title_label = QLabel(
            title,
            self,
        )
        self._title_label.setObjectName(
            "emptyStateWidgetTitle"
        )
        self._title_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self._description_label = QLabel(
            description,
            self,
        )
        self._description_label.setObjectName(
            "emptyStateWidgetDescription"
        )
        self._description_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        self._description_label.setWordWrap(True)

        self._action_button = QPushButton(
            action_text,
            self,
        )
        self._action_button.setObjectName(
            "primaryButton"
        )
        self._action_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        if not action_text:
            self._action_button.hide()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            32,
            40,
            32,
            40,
        )
        layout.setSpacing(10)
        layout.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        layout.addWidget(
            self._title_label
        )
        layout.addWidget(
            self._description_label
        )
        layout.addSpacing(8)
        layout.addWidget(
            self._action_button,
            alignment=Qt.AlignmentFlag.AlignCenter,
        )

    def action_button(self) -> QPushButton:
        """Return the optional action button."""

        return self._action_button

    def set_title(
        self,
        title: str,
    ) -> None:
        """Update the empty-state title."""

        self._title_label.setText(title)

    def set_description(
        self,
        description: str,
    ) -> None:
        """Update the empty-state description."""

        self._description_label.setText(
            description
        )

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