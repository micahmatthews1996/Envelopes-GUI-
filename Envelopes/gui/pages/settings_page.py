from gui.widgets.placeholder_page import PlaceholderPage


class SettingsPage(PlaceholderPage):
    """Displays application settings."""

    def __init__(self) -> None:
        super().__init__(
            title="Settings",
            description="Application preferences will appear here.",
        )