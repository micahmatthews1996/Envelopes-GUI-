from datetime import date

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from gui.widgets.card import Card
from gui.widgets.page_header import PageHeader
from services.reports_service import ReportsService
from utils.money import format_currency


class ReportsPage(QWidget):
    """Displays monthly financial reports."""

    def __init__(
        self,
        reports_service: ReportsService,
    ) -> None:
        super().__init__()

        self._reports_service = reports_service
        self._available_months: list[date] = []

        self.setObjectName("page")

        self._create_interface()
        self.refresh_reports()

    def _create_interface(self) -> None:
        """Create the Reports page interface."""

        self._month_input = QComboBox(self)
        self._month_input.setMinimumWidth(180)
        self._month_input.currentIndexChanged.connect(
            self._month_changed
        )

        month_control = QWidget(self)
        month_layout = QHBoxLayout(month_control)
        month_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        month_layout.setSpacing(8)

        month_label = QLabel(
            "Report month:",
            month_control,
        )
        month_label.setObjectName(
            "listCardSecondaryText"
        )

        month_layout.addWidget(month_label)
        month_layout.addWidget(self._month_input)

        page_header = PageHeader(
            title="Reports",
            description=(
                "Review monthly income, expenses, "
                "category spending, and budget performance."
            ),
            action_widget=month_control,
        )

        self._income_card = self._create_metric_card(
            "Income"
        )
        self._expense_card = self._create_metric_card(
            "Expenses"
        )
        self._cash_flow_card = self._create_metric_card(
            "Net Cash Flow"
        )
        self._transaction_count_card = (
            self._create_metric_card(
                "Transactions"
            )
        )

        metrics_layout = QGridLayout()
        metrics_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        metrics_layout.setHorizontalSpacing(18)
        metrics_layout.setVerticalSpacing(18)
        metrics_layout.addWidget(
            self._income_card,
            0,
            0,
        )
        metrics_layout.addWidget(
            self._expense_card,
            0,
            1,
        )
        metrics_layout.addWidget(
            self._cash_flow_card,
            1,
            0,
        )
        metrics_layout.addWidget(
            self._transaction_count_card,
            1,
            1,
        )

        self._category_card = Card(self)
        self._category_card.setObjectName(
            "reportSectionCard"
        )

        category_layout = self._require_vertical_layout(
            self._category_card
        )

        category_title = QLabel(
            "Spending by Category",
            self._category_card,
        )
        category_title.setObjectName(
            "sectionCardTitle"
        )

        category_subtitle = QLabel(
            "Expense totals for the selected month.",
            self._category_card,
        )
        category_subtitle.setObjectName(
            "sectionCardSubtitle"
        )

        self._category_rows = QWidget(
            self._category_card
        )
        self._category_rows_layout = QVBoxLayout(
            self._category_rows
        )
        self._category_rows_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        self._category_rows_layout.setSpacing(12)

        category_layout.addWidget(category_title)
        category_layout.addWidget(category_subtitle)
        category_layout.addSpacing(6)
        category_layout.addWidget(
            self._category_rows
        )

        self._budget_card = Card(self)
        self._budget_card.setObjectName(
            "reportSectionCard"
        )

        budget_layout = self._require_vertical_layout(
            self._budget_card
        )

        budget_title = QLabel(
            "Budget Performance",
            self._budget_card,
        )
        budget_title.setObjectName(
            "sectionCardTitle"
        )

        budget_subtitle = QLabel(
            "Current performance for active monthly budgets.",
            self._budget_card,
        )
        budget_subtitle.setObjectName(
            "sectionCardSubtitle"
        )

        self._budget_rows = QWidget(
            self._budget_card
        )
        self._budget_rows_layout = QVBoxLayout(
            self._budget_rows
        )
        self._budget_rows_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        self._budget_rows_layout.setSpacing(14)

        budget_layout.addWidget(budget_title)
        budget_layout.addWidget(budget_subtitle)
        budget_layout.addSpacing(6)
        budget_layout.addWidget(
            self._budget_rows
        )

        content = QWidget(self)
        content.setObjectName(
            "reportsContent"
        )

        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(
            40,
            32,
            40,
            32,
        )
        content_layout.setSpacing(24)
        content_layout.addWidget(page_header)
        content_layout.addLayout(metrics_layout)
        content_layout.addWidget(
            self._category_card
        )
        content_layout.addWidget(
            self._budget_card
        )
        content_layout.addStretch()

        scroll_area = QScrollArea(self)
        scroll_area.setObjectName(
            "reportsScrollArea"
        )
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(
            QFrame.Shape.NoFrame
        )
        scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        scroll_area.setWidget(content)

        page_layout = QVBoxLayout(self)
        page_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        page_layout.setSpacing(0)
        page_layout.addWidget(scroll_area)

    def refresh_reports(self) -> None:
        """Reload available months and report data."""

        selected_month = self._selected_month()

        self._available_months = (
            self._reports_service
            .get_available_months()
        )

        self._month_input.blockSignals(True)
        self._month_input.clear()

        for report_month in self._available_months:
            self._month_input.addItem(
                report_month.strftime(
                    "%B %Y"
                ),
                report_month,
            )

        if selected_month is not None:
            selected_index = (
                self._month_input.findData(
                    selected_month
                )
            )

            if selected_index >= 0:
                self._month_input.setCurrentIndex(
                    selected_index
                )

        self._month_input.blockSignals(False)

        self._load_selected_report()

    def _month_changed(self) -> None:
        """Reload the report when the selected month changes."""

        self._load_selected_report()

    def _load_selected_report(self) -> None:
        """Load report values for the selected month."""

        selected_month = self._selected_month()

        if selected_month is None:
            selected_month = date.today()

        summary = (
            self._reports_service
            .get_monthly_summary(
                selected_month
            )
        )

        category_spending = (
            self._reports_service
            .get_category_spending(
                selected_month
            )
        )

        budget_progress = (
            self._reports_service
            .get_budget_performance(
                selected_month
            )
        )

        self._set_metric_value(
            self._income_card,
            format_currency(
                summary.total_income_cents
            ),
        )
        self._set_metric_value(
            self._expense_card,
            format_currency(
                summary.total_expense_cents
            ),
        )
        self._set_metric_value(
            self._cash_flow_card,
            format_currency(
                summary.net_cash_flow_cents
            ),
        )
        self._set_metric_value(
            self._transaction_count_card,
            str(summary.transaction_count),
        )

        cash_flow_value = (
            self._metric_value_label(
                self._cash_flow_card
            )
        )

        if summary.net_cash_flow_cents < 0:
            cash_flow_value.setStyleSheet(
                "color: #D64545;"
            )
        else:
            cash_flow_value.setStyleSheet(
                "color: #219653;"
            )

        self._populate_category_rows(
            category_spending
        )
        self._populate_budget_rows(
            budget_progress
        )

    def _populate_category_rows(
        self,
        items,
    ) -> None:
        """Display category-spending rows."""

        self._clear_layout(
            self._category_rows_layout
        )

        if not items:
            empty_label = QLabel(
                "No expense activity for this month.",
                self._category_rows,
            )
            empty_label.setObjectName(
                "listCardSecondaryText"
            )
            empty_label.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )
            self._category_rows_layout.addWidget(
                empty_label
            )
            return

        maximum_amount = max(
            item.amount_cents
            for item in items
        )

        for item in items:
            row = QWidget(
                self._category_rows
            )
            row_layout = QVBoxLayout(row)
            row_layout.setContentsMargins(
                0,
                0,
                0,
                0,
            )
            row_layout.setSpacing(6)

            heading_layout = QHBoxLayout()
            heading_layout.setContentsMargins(
                0,
                0,
                0,
                0,
            )

            name_label = QLabel(
                item.category_name,
                row,
            )
            name_label.setObjectName(
                "listCardPrimaryText"
            )
            name_label.setStyleSheet(
                f"color: {QColor(item.color).name()};"
            )

            amount_label = QLabel(
                format_currency(
                    item.amount_cents
                ),
                row,
            )
            amount_label.setObjectName(
                "listCardTrailingText"
            )
            amount_label.setAlignment(
                Qt.AlignmentFlag.AlignRight
                | Qt.AlignmentFlag.AlignVCenter
            )

            heading_layout.addWidget(
                name_label,
                stretch=1,
            )
            heading_layout.addWidget(
                amount_label
            )

            progress_bar = QProgressBar(row)
            progress_bar.setRange(
                0,
                100,
            )
            progress_bar.setValue(
                round(
                    item.amount_cents
                    / maximum_amount
                    * 100
                )
                if maximum_amount > 0
                else 0
            )
            progress_bar.setTextVisible(False)
            progress_bar.setFixedHeight(8)

            row_layout.addLayout(
                heading_layout
            )
            row_layout.addWidget(
                progress_bar
            )

            self._category_rows_layout.addWidget(
                row
            )

    def _populate_budget_rows(
        self,
        items,
    ) -> None:
        """Display monthly budget-performance rows."""

        self._clear_layout(
            self._budget_rows_layout
        )

        if not items:
            empty_label = QLabel(
                "No active budgets to report.",
                self._budget_rows,
            )
            empty_label.setObjectName(
                "listCardSecondaryText"
            )
            empty_label.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )
            self._budget_rows_layout.addWidget(
                empty_label
            )
            return

        for item in items:
            row = QWidget(
                self._budget_rows
            )
            row_layout = QVBoxLayout(row)
            row_layout.setContentsMargins(
                0,
                0,
                0,
                0,
            )
            row_layout.setSpacing(6)

            heading_layout = QHBoxLayout()
            heading_layout.setContentsMargins(
                0,
                0,
                0,
                0,
            )

            name_label = QLabel(
                item.category_name,
                row,
            )
            name_label.setObjectName(
                "listCardPrimaryText"
            )
            name_label.setStyleSheet(
                (
                    f"color: "
                    f"{QColor(item.category_color).name()};"
                )
            )

            amount_label = QLabel(
                (
                    f"{format_currency(item.spent_cents)}"
                    " / "
                    f"{format_currency(
                        item.budget.monthly_limit_cents
                    )}"
                ),
                row,
            )
            amount_label.setObjectName(
                "listCardTrailingText"
            )

            heading_layout.addWidget(
                name_label,
                stretch=1,
            )
            heading_layout.addWidget(
                amount_label
            )

            progress_bar = QProgressBar(row)
            progress_bar.setRange(
                0,
                100,
            )
            progress_bar.setValue(
                min(
                    100,
                    item.progress_percent,
                )
            )
            progress_bar.setTextVisible(False)
            progress_bar.setFixedHeight(8)

            if item.is_overspent:
                status_text = (
                    "Overspent by "
                    f"{format_currency(
                        abs(item.remaining_cents)
                    )}"
                )
            else:
                status_text = (
                    f"{format_currency(
                        item.remaining_cents
                    )} remaining"
                )

            status_label = QLabel(
                status_text,
                row,
            )
            status_label.setObjectName(
                (
                    "budgetOverspentText"
                    if item.is_overspent
                    else "listCardSecondaryText"
                )
            )

            row_layout.addLayout(
                heading_layout
            )
            row_layout.addWidget(
                progress_bar
            )
            row_layout.addWidget(
                status_label
            )

            self._budget_rows_layout.addWidget(
                row
            )

    def _create_metric_card(
        self,
        label_text: str,
    ) -> Card:
        """Create a report metric card."""

        card = Card(self)
        card.setObjectName(
            "metricCard"
        )
        card.setMinimumHeight(130)

        layout = self._require_vertical_layout(
            card
        )

        label = QLabel(
            label_text,
            card,
        )
        label.setObjectName(
            "metricCardLabel"
        )

        value = QLabel(
            "$0.00",
            card,
        )
        value.setObjectName(
            "metricCardValue"
        )
        value.setProperty(
            "reportMetricValue",
            True,
        )

        layout.addWidget(label)
        layout.addWidget(value)
        layout.addStretch()

        return card

    def _set_metric_value(
        self,
        card: Card,
        value: str,
    ) -> None:
        """Set the value displayed by a metric card."""

        self._metric_value_label(
            card
        ).setText(value)

    def _metric_value_label(
        self,
        card: Card,
    ) -> QLabel:
        """Return a metric card's value label."""

        label = card.findChild(
            QLabel,
            options=Qt.FindChildOption.FindDirectChildrenOnly,
        )

        labels = card.findChildren(
            QLabel,
            options=Qt.FindChildOption.FindDirectChildrenOnly,
        )

        for candidate in labels:
            if candidate.property(
                "reportMetricValue"
            ):
                return candidate

        if label is None:
            raise RuntimeError(
                "Report metric card has no value label."
            )

        return label

    def _selected_month(self) -> date | None:
        """Return the currently selected report month."""

        selected_data = self._month_input.currentData()

        if isinstance(
            selected_data,
            date,
        ):
            return selected_data

        return None

    def _require_vertical_layout(
        self,
        card: Card,
    ) -> QVBoxLayout:
        """Return a card's vertical content layout."""

        layout = card.content_layout()

        if not isinstance(
            layout,
            QVBoxLayout,
        ):
            raise RuntimeError(
                "Report cards require a vertical layout."
            )

        return layout

    def _clear_layout(
        self,
        layout: QVBoxLayout,
    ) -> None:
        """Remove all widgets from a report section."""

        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()

            if widget is not None:
                widget.deleteLater()