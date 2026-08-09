from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)


class PageHeader(QWidget):
    """Standard title, description, and action area for a page."""

    def __init__(
        self,
        title: str,
        description: str,
        action_widget: QWidget | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self.setObjectName("pageHeader")

        title_label = QLabel(title)
        title_label.setObjectName("pageTitle")

        description_label = QLabel(description)
        description_label.setObjectName(
            "pageDescription"
        )
        description_label.setWordWrap(True)

        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        text_layout.setSpacing(4)
        text_layout.addWidget(title_label)
        text_layout.addWidget(description_label)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        main_layout.setSpacing(20)
        main_layout.addLayout(
            text_layout,
            stretch=1,
        )

        if action_widget is not None:
            main_layout.addWidget(
                action_widget,
                alignment=Qt.AlignmentFlag.AlignTop,
            )