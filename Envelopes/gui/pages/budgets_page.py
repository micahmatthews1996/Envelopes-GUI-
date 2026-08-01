from gui.widgets.placeholder_page import PlaceholderPage


class BudgetsPage(PlaceholderPage):
    """Displays and manages budget envelopes."""

    def __init__(self) -> None:
        super().__init__(
            title="Budgets",
            description="Create envelopes and monitor your spending.",
        )