from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class PlaceholderPage(QWidget):
    """Temporary page used while application features are developed."""

    def __init__(self, title: str, description: str = "") -> None:
        super().__init__()

        self.setObjectName("page")

        title_label = QLabel(title)
        title_label.setObjectName("pageTitle")

        description_label = QLabel(description)
        description_label.setObjectName("pageDescription")
        description_label.setWordWrap(True)

        placeholder_label = QLabel(
            "This section will be implemented in a future step."
        )
        placeholder_label.setObjectName("placeholderMessage")
        placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 32, 40, 32)
        layout.setSpacing(8)

        layout.addWidget(title_label)
        layout.addWidget(description_label)
        layout.addSpacing(24)
        layout.addWidget(placeholder_label, stretch=1)