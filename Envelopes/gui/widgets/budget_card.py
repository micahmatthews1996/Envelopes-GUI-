from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from gui.widgets.card import Card
from utils.money import format_currency


class BudgetCard(Card):
    """Displays one monthly category budget."""

    edit_requested = Signal()

    def __init__(
        self,
        category_name: str,
        category_color: str,
        spent_cents: int,
        monthly_limit_cents: int,
        remaining_cents: int,
        progress_percent: int,
        is_overspent: bool,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self.setObjectName("budgetCard")
        self.setMinimumHeight(170)

        display_percent = max(
            0,
            progress_percent,
        )

        progress_bar_value = min(
            100,
            display_percent,
        )

        category_label = QLabel(
            category_name,
            self,
        )
        category_label.setObjectName(
            "progressCardTitle"
        )
        category_label.setStyleSheet(
            f"color: {QColor(category_color).name()};"
        )

        edit_button = QPushButton(
            "Edit",
            self,
        )
        edit_button.setObjectName(
            "secondaryButton"
        )
        edit_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        edit_button.clicked.connect(
            self.edit_requested.emit
        )

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        header_layout.setSpacing(12)
        header_layout.addWidget(
            category_label,
            stretch=1,
        )
        header_layout.addWidget(
            edit_button,
            alignment=Qt.AlignmentFlag.AlignTop,
        )

        amount_label = QLabel(
            (
                f"{format_currency(spent_cents)}"
                " / "
                f"{format_currency(monthly_limit_cents)}"
            ),
            self,
        )
        amount_label.setObjectName(
            "progressCardValue"
        )

        percent_label = QLabel(
            f"{display_percent}%",
            self,
        )
        percent_label.setObjectName(
            "progressCardPercent"
        )
        percent_label.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignVCenter
        )

        amount_layout = QHBoxLayout()
        amount_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        amount_layout.setSpacing(12)
        amount_layout.addWidget(
            amount_label,
            stretch=1,
        )
        amount_layout.addWidget(
            percent_label
        )

        progress_bar = QProgressBar(self)
        progress_bar.setObjectName(
            "budgetProgressBar"
        )
        progress_bar.setRange(
            0,
            100,
        )
        progress_bar.setValue(
            progress_bar_value
        )
        progress_bar.setTextVisible(False)
        progress_bar.setFixedHeight(10)

        if is_overspent:
            status_text = (
                "Overspent by "
                f"{format_currency(abs(remaining_cents))}"
            )
            status_object_name = (
                "budgetOverspentText"
            )
            self.setProperty(
                "overspent",
                True,
            )
        else:
            status_text = (
                f"{format_currency(remaining_cents)} "
                "remaining"
            )
            status_object_name = (
                "progressCardSupportingText"
            )
            self.setProperty(
                "overspent",
                False,
            )

        status_label = QLabel(
            status_text,
            self,
        )
        status_label.setObjectName(
            status_object_name
        )

        card_layout = self.content_layout()

        if not isinstance(
            card_layout,
            QVBoxLayout,
        ):
            raise RuntimeError(
                "Budget cards require a vertical layout."
            )

        card_layout.setContentsMargins(
            20,
            18,
            20,
            18,
        )
        card_layout.setSpacing(10)

        card_layout.addLayout(
            header_layout
        )
        card_layout.addLayout(
            amount_layout
        )
        card_layout.addWidget(
            progress_bar
        )
        card_layout.addWidget(
            status_label
        )

        self.style().unpolish(self)
        self.style().polish(self)