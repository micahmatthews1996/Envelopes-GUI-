from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

ASSETS_DIRECTORY = PROJECT_ROOT / "assets"
DATA_DIRECTORY = PROJECT_ROOT / "data"
GUI_DIRECTORY = PROJECT_ROOT / "gui"
STYLES_DIRECTORY = GUI_DIRECTORY / "styles"

STYLE_FILE = STYLES_DIRECTORY / "style.qss"
ACCOUNTS_FILE = DATA_DIRECTORY / "accounts.json"