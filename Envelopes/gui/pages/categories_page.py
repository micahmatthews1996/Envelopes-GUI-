from gui.widgets.placeholder_page import PlaceholderPage


class CategoriesPage(PlaceholderPage):
    """Displays and manages transaction categories."""

    def __init__(self) -> None:
        super().__init__(
            title="Categories",
            description="Create and organize transaction categories.",
        )