from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLabel,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)

from gui.widgets.card import Card


class ProgressCard(Card):
    """Displays progress toward a financial goal."""

    def __init__(
        self,
        title: str,
        current_value: str,
        target_value: str,
        progress_percent: int,
        supporting_text: str = "",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self.setObjectName("progressCard")
        self.setMinimumHeight(170)

        self._title_label = QLabel(title)
        self._title_label.setObjectName(
            "progressCardTitle"
        )

        self._value_label = QLabel(
            f"{current_value} / {target_value}"
        )
        self._value_label.setObjectName(
            "progressCardValue"
        )

        self._percent_label = QLabel(
            f"{self._normalize_percent(progress_percent)}%"
        )
        self._percent_label.setObjectName(
            "progressCardPercent"
        )
        self._percent_label.setAlignment(
            Qt.AlignmentFlag.AlignRight
        )

        self._progress_bar = QProgressBar()
        self._progress_bar.setObjectName(
            "goalProgressBar"
        )
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setValue(
            self._normalize_percent(
                progress_percent
            )
        )
        self._progress_bar.setTextVisible(False)
        self._progress_bar.setFixedHeight(10)

        self._supporting_label = QLabel(
            supporting_text
        )
        self._supporting_label.setObjectName(
            "progressCardSupportingText"
        )
        self._supporting_label.setWordWrap(True)
        self._supporting_label.setVisible(
            bool(supporting_text)
        )

        value_row = QVBoxLayout()
        value_row.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        value_row.setSpacing(4)
        value_row.addWidget(
            self._value_label
        )
        value_row.addWidget(
            self._percent_label
        )

        card_layout = self.content_layout()

        if not isinstance(card_layout, QVBoxLayout):
            raise RuntimeError(
                "ProgressCard requires a vertical card layout."
            )

        card_layout.addWidget(
            self._title_label
        )
        card_layout.addLayout(
            value_row
        )
        card_layout.addWidget(
            self._progress_bar
        )
        card_layout.addStretch()
        card_layout.addWidget(
            self._supporting_label
        )

    def set_progress(
        self,
        current_value: str,
        target_value: str,
        progress_percent: int,
    ) -> None:
        """Update the displayed goal progress."""

        normalized_percent = (
            self._normalize_percent(
                progress_percent
            )
        )

        self._value_label.setText(
            f"{current_value} / {target_value}"
        )
        self._percent_label.setText(
            f"{normalized_percent}%"
        )
        self._progress_bar.setValue(
            normalized_percent
        )

    def set_title(
        self,
        title: str,
    ) -> None:
        """Update the goal title."""

        self._title_label.setText(title)

    def set_supporting_text(
        self,
        supporting_text: str,
    ) -> None:
        """Update the supporting message."""

        self._supporting_label.setText(
            supporting_text
        )
        self._supporting_label.setVisible(
            bool(supporting_text)
        )

    def set_completed(
        self,
        completed: bool,
    ) -> None:
        """Update the card's completed visual state."""

        self.setProperty(
            "completed",
            completed,
        )

        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def _normalize_percent(
        self,
        progress_percent: int,
    ) -> int:
        """Clamp a percentage between zero and one hundred."""

        return max(
            0,
            min(
                100,
                int(progress_percent),
            ),
        )