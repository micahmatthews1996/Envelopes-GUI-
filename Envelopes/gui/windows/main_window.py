from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QButtonGroup,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from core.application_container import ApplicationContainer
from gui.pages.accounts_page import AccountsPage
from gui.pages.budgets_page import BudgetsPage
from gui.pages.categories_page import CategoriesPage
from gui.pages.dashboard_page import DashboardPage
from gui.pages.reports_page import ReportsPage
from gui.pages.savings_goals_page import SavingsGoalsPage
from gui.pages.transactions_page import TransactionsPage


PAGE_DASHBOARD = "dashboard"
PAGE_ACCOUNTS = "accounts"
PAGE_TRANSACTIONS = "transactions"
PAGE_SAVINGS_GOALS = "savings_goals"
PAGE_BUDGETS = "budgets"
PAGE_REPORTS = "reports"
PAGE_CATEGORIES = "categories"


class MainWindow(QMainWindow):
    """The main window for the Envelopes desktop application."""

    def __init__(
        self,
        container: ApplicationContainer,
    ) -> None:
        super().__init__()

        self._container = container

        self.setWindowTitle("Envelopes")
        self.setWindowIcon(
            QIcon("assets/icons/envelopes.png")
        )
        self.resize(1100, 700)
        self.setMinimumSize(900, 600)

        self.page_stack = QStackedWidget()

        self.navigation_group = QButtonGroup(self)
        self.navigation_group.setExclusive(True)

        self.pages: dict[str, QWidget] = {}
        self.page_indexes: dict[str, int] = {}

        self._create_pages()
        self._create_interface()
        self._create_status_bar()

        self._show_page(PAGE_DASHBOARD)

    def _create_pages(self) -> None:
        """Create and register all application pages."""

        self.pages = {
            PAGE_DASHBOARD: DashboardPage(
                dashboard_service=(
                    self._container.dashboard_service
                ),
            ),
            PAGE_ACCOUNTS: AccountsPage(
                account_service=(
                    self._container.account_service
                ),
                balance_service=(
                    self._container.balance_service
                ),
            ),
            PAGE_TRANSACTIONS: TransactionsPage(
                transaction_service=(
                    self._container.transaction_service
                ),
                account_service=(
                    self._container.account_service
                ),
                category_service=(
                    self._container.category_service
                ),
                savings_goal_service=(
                    self._container.savings_goal_service
                ),
                savings_goal_allocation_service=(
                    self._container
                    .savings_goal_allocation_service
                ),
            ),
            PAGE_SAVINGS_GOALS: SavingsGoalsPage(
                savings_goal_service=(
                    self._container.savings_goal_service
                ),
                savings_goal_allocation_service=(
                    self._container
                    .savings_goal_allocation_service
                ),
            ),
            PAGE_BUDGETS: BudgetsPage(
                budget_service=(
                    self._container.budget_service
                ),
                category_service=(
                    self._container.category_service
                ),
                account_service=(
                    self._container.account_service
                ),
                transaction_service=(
                    self._container.transaction_service
                ),
                savings_goal_service=(
                    self._container.savings_goal_service
                ),
                savings_goal_allocation_service=(
                    self._container.savings_goal_allocation_service
                ),
                budget_rollover_service=(
                    self._container.budget_rollover_service
                ),
            ),
            PAGE_REPORTS: ReportsPage(
                reports_service=(
                    self._container.reports_service
                ),
            ),
            PAGE_CATEGORIES: CategoriesPage(
                self._container.category_service
            ),
        }

        for page_name, page_widget in self.pages.items():
            page_index = self.page_stack.addWidget(
                page_widget
            )
            self.page_indexes[page_name] = page_index

    def _create_interface(self) -> None:
        """Create the main application layout."""

        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        sidebar = self._create_sidebar()

        main_layout.addWidget(sidebar)
        main_layout.addWidget(
            self.page_stack,
            stretch=1,
        )

        self.setCentralWidget(central_widget)

    def _create_sidebar(self) -> QWidget:
        """Create the navigation sidebar."""

        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(
            16,
            24,
            16,
            24,
        )
        sidebar_layout.setSpacing(8)

        application_title = QLabel("Envelopes")
        application_title.setObjectName(
            "applicationTitle"
        )
        application_title.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        application_subtitle = QLabel(
            "Personal Finance"
        )
        application_subtitle.setObjectName(
            "applicationSubtitle"
        )
        application_subtitle.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        sidebar_layout.addWidget(
            application_title
        )
        sidebar_layout.addWidget(
            application_subtitle
        )
        sidebar_layout.addSpacing(24)

        navigation_items = [
            ("Dashboard", PAGE_DASHBOARD),
            ("Accounts", PAGE_ACCOUNTS),
            ("Transactions", PAGE_TRANSACTIONS),
            ("Savings Goals", PAGE_SAVINGS_GOALS),
            ("Budgets", PAGE_BUDGETS),
            ("Reports", PAGE_REPORTS),
            ("Categories", PAGE_CATEGORIES),
        ]

        for button_text, page_name in navigation_items:
            button = self._create_navigation_button(
                text=button_text,
                page_name=page_name,
            )

            sidebar_layout.addWidget(button)

        sidebar_layout.addStretch()

        version_label = QLabel("Version 0.1.0")
        version_label.setObjectName("versionLabel")
        version_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        sidebar_layout.addWidget(version_label)

        return sidebar

    def _create_navigation_button(
        self,
        text: str,
        page_name: str,
    ) -> QPushButton:
        """Create a sidebar navigation button."""

        button = QPushButton(text)
        button.setObjectName("navigationButton")
        button.setCheckable(True)
        button.setMinimumHeight(44)

        button.clicked.connect(
            lambda checked=False, name=page_name: (
                self._show_page(name)
            )
        )

        button.setProperty(
            "page_name",
            page_name,
        )

        self.navigation_group.addButton(button)

        return button

    def _show_page(self, page_name: str) -> None:
        """Refresh and display the selected page."""

        page_index = self.page_indexes.get(
            page_name
        )

        if page_index is None:
            self.statusBar().showMessage(
                f"Unable to open page: {page_name}",
                3000,
            )
            return

        selected_page = self.pages[page_name]

        self._refresh_page(selected_page)

        self.page_stack.setCurrentIndex(
            page_index
        )

        for button in self.navigation_group.buttons():
            button_page_name = button.property(
                "page_name"
            )
            button.setChecked(
                button_page_name == page_name
            )

        display_name = page_name.replace(
            "_",
            " ",
        ).title()

        self.statusBar().showMessage(
            f"{display_name} page",
            2000,
        )

    def _refresh_page(
        self,
        page: QWidget,
    ) -> None:
        """Refresh a page when it provides a refresh method."""

        refresh_method_names = [
            "refresh_dashboard",
            "refresh_accounts",
            "refresh_transactions",
            "refresh_budgets",
            "refresh_reports",
            "refresh_categories",
            "refresh",
        ]

        for method_name in refresh_method_names:
            refresh_method = getattr(
                page,
                method_name,
                None,
            )

            if callable(refresh_method):
                refresh_method()
                return

    def _create_status_bar(self) -> None:
        """Create the main application status bar."""

        status_bar = QStatusBar()
        status_bar.setObjectName("statusBar")
        status_bar.showMessage("Ready")

        self.setStatusBar(status_bar)