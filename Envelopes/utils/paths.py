from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

ASSETS_DIRECTORY = PROJECT_ROOT / "assets"
DATA_DIRECTORY = PROJECT_ROOT / "data"
GUI_DIRECTORY = PROJECT_ROOT / "gui"
STYLES_DIRECTORY = GUI_DIRECTORY / "styles"

STYLE_FILE = STYLES_DIRECTORY / "style.qss"

ACCOUNTS_FILE = DATA_DIRECTORY / "accounts.json"
BUDGETS_FILE = DATA_DIRECTORY / "budgets.json"
CATEGORIES_FILE = DATA_DIRECTORY / "categories.json"
TRANSACTIONS_FILE = DATA_DIRECTORY / "transactions.json"
SAVINGS_GOALS_FILE = DATA_DIRECTORY / "savings_goals.json"
SAVINGS_GOAL_ALLOCATIONS_FILE = (
    DATA_DIRECTORY / "savings_goal_allocations.json"
)
BUDGET_ROLLOVERS_FILE = DATA_DIRECTORY / "budget_rollovers.json"
