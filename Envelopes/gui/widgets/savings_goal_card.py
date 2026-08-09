from PySide6.QtCore import Qt, Signal
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


class SavingsGoalCard(Card):
    """Displays one savings goal."""

    edit_requested = Signal()
    move_money_requested = Signal()
    fund_goal_requested = Signal()

    def __init__(
        self,
        goal_name: str,
        current_amount_cents: int,
        target_amount_cents: int,
        progress_percent: int,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self.setObjectName("progressCard")
        self.setMinimumHeight(160)

        normalized_percent = max(
            0,
            min(
                100,
                progress_percent,
            ),
        )

        title_label = QLabel(
            goal_name,
            self,
        )
        title_label.setObjectName(
            "progressCardTitle"
        )

        fund_goal_button = QPushButton(
            "Fund Goal",
            self,
        )
        fund_goal_button.setObjectName(
            "primaryButton"
        )
        fund_goal_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        fund_goal_button.setEnabled(
            current_amount_cents < target_amount_cents
        )
        fund_goal_button.clicked.connect(
            self.fund_goal_requested.emit
        )

        move_money_button = QPushButton(
            "Move Money",
            self,
        )
        move_money_button.setObjectName(
            "secondaryButton"
        )
        move_money_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        move_money_button.setEnabled(
            current_amount_cents > 0
        )
        move_money_button.clicked.connect(
            self.move_money_requested.emit
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
        header_layout.setSpacing(8)
        header_layout.addWidget(
            title_label,
            stretch=1,
        )
        header_layout.addWidget(
            fund_goal_button,
            alignment=Qt.AlignmentFlag.AlignTop,
        )
        header_layout.addWidget(
            move_money_button,
            alignment=Qt.AlignmentFlag.AlignTop,
        )
        header_layout.addWidget(
            edit_button,
            alignment=Qt.AlignmentFlag.AlignTop,
        )

        amount_label = QLabel(
            (
                f"{format_currency(current_amount_cents)}"
                " / "
                f"{format_currency(target_amount_cents)}"
            ),
            self,
        )
        amount_label.setObjectName(
            "progressCardValue"
        )

        percent_label = QLabel(
            f"{normalized_percent}%",
            self,
        )
        percent_label.setObjectName(
            "progressCardPercent"
        )
        percent_label.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignVCenter
        )

        value_layout = QHBoxLayout()
        value_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        value_layout.setSpacing(12)
        value_layout.addWidget(
            amount_label,
            stretch=1,
        )
        value_layout.addWidget(
            percent_label
        )

        progress_bar = QProgressBar(self)
        progress_bar.setObjectName(
            "goalProgressBar"
        )
        progress_bar.setRange(
            0,
            100,
        )
        progress_bar.setValue(
            normalized_percent
        )
        progress_bar.setTextVisible(False)
        progress_bar.setFixedHeight(10)

        remaining_amount_cents = max(
            0,
            (
                target_amount_cents
                - current_amount_cents
            ),
        )

        if normalized_percent >= 100:
            supporting_text = "Goal complete!"
            self.setProperty(
                "completed",
                True,
            )
        else:
            supporting_text = (
                f"{format_currency(remaining_amount_cents)} "
                "remaining"
            )
            self.setProperty(
                "completed",
                False,
            )

        supporting_label = QLabel(
            supporting_text,
            self,
        )
        supporting_label.setObjectName(
            "progressCardSupportingText"
        )

        card_layout = self.content_layout()

        if not isinstance(
            card_layout,
            QVBoxLayout,
        ):
            raise RuntimeError(
                "Savings goal cards require "
                "a vertical layout."
            )

        card_layout.setContentsMargins(
            20,
            18,
            20,
            18,
        )
        card_layout.setSpacing(10)
        card_layout.addLayout(header_layout)
        card_layout.addLayout(value_layout)
        card_layout.addWidget(progress_bar)
        card_layout.addWidget(supporting_label)

        self.style().unpolish(self)
        self.style().polish(self)