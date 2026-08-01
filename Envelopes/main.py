import sys

from PySide6.QtWidgets import QApplication

from core.application_container import ApplicationContainer
from gui.styles.style_loader import load_stylesheet
from gui.windows.main_window import MainWindow
from utils.paths import STYLE_FILE


def main() -> None:
    """Start the Envelopes desktop application."""

    application = QApplication(sys.argv)
    application.setApplicationName("Envelopes")
    application.setOrganizationName("Envelopes")

    stylesheet = load_stylesheet(STYLE_FILE)
    application.setStyleSheet(stylesheet)

    container = ApplicationContainer()

    window = MainWindow(container)
    window.show()

    sys.exit(application.exec())


if __name__ == "__main__":
    main()