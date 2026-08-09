from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from gui.widgets.dashboard_section import DashboardSection
from gui.widgets.donut_chart_widget import DonutChartWidget
from gui.widgets.metric_card import MetricCard
from gui.widgets.page_header import PageHeader
from gui.widgets.savings_goal_card import SavingsGoalCard
from gui.widgets.spending_legend_item import SpendingLegendItem
from models.dashboard_summary import (
    DashboardAccountItem,
    DashboardCategorySpendingItem,
    DashboardSavingsGoalItem,
    DashboardTransactionItem,
)
from models.donut_chart_segment import DonutChartSegment
from services.dashboard_service import DashboardService
from utils.money import format_currency


MAX_DASHBOARD_ACCOUNTS = 4
MAX_DASHBOARD_TRANSACTIONS = 5


class DashboardPage(QWidget):
    """Displays the application's financial dashboard."""

    def __init__(
        self,
        dashboard_service: DashboardService,
    ) -> None:
        super().__init__()

        self._dashboard_service = dashboard_service

        self.setObjectName("page")

        self._create_interface()
        self.refresh_dashboard()

    def _create_interface(self) -> None:
        """Create the Dashboard interface."""

        page_header = PageHeader(
            title="Dashboard",
            description=(
                "See your balances, monthly activity, "
                "and financial progress at a glance."
            ),
        )

        self._net_worth_card = MetricCard(
            label="Net Worth",
            value="$0.00",
            supporting_text=(
                "Combined current balance across all accounts"
            ),
        )
        self._net_worth_card.setObjectName(
            "featuredMetricCard"
        )
        self._net_worth_card.setMinimumHeight(170)

        self._income_card = MetricCard(
            label="Total Income",
            value="$0.00",
            supporting_text=(
                "Income recorded across all transactions"
            ),
        )

        self._expense_card = MetricCard(
            label="Total Expenses",
            value="$0.00",
            supporting_text=(
                "Spending recorded across all transactions"
            ),
        )

        self._savings_card = MetricCard(
            label="Savings Balance",
            value="$0.00",
            supporting_text=(
                "Current balance of your Savings account"
            ),
        )

        supporting_metrics_layout = QGridLayout()
        supporting_metrics_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        supporting_metrics_layout.setHorizontalSpacing(18)
        supporting_metrics_layout.setVerticalSpacing(18)
        supporting_metrics_layout.setColumnStretch(0, 1)
        supporting_metrics_layout.setColumnStretch(1, 1)
        supporting_metrics_layout.setColumnStretch(2, 1)

        supporting_metrics_layout.addWidget(
            self._income_card,
            0,
            0,
        )
        supporting_metrics_layout.addWidget(
            self._expense_card,
            0,
            1,
        )
        supporting_metrics_layout.addWidget(
            self._savings_card,
            0,
            2,
        )

        self._recent_transactions_section = DashboardSection(
            title="Recent Transactions",
            subtitle=(
                "Your five most recent income "
                "and expense transactions."
            ),
        )
        self._recent_transactions_section.setMinimumHeight(
            470
        )

        self._transactions_container = QWidget()
        self._transactions_container.setObjectName(
            "dashboardTransactionsContainer"
        )

        self._transactions_layout = QVBoxLayout(
            self._transactions_container
        )
        self._transactions_layout.setContentsMargins(
            0,
            10,
            0,
            0,
        )
        self._transactions_layout.setSpacing(10)
        self._transactions_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop
        )

        self._recent_transactions_section.add_widget(
            self._transactions_container,
            stretch=1,
        )

        self._accounts_section = DashboardSection(
            title="Accounts",
            subtitle=(
                "Current balances across your "
                "financial accounts."
            ),
        )
        self._accounts_section.setMinimumHeight(470)

        self._accounts_container = QWidget()
        self._accounts_container.setObjectName(
            "dashboardAccountsContainer"
        )

        self._accounts_layout = QVBoxLayout(
            self._accounts_container
        )
        self._accounts_layout.setContentsMargins(
            0,
            10,
            0,
            0,
        )
        self._accounts_layout.setSpacing(10)
        self._accounts_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop
        )

        self._accounts_section.add_widget(
            self._accounts_container,
            stretch=1,
        )

        snapshot_layout = QGridLayout()
        snapshot_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        snapshot_layout.setHorizontalSpacing(18)
        snapshot_layout.setVerticalSpacing(18)
        snapshot_layout.setColumnStretch(0, 1)
        snapshot_layout.setColumnStretch(1, 1)

        snapshot_layout.addWidget(
            self._recent_transactions_section,
            0,
            0,
        )
        snapshot_layout.addWidget(
            self._accounts_section,
            0,
            1,
        )

        self._spending_section = DashboardSection(
            title="Spending by Category",
            subtitle=(
                "Your expense breakdown for the current month."
            ),
        )
        self._spending_section.setMinimumHeight(
            440
        )

        self._spending_chart = DonutChartWidget()
        self._spending_chart.setMinimumSize(
            280,
            280,
        )

        self._spending_legend_container = QWidget()
        self._spending_legend_container.setObjectName(
            "dashboardSpendingLegend"
        )

        self._spending_legend_layout = QVBoxLayout(
            self._spending_legend_container
        )
        self._spending_legend_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        self._spending_legend_layout.setSpacing(8)
        self._spending_legend_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop
        )

        spending_content_layout = QHBoxLayout()
        spending_content_layout.setContentsMargins(
            0,
            12,
            0,
            0,
        )
        spending_content_layout.setSpacing(24)
        spending_content_layout.addWidget(
            self._spending_chart,
            stretch=1,
        )
        spending_content_layout.addWidget(
            self._spending_legend_container,
            stretch=1,
        )

        self._spending_section.add_layout(
            spending_content_layout
        )

        self._savings_goals_section = DashboardSection(
            title="Savings Goals",
            subtitle=(
                "Track your progress toward your "
                "financial goals."
            ),
        )
        self._savings_goals_section.setMinimumHeight(
            420
        )

        self._savings_goals_container = QWidget()
        self._savings_goals_container.setObjectName(
            "dashboardSavingsGoalsContainer"
        )

        self._savings_goals_layout = QVBoxLayout(
            self._savings_goals_container
        )
        self._savings_goals_layout.setContentsMargins(
            0,
            10,
            0,
            0,
        )
        self._savings_goals_layout.setSpacing(12)
        self._savings_goals_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop
        )

        self._savings_goals_section.add_widget(
            self._savings_goals_container,
            stretch=1,
        )

        dashboard_content = QWidget()
        dashboard_content.setObjectName(
            "dashboardContent"
        )

        content_layout = QVBoxLayout(
            dashboard_content
        )
        content_layout.setContentsMargins(
            40,
            32,
            40,
            32,
        )
        content_layout.setSpacing(20)

        content_layout.addWidget(page_header)
        content_layout.addWidget(
            self._net_worth_card
        )
        content_layout.addLayout(
            supporting_metrics_layout
        )
        content_layout.addLayout(
            snapshot_layout
        )
        content_layout.addWidget(
            self._spending_section
        )
        content_layout.addWidget(
            self._savings_goals_section
        )
        content_layout.addStretch()

        scroll_area = QScrollArea()
        scroll_area.setObjectName(
            "dashboardScrollArea"
        )
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(
            QFrame.Shape.NoFrame
        )
        scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        scroll_area.setWidget(
            dashboard_content
        )

        page_layout = QVBoxLayout(self)
        page_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        page_layout.setSpacing(0)
        page_layout.addWidget(
            scroll_area
        )

    def refresh_dashboard(self) -> None:
        """Refresh all Dashboard information."""

        summary = (
            self._dashboard_service
            .get_dashboard_summary()
        )

        self._net_worth_card.set_value(
            format_currency(
                summary.net_worth_cents
            )
        )

        self._income_card.set_value(
            format_currency(
                summary.total_income_cents
            )
        )

        self._expense_card.set_value(
            format_currency(
                summary.total_expense_cents
            )
        )

        self._savings_card.set_value(
            format_currency(
                summary.total_savings_cents
            )
        )

        self._refresh_recent_transactions(
            summary.recent_transactions
        )

        self._refresh_accounts(
            summary.accounts
        )

        self._refresh_spending(
            summary.category_spending
        )

        self._refresh_savings_goals(
            summary.savings_goals
        )

    def _refresh_recent_transactions(
        self,
        transactions: list[
            DashboardTransactionItem
        ],
    ) -> None:
        """Refresh the recent-transaction snapshot."""

        self._clear_layout(
            self._transactions_layout
        )

        if not transactions:
            self._show_transactions_empty_state()
            return

        visible_transactions = transactions[
            :MAX_DASHBOARD_TRANSACTIONS
        ]

        for transaction in visible_transactions:
            transaction_row = (
                self._create_transaction_row(
                    transaction
                )
            )

            self._transactions_layout.addWidget(
                transaction_row
            )

    def _create_transaction_row(
        self,
        transaction: DashboardTransactionItem,
    ) -> QFrame:
        """Create one recent-transaction row."""

        row = QFrame()
        row.setObjectName(
            "dashboardAccountRow"
        )
        row.setMinimumHeight(72)

        payee_label = QLabel(
            transaction.payee
        )
        payee_label.setObjectName(
            "listCardPrimaryText"
        )

        date_text = (
            f"{transaction.transaction_date.strftime('%b')} "
            f"{transaction.transaction_date.day}, "
            f"{transaction.transaction_date.year}"
        )

        details_label = QLabel(
            (
                f"{transaction.category_name}"
                f"  •  {date_text}"
            )
        )
        details_label.setObjectName(
            "listCardSecondaryText"
        )

        amount_label = QLabel(
            format_currency(
                transaction.amount_cents
            )
        )
        amount_label.setObjectName(
            "listCardTrailingText"
        )
        amount_label.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignVCenter
        )

        if transaction.amount_cents < 0:
            amount_label.setStyleSheet(
                "color: #D64545;"
            )
        else:
            amount_label.setStyleSheet(
                "color: #219653;"
            )

        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        text_layout.setSpacing(4)
        text_layout.addWidget(
            payee_label
        )
        text_layout.addWidget(
            details_label
        )

        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(
            16,
            12,
            16,
            12,
        )
        row_layout.setSpacing(14)
        row_layout.addLayout(
            text_layout,
            stretch=1,
        )
        row_layout.addWidget(
            amount_label
        )

        return row

    def _show_transactions_empty_state(
        self,
    ) -> None:
        """Display a message when no transactions exist."""

        empty_container = QWidget()
        empty_container.setObjectName(
            "listCardEmptyState"
        )

        title_label = QLabel(
            "No transactions yet"
        )
        title_label.setObjectName(
            "listCardEmptyTitle"
        )
        title_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        description_label = QLabel(
            (
                "Add an income or expense transaction "
                "to see recent activity here."
            )
        )
        description_label.setObjectName(
            "listCardEmptyDescription"
        )
        description_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        description_label.setWordWrap(True)

        empty_layout = QVBoxLayout(
            empty_container
        )
        empty_layout.setContentsMargins(
            24,
            40,
            24,
            40,
        )
        empty_layout.setSpacing(8)
        empty_layout.addWidget(
            title_label
        )
        empty_layout.addWidget(
            description_label
        )

        self._transactions_layout.addWidget(
            empty_container
        )

    def _refresh_accounts(
        self,
        accounts: list[
            DashboardAccountItem
        ],
    ) -> None:
        """Refresh the Dashboard account snapshot."""

        self._clear_layout(
            self._accounts_layout
        )

        if not accounts:
            self._show_accounts_empty_state()
            return

        visible_accounts = accounts[
            :MAX_DASHBOARD_ACCOUNTS
        ]

        for account in visible_accounts:
            account_row = self._create_account_row(
                account
            )

            self._accounts_layout.addWidget(
                account_row
            )

        hidden_account_count = (
            len(accounts)
            - len(visible_accounts)
        )

        if hidden_account_count > 0:
            additional_label = QLabel(
                (
                    f"{hidden_account_count} more "
                    f"account"
                    f"{'s' if hidden_account_count != 1 else ''}"
                )
            )
            additional_label.setObjectName(
                "listCardSecondaryText"
            )
            additional_label.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

            self._accounts_layout.addWidget(
                additional_label
            )

    def _create_account_row(
        self,
        account: DashboardAccountItem,
    ) -> QFrame:
        """Create one account snapshot row."""

        row = QFrame()
        row.setObjectName(
            "dashboardAccountRow"
        )
        row.setMinimumHeight(72)

        account_name_label = QLabel(
            account.account_name
        )
        account_name_label.setObjectName(
            "listCardPrimaryText"
        )

        balance_caption = QLabel(
            "Current balance"
        )
        balance_caption.setObjectName(
            "listCardSecondaryText"
        )

        balance_label = QLabel(
            format_currency(
                account.current_balance_cents
            )
        )
        balance_label.setObjectName(
            "listCardTrailingText"
        )
        balance_label.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignVCenter
        )

        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        text_layout.setSpacing(4)
        text_layout.addWidget(
            account_name_label
        )
        text_layout.addWidget(
            balance_caption
        )

        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(
            16,
            12,
            16,
            12,
        )
        row_layout.setSpacing(14)
        row_layout.addLayout(
            text_layout,
            stretch=1,
        )
        row_layout.addWidget(
            balance_label
        )

        return row

    def _show_accounts_empty_state(
        self,
    ) -> None:
        """Display a message when no accounts exist."""

        empty_container = QWidget()
        empty_container.setObjectName(
            "listCardEmptyState"
        )

        title_label = QLabel(
            "No accounts yet"
        )
        title_label.setObjectName(
            "listCardEmptyTitle"
        )
        title_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        description_label = QLabel(
            (
                "Create an account to begin tracking "
                "balances on your Dashboard."
            )
        )
        description_label.setObjectName(
            "listCardEmptyDescription"
        )
        description_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        description_label.setWordWrap(True)

        empty_layout = QVBoxLayout(
            empty_container
        )
        empty_layout.setContentsMargins(
            24,
            40,
            24,
            40,
        )
        empty_layout.setSpacing(8)
        empty_layout.addWidget(
            title_label
        )
        empty_layout.addWidget(
            description_label
        )

        self._accounts_layout.addWidget(
            empty_container
        )

    def _refresh_spending(
        self,
        spending_items: list[
            DashboardCategorySpendingItem
        ],
    ) -> None:
        """Refresh the monthly spending chart and legend."""

        self._clear_layout(
            self._spending_legend_layout
        )

        total_spending_cents = sum(
            item.amount_cents
            for item in spending_items
        )

        segments = [
            DonutChartSegment(
                value=item.amount_cents,
                color=item.color,
            )
            for item in spending_items
        ]

        self._spending_chart.set_segments(
            segments
        )

        self._spending_chart.set_center_text(
            value=format_currency(
                total_spending_cents
            ),
            caption="Spent this month",
        )

        if not spending_items:
            self._show_spending_empty_state()
            return

        for item in spending_items:
            percentage = 0.0

            if total_spending_cents > 0:
                percentage = (
                    item.amount_cents
                    / total_spending_cents
                    * 100
                )

            legend_item = SpendingLegendItem(
                category_name=item.category_name,
                amount_cents=item.amount_cents,
                percentage=percentage,
                color=item.color,
            )

            self._spending_legend_layout.addWidget(
                legend_item
            )

    def _show_spending_empty_state(
        self,
    ) -> None:
        """Display a message when the month has no expenses."""

        empty_container = QWidget()
        empty_container.setObjectName(
            "listCardEmptyState"
        )

        title_label = QLabel(
            "No spending this month"
        )
        title_label.setObjectName(
            "listCardEmptyTitle"
        )
        title_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        description_label = QLabel(
            (
                "Expense transactions recorded this month "
                "will appear in this chart."
            )
        )
        description_label.setObjectName(
            "listCardEmptyDescription"
        )
        description_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        description_label.setWordWrap(True)

        empty_layout = QVBoxLayout(
            empty_container
        )
        empty_layout.setContentsMargins(
            24,
            34,
            24,
            34,
        )
        empty_layout.setSpacing(8)
        empty_layout.addWidget(
            title_label
        )
        empty_layout.addWidget(
            description_label
        )

        self._spending_legend_layout.addWidget(
            empty_container
        )

    def _refresh_savings_goals(
        self,
        goals: list[
            DashboardSavingsGoalItem
        ],
    ) -> None:
        """Refresh the savings-goal snapshot."""

        self._clear_layout(
            self._savings_goals_layout
        )

        if not goals:
            self._show_savings_goals_empty_state()
            return

        for goal in goals:
            goal_card = SavingsGoalCard(
                goal_name=goal.name,
                current_amount_cents=(
                    goal.current_amount_cents
                ),
                target_amount_cents=(
                    goal.target_amount_cents
                ),
                progress_percent=(
                    goal.progress_percent
                ),
            )

            self._savings_goals_layout.addWidget(
                goal_card
            )

    def _show_savings_goals_empty_state(
        self,
    ) -> None:
        """Display a message when no savings goals exist."""

        empty_container = QWidget()
        empty_container.setObjectName(
            "listCardEmptyState"
        )

        title_label = QLabel(
            "No savings goals yet"
        )
        title_label.setObjectName(
            "listCardEmptyTitle"
        )
        title_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        description_label = QLabel(
            (
                "Create a savings goal to track progress "
                "toward an emergency fund, vacation, "
                "major purchase, or another priority."
            )
        )
        description_label.setObjectName(
            "listCardEmptyDescription"
        )
        description_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        description_label.setWordWrap(True)

        empty_layout = QVBoxLayout(
            empty_container
        )
        empty_layout.setContentsMargins(
            24,
            46,
            24,
            46,
        )
        empty_layout.setSpacing(8)
        empty_layout.addWidget(
            title_label
        )
        empty_layout.addWidget(
            description_label
        )

        self._savings_goals_layout.addWidget(
            empty_container
        )

    def _clear_layout(
        self,
        layout: QVBoxLayout,
    ) -> None:
        """Remove every widget from a Dashboard list."""

        while layout.count():
            layout_item = layout.takeAt(0)
            widget = layout_item.widget()

            if widget is not None:
                widget.deleteLater()