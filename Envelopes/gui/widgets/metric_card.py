from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLabel,
    QVBoxLayout,
    QWidget,
)

from gui.widgets.card import Card


class MetricCard(Card):
    """Displays a primary financial metric and optional supporting text."""

    def __init__(
        self,
        label: str,
        value: str,
        supporting_text: str = "",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self.setObjectName("metricCard")
        self.setMinimumHeight(130)

        self._label = QLabel(label, self)
        self._label.setObjectName(
            "metricCardLabel"
        )

        self._value = QLabel(value, self)
        self._value.setObjectName(
            "metricCardValue"
        )
        self._value.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )

        self._supporting_text = QLabel(
            supporting_text,
            self,
        )
        self._supporting_text.setObjectName(
            "metricCardSupportingText"
        )
        self._supporting_text.setWordWrap(True)

        if not supporting_text:
            self._supporting_text.hide()

        card_layout = self.content_layout()

        if not isinstance(
            card_layout,
            QVBoxLayout,
        ):
            raise RuntimeError(
                "MetricCard requires a vertical card layout."
            )

        card_layout.addWidget(
            self._label
        )
        card_layout.addWidget(
            self._value
        )
        card_layout.addStretch()
        card_layout.addWidget(
            self._supporting_text
        )

    def set_value(
        self,
        value: str,
    ) -> None:
        """Update the displayed metric value."""

        self._value.setText(value)

    def set_supporting_text(
        self,
        supporting_text: str,
    ) -> None:
        """Update the supporting message."""

        self._supporting_text.setText(
            supporting_text
        )

        if supporting_text:
            self._supporting_text.show()
        else:
            self._supporting_text.hide()

    def set_label(
        self,
        label: str,
    ) -> None:
        """Update the displayed metric label."""

        self._label.setText(label)