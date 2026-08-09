from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from gui.dialogs.category_dialog import CategoryDialog
from gui.widgets.page_header import PageHeader
from gui.widgets.section_card import SectionCard
from models.category import Category
from services.category_service import CategoryService


class CategoryRow(QFrame):
    """Displays one category inside a category panel."""

    edit_requested = Signal(object)
    archive_requested = Signal(object)

    def __init__(
        self,
        category: Category,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self._category = category

        self.setObjectName("categoryRow")
        self.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        self.setMinimumHeight(72)

        self._create_interface()

    def _create_interface(self) -> None:
        """Create the category row interface."""

        color_indicator = QFrame()
        color_indicator.setObjectName(
            "categoryColorDot"
        )
        color_indicator.setFixedSize(16, 16)
        color_indicator.setStyleSheet(
            (
                "background-color: "
                f"{self._category.color};"
                "border: none;"
                "border-radius: 8px;"
            )
        )

        category_name = QLabel(
            self._category.name
        )
        category_name.setObjectName(
            "categoryRowName"
        )

        edit_button = QPushButton("Edit")
        edit_button.setObjectName(
            "categoryEditButton"
        )
        edit_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        edit_button.clicked.connect(
            lambda: self.edit_requested.emit(
                self._category
            )
        )

        archive_button = QPushButton("Archive")
        archive_button.setObjectName(
            "categoryArchiveButton"
        )
        archive_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        archive_button.clicked.connect(
            lambda: self.archive_requested.emit(
                self._category
            )
        )

        name_layout = QHBoxLayout()
        name_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        name_layout.setSpacing(12)
        name_layout.addWidget(
            color_indicator
        )
        name_layout.addWidget(
            category_name
        )
        name_layout.addStretch()

        action_layout = QHBoxLayout()
        action_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        action_layout.setSpacing(4)
        action_layout.addWidget(
            edit_button
        )
        action_layout.addWidget(
            archive_button
        )

        row_layout = QHBoxLayout(self)
        row_layout.setContentsMargins(
            16,
            12,
            10,
            12,
        )
        row_layout.setSpacing(12)
        row_layout.addLayout(
            name_layout,
            stretch=1,
        )
        row_layout.addLayout(
            action_layout
        )

    def mouseDoubleClickEvent(
        self,
        event: QMouseEvent,
    ) -> None:
        """Open the category editor when double-clicked."""

        if (
            event.button()
            == Qt.MouseButton.LeftButton
        ):
            self.edit_requested.emit(
                self._category
            )
            event.accept()
            return

        super().mouseDoubleClickEvent(
            event
        )


class CategoriesPage(QWidget):
    """Displays and manages custom transaction categories."""

    def __init__(
        self,
        category_service: CategoryService,
    ) -> None:
        super().__init__()

        self._category_service = (
            category_service
        )

        self._expense_list_widget = QWidget()
        self._expense_list_layout = QVBoxLayout(
            self._expense_list_widget
        )

        self._income_list_widget = QWidget()
        self._income_list_layout = QVBoxLayout(
            self._income_list_widget
        )

        self._expense_count_label = QLabel("0")
        self._income_count_label = QLabel("0")

        self.setObjectName("page")

        self._create_interface()
        self.refresh_categories()

    def _create_interface(self) -> None:
        """Create the Categories page interface."""

        add_category_button = QPushButton(
            "+ Add Category"
        )
        add_category_button.setObjectName(
            "primaryButton"
        )
        add_category_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        add_category_button.clicked.connect(
            lambda: self._open_category_dialog()
        )

        page_header = PageHeader(
            title="Categories",
            description=(
                "Create custom categories for transactions, "
                "budgets, and spending reports."
            ),
            action_widget=add_category_button,
        )

        self._configure_list_layout(
            self._expense_list_layout
        )
        self._configure_list_layout(
            self._income_list_layout
        )

        expense_panel = self._create_category_panel(
            title="Expense Categories",
            count_label=(
                self._expense_count_label
            ),
            list_widget=(
                self._expense_list_widget
            ),
        )

        income_panel = self._create_category_panel(
            title="Income Categories",
            count_label=(
                self._income_count_label
            ),
            list_widget=(
                self._income_list_widget
            ),
        )

        panels_layout = QHBoxLayout()
        panels_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        panels_layout.setSpacing(18)
        panels_layout.addWidget(
            expense_panel,
            stretch=1,
        )
        panels_layout.addWidget(
            income_panel,
            stretch=1,
        )

        page_layout = QVBoxLayout(self)
        page_layout.setContentsMargins(
            40,
            32,
            40,
            32,
        )
        page_layout.setSpacing(24)
        page_layout.addWidget(
            page_header
        )
        page_layout.addLayout(
            panels_layout,
            stretch=1,
        )

    def _configure_list_layout(
        self,
        layout: QVBoxLayout,
    ) -> None:
        """Configure a category list layout."""

        layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        layout.setSpacing(0)
        layout.setAlignment(
            Qt.AlignmentFlag.AlignTop
        )

    def _create_category_panel(
        self,
        title: str,
        count_label: QLabel,
        list_widget: QWidget,
    ) -> SectionCard:
        """Create one independently scrollable category panel."""

        count_label.setObjectName(
            "categoryCountBadge"
        )
        count_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        panel = SectionCard(
            title=title,
            action_widget=count_label,
        )

        scroll_area = QScrollArea()
        scroll_area.setObjectName(
            "categoryPanelScrollArea"
        )
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(
            QFrame.Shape.NoFrame
        )
        scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        scroll_area.setWidget(
            list_widget
        )

        panel.add_widget(
            scroll_area,
            stretch=1,
        )

        return panel

    def refresh_categories(self) -> None:
        """Reload and display all active categories."""

        self._clear_category_list(
            self._expense_list_layout
        )
        self._clear_category_list(
            self._income_list_layout
        )

        try:
            categories = (
                self._category_service.get_categories()
            )
        except RuntimeError as error:
            QMessageBox.critical(
                self,
                "Unable to Load Categories",
                str(error),
            )
            return

        expense_categories = [
            category
            for category in categories
            if (
                category.category_type
                == "Expense"
            )
        ]

        income_categories = [
            category
            for category in categories
            if (
                category.category_type
                == "Income"
            )
        ]

        self._expense_count_label.setText(
            str(len(expense_categories))
        )
        self._income_count_label.setText(
            str(len(income_categories))
        )

        self._populate_category_list(
            layout=self._expense_list_layout,
            categories=expense_categories,
            empty_title=(
                "No expense categories"
            ),
            empty_description=(
                "Create an expense category "
                "to organize spending."
            ),
        )

        self._populate_category_list(
            layout=self._income_list_layout,
            categories=income_categories,
            empty_title=(
                "No income categories"
            ),
            empty_description=(
                "Create an income category "
                "to organize earnings."
            ),
        )

    def _populate_category_list(
        self,
        layout: QVBoxLayout,
        categories: list[Category],
        empty_title: str,
        empty_description: str,
    ) -> None:
        """Populate one category panel."""

        if not categories:
            empty_state = (
                self._create_panel_empty_state(
                    title=empty_title,
                    description=(
                        empty_description
                    ),
                )
            )

            layout.addWidget(
                empty_state
            )
            layout.addStretch()
            return

        for index, category in enumerate(
            categories
        ):
            category_row = (
                self._create_category_row(
                    category
                )
            )

            layout.addWidget(
                category_row
            )

            if (
                index
                < len(categories) - 1
            ):
                divider = QFrame()
                divider.setObjectName(
                    "categoryRowDivider"
                )
                divider.setFrameShape(
                    QFrame.Shape.HLine
                )
                divider.setFixedHeight(1)

                layout.addWidget(
                    divider
                )

        layout.addStretch()

    def _create_category_row(
        self,
        category: Category,
    ) -> CategoryRow:
        """Create one interactive category row."""

        category_row = CategoryRow(
            category=category,
            parent=self,
        )

        category_row.edit_requested.connect(
            self._open_category_dialog
        )
        category_row.archive_requested.connect(
            self._confirm_archive
        )

        return category_row

    def _create_panel_empty_state(
        self,
        title: str,
        description: str,
    ) -> QFrame:
        """Create an empty message for one category panel."""

        empty_state = QFrame()
        empty_state.setObjectName(
            "categoryPanelEmptyState"
        )

        title_label = QLabel(title)
        title_label.setObjectName(
            "categoryPanelEmptyTitle"
        )
        title_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        description_label = QLabel(
            description
        )
        description_label.setObjectName(
            "categoryPanelEmptyDescription"
        )
        description_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        description_label.setWordWrap(True)

        create_button = QPushButton(
            "+ Add Category"
        )
        create_button.setObjectName(
            "secondaryButton"
        )
        create_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        create_button.clicked.connect(
            lambda: self._open_category_dialog()
        )

        empty_layout = QVBoxLayout(
            empty_state
        )
        empty_layout.setContentsMargins(
            24,
            40,
            24,
            40,
        )
        empty_layout.setSpacing(10)
        empty_layout.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        empty_layout.addWidget(
            title_label
        )
        empty_layout.addWidget(
            description_label
        )
        empty_layout.addSpacing(6)
        empty_layout.addWidget(
            create_button,
            alignment=(
                Qt.AlignmentFlag.AlignCenter
            ),
        )

        return empty_state

    def _open_category_dialog(
        self,
        category: Category | None = None,
    ) -> None:
        """Open the category dialog in create or edit mode."""

        dialog = CategoryDialog(
            parent=self,
            category=category,
        )

        while dialog.exec():
            (
                category_name,
                category_type,
                category_color,
            ) = dialog.get_category_data()

            try:
                if category is None:
                    self._category_service.create_category(
                        name=category_name,
                        category_type=category_type,
                        color=category_color,
                    )
                else:
                    self._category_service.update_category(
                        category_id=(
                            category.category_id
                        ),
                        name=category_name,
                        category_type=category_type,
                        color=category_color,
                    )
            except ValueError as error:
                dialog.show_error(str(error))
                continue
            except RuntimeError as error:
                QMessageBox.critical(
                    self,
                    "Unable to Save Category",
                    str(error),
                )
                return

            self.refresh_categories()
            break

    def _confirm_archive(
        self,
        category: Category,
    ) -> None:
        """Ask the user to confirm category archiving."""

        response = QMessageBox.question(
            self,
            "Archive Category",
            (
                f'Archive "{category.name}"?\n\n'
                "Archived categories will no longer appear "
                "when creating new transactions, but their "
                "financial history will be preserved."
            ),
            (
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No
            ),
            QMessageBox.StandardButton.No,
        )

        if (
            response
            != QMessageBox.StandardButton.Yes
        ):
            return

        try:
            self._category_service.archive_category(
                category.category_id
            )
        except (
            ValueError,
            RuntimeError,
        ) as error:
            QMessageBox.critical(
                self,
                "Unable to Archive Category",
                str(error),
            )
            return

        self.refresh_categories()

    def _clear_category_list(
        self,
        layout: QVBoxLayout,
    ) -> None:
        """Remove all widgets shown in a category list."""

        while layout.count():
            layout_item = layout.takeAt(0)
            widget = layout_item.widget()

            if widget is not None:
                widget.deleteLater()
                continue

            child_layout = (
                layout_item.layout()
            )

            if child_layout is not None:
                self._delete_layout(
                    child_layout
                )

    def _delete_layout(
        self,
        layout: QVBoxLayout | QHBoxLayout,
    ) -> None:
        """Delete all widgets and child layouts."""

        while layout.count():
            layout_item = layout.takeAt(0)
            widget = layout_item.widget()

            if widget is not None:
                widget.deleteLater()
                continue

            child_layout = (
                layout_item.layout()
            )

            if child_layout is not None:
                self._delete_layout(
                    child_layout
                )