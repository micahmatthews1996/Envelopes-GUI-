from gui.widgets.placeholder_page import PlaceholderPage


class TransactionsPage(PlaceholderPage):
    """Displays and manages financial transactions."""

    def __init__(self) -> None:
        super().__init__(
            title="Transactions",
            description="Record and review income and expenses.",
        )