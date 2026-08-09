from PySide6.QtWidgets import (
    QFrame,
    QLayout,
    QVBoxLayout,
    QWidget,
)


class Card(QFrame):
    """Base card container used throughout Envelopes."""

    def __init__(
        self,
        parent: QWidget | None = None,
        layout: QLayout | None = None,
    ) -> None:
        super().__init__(parent)

        self.setObjectName("card")

        if layout is None:
            layout = QVBoxLayout()

        layout.setContentsMargins(
            20,
            20,
            20,
            20,
        )
        layout.setSpacing(12)

        self.setLayout(layout)

    def content_layout(self) -> QLayout:
        """Return the card's primary layout."""

        layout = self.layout()

        if layout is None:
            raise RuntimeError(
                "The card does not have a layout."
            )

        return layout