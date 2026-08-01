from gui.widgets.placeholder_page import PlaceholderPage


class ReportsPage(PlaceholderPage):
    """Displays and manages budget envelopes."""

    def __init__(self) -> None:
        super().__init__(
            title="Reports",
            description="View your finaincial reports.",
        )