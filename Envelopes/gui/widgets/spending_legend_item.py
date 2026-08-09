from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from utils.money import format_currency


class SpendingLegendItem(QFrame):
    """Displays one category within the Dashboard legend."""

    def __init__(
        self,
        category_name: str,
        amount_cents: int,
        percentage: float,
        color: str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self.setObjectName(
            "spendingLegendItem"
        )

        self.setMinimumHeight(64)

        marker = QFrame()
        marker.setObjectName(
            "spendingLegendMarker"
        )
        marker.setFixedSize(
            14,
            14,
        )

        marker.setStyleSheet(
            f"""
            background: {color};
            border-radius: 7px;
            border: none;
            """
        )

        category_label = QLabel(
            category_name
        )
        category_label.setObjectName(
            "listCardPrimaryText"
        )

        amount_label = QLabel(
            format_currency(
                amount_cents
            )
        )
        amount_label.setObjectName(
            "listCardTrailingText"
        )
        amount_label.setAlignment(
            Qt.AlignmentFlag.AlignRight
        )

        percentage_label = QLabel(
            f"{percentage:.1f}%"
        )
        percentage_label.setObjectName(
            "listCardSecondaryText"
        )
        percentage_label.setAlignment(
            Qt.AlignmentFlag.AlignRight
        )

        values_layout = QVBoxLayout()
        values_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        values_layout.setSpacing(2)
        values_layout.addWidget(
            amount_label
        )
        values_layout.addWidget(
            percentage_label
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(
            16,
            12,
            16,
            12,
        )
        layout.setSpacing(14)

        layout.addWidget(marker)
        layout.addWidget(
            category_label,
            stretch=1,
        )
        layout.addLayout(
            values_layout
        )