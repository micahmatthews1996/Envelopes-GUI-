from gui.widgets.placeholder_page import PlaceholderPage

class DashboardPage(PlaceholderPage):
	"""Displays an overview of the user's finances."""

	def __init__(self):
		super().__init__(
			title="Dashboard",
			description="Your financial overview will appear here."
		)