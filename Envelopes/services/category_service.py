from uuid import uuid4

from models.category import Category
from repositories.json_category_repository import JsonCategoryRepository


VALID_CATEGORY_TYPES = {
    "Expense",
    "Income",
    "Transfer",
}


TRANSFER_CATEGORY_NAME = "Transfer"
TRANSFER_CATEGORY_COLOR = "#2F80ED"

DEFAULT_CATEGORIES = [
    {
        "name": "Groceries",
        "category_type": "Expense",
        "color": "#27AE60",
    },
    {
        "name": "Restaurants",
        "category_type": "Expense",
        "color": "#EB5757",
    },
    {
        "name": "Fuel",
        "category_type": "Expense",
        "color": "#F2994A",
    },
    {
        "name": "Housing",
        "category_type": "Expense",
        "color": "#9B51E0",
    },
    {
        "name": "Utilities",
        "category_type": "Expense",
        "color": "#2D9CDB",
    },
    {
        "name": "Insurance",
        "category_type": "Expense",
        "color": "#56CCF2",
    },
    {
        "name": "Healthcare",
        "category_type": "Expense",
        "color": "#E0529C",
    },
    {
        "name": "Entertainment",
        "category_type": "Expense",
        "color": "#BB6BD9",
    },
    {
        "name": "Shopping",
        "category_type": "Expense",
        "color": "#F2C94C",
    },
    {
        "name": "Travel",
        "category_type": "Expense",
        "color": "#6FCF97",
    },
    {
        "name": "Education",
        "category_type": "Expense",
        "color": "#2F80ED",
    },
    {
        "name": "Personal Care",
        "category_type": "Expense",
        "color": "#F299C2",
    },
    {
        "name": "Gifts",
        "category_type": "Expense",
        "color": "#F27A54",
    },
    {
        "name": "Taxes",
        "category_type": "Expense",
        "color": "#828282",
    },
    {
        "name": "Miscellaneous",
        "category_type": "Expense",
        "color": "#6B7280",
    },
    {
        "name": "Paycheck",
        "category_type": "Income",
        "color": "#219653",
    },
    {
        "name": "Bonus",
        "category_type": "Income",
        "color": "#27AE60",
    },
    {
        "name": "Interest",
        "category_type": "Income",
        "color": "#2D9CDB",
    },
    {
        "name": "Dividends",
        "category_type": "Income",
        "color": "#56CCF2",
    },
    {
        "name": "Refund",
        "category_type": "Income",
        "color": "#6FCF97",
    },
    {
        "name": "Gift Income",
        "category_type": "Income",
        "color": "#BB6BD9",
    },
    {
        "name": "Sale",
        "category_type": "Income",
        "color": "#F2C94C",
    },
    {
        "name": "Other Income",
        "category_type": "Income",
        "color": "#828282",
    },
]


class CategoryService:
    """Provides category-related business operations."""

    def __init__(
        self,
        repository: JsonCategoryRepository,
    ) -> None:
        self._repository = repository

    def seed_default_categories(self) -> bool:
        """
        Create starter categories and ensure Transfer exists.

        Returns True when any categories were created and False
        when existing category data was left unchanged.
        """

        categories = self._repository.get_all()
        categories_created = False

        if not categories:
            categories = [
                Category(
                    category_id=str(uuid4()),
                    name=str(category_data["name"]),
                    category_type=str(
                        category_data["category_type"]
                    ),
                    color=str(category_data["color"]),
                    is_system=False,
                    is_archived=False,
                )
                for category_data in DEFAULT_CATEGORIES
            ]
            categories_created = True

        transfer_exists = any(
            category.name.casefold()
            == TRANSFER_CATEGORY_NAME.casefold()
            and category.category_type.casefold()
            == "transfer"
            for category in categories
        )

        if not transfer_exists:
            categories.append(
                Category(
                    category_id=str(uuid4()),
                    name=TRANSFER_CATEGORY_NAME,
                    category_type="Transfer",
                    color=TRANSFER_CATEGORY_COLOR,
                    is_system=True,
                    is_archived=False,
                )
            )
            categories_created = True

        if categories_created:
            self._repository.save_all(categories)

        return categories_created

    def get_categories(
        self,
        include_archived: bool = False,
    ) -> list[Category]:
        """Return categories sorted by type and name."""

        categories = self._repository.get_all()

        categories = [
            category
            for category in categories
            if category.category_type != "Transfer"
        ]

        if not include_archived:
            categories = [
                category
                for category in categories
                if not category.is_archived
            ]

        return sorted(
            categories,
            key=lambda category: (
                category.category_type.casefold(),
                category.name.casefold(),
            ),
        )

    def get_category_by_id(
        self,
        category_id: str,
    ) -> Category:
        """Return a category by its unique identifier."""

        category = self._repository.get_by_id(
            category_id
        )

        if category is None:
            raise ValueError(
                "The selected category could not be found."
            )

        return category

    def get_transfer_category(self) -> Category:
        """Return the system Transfer category."""

        for category in self._repository.get_all():
            if (
                category.name.casefold()
                == TRANSFER_CATEGORY_NAME.casefold()
                and category.category_type.casefold()
                == "transfer"
                and not category.is_archived
            ):
                return category

        raise ValueError(
            "The system Transfer category could not be found."
        )

    def create_category(
        self,
        name: str,
        category_type: str,
        color: str,
    ) -> Category:
        """Validate and create a custom category."""

        cleaned_name = self._validate_name(name)
        cleaned_type = self._validate_category_type(
            category_type
        )
        cleaned_color = self._validate_color(color)

        self._ensure_unique_name(
            name=cleaned_name,
            category_type=cleaned_type,
        )

        category = Category(
            category_id=str(uuid4()),
            name=cleaned_name,
            category_type=cleaned_type,
            color=cleaned_color,
            is_system=False,
            is_archived=False,
        )

        self._repository.add(category)

        return category

    def update_category(
        self,
        category_id: str,
        name: str,
        category_type: str,
        color: str,
    ) -> Category:
        """Validate and update an existing custom category."""

        existing_category = self.get_category_by_id(
            category_id
        )

        if existing_category.is_system:
            raise ValueError(
                "System categories cannot be edited."
            )

        cleaned_name = self._validate_name(name)
        cleaned_type = self._validate_category_type(
            category_type
        )
        cleaned_color = self._validate_color(color)

        self._ensure_unique_name(
            name=cleaned_name,
            category_type=cleaned_type,
            excluded_category_id=category_id,
        )

        updated_category = Category(
            category_id=existing_category.category_id,
            name=cleaned_name,
            category_type=cleaned_type,
            color=cleaned_color,
            is_system=existing_category.is_system,
            is_archived=existing_category.is_archived,
        )

        self._repository.update(updated_category)

        return updated_category

    def archive_category(
        self,
        category_id: str,
    ) -> Category:
        """Archive a custom category."""

        category = self.get_category_by_id(
            category_id
        )

        if category.is_system:
            raise ValueError(
                "System categories cannot be archived."
            )

        archived_category = Category(
            category_id=category.category_id,
            name=category.name,
            category_type=category.category_type,
            color=category.color,
            is_system=category.is_system,
            is_archived=True,
        )

        self._repository.update(archived_category)

        return archived_category

    def restore_category(
        self,
        category_id: str,
    ) -> Category:
        """Restore an archived category."""

        category = self.get_category_by_id(
            category_id
        )

        restored_category = Category(
            category_id=category.category_id,
            name=category.name,
            category_type=category.category_type,
            color=category.color,
            is_system=category.is_system,
            is_archived=False,
        )

        self._repository.update(restored_category)

        return restored_category

    def delete_category(
        self,
        category_id: str,
    ) -> None:
        """Delete a category."""

        category = self.get_category_by_id(
            category_id
        )

        if category.is_system:
            raise ValueError(
                "System categories cannot be deleted."
            )

        self._repository.delete(category_id)

    def _ensure_unique_name(
        self,
        name: str,
        category_type: str,
        excluded_category_id: str | None = None,
    ) -> None:
        """Ensure names are unique within each category type."""

        for category in self._repository.get_all():
            if (
                category.category_id
                != excluded_category_id
                and category.name.casefold()
                == name.casefold()
                and category.category_type.casefold()
                == category_type.casefold()
            ):
                raise ValueError(
                    "A category with that name already exists."
                )

    def _validate_name(
        self,
        name: str,
    ) -> str:
        """Validate a category name."""

        cleaned_name = name.strip()

        if not cleaned_name:
            raise ValueError(
                "Category name is required."
            )

        if len(cleaned_name) > 50:
            raise ValueError(
                "Category name cannot exceed 50 characters."
            )

        return cleaned_name

    def _validate_category_type(
        self,
        category_type: str,
    ) -> str:
        """Validate the category type."""

        cleaned_type = category_type.strip().title()

        if cleaned_type not in VALID_CATEGORY_TYPES:
            raise ValueError(
                "Category type must be Expense, Income, or Transfer."
            )

        return cleaned_type

    def _validate_color(
        self,
        color: str,
    ) -> str:
        """Validate a hexadecimal color."""

        cleaned_color = color.strip().upper()

        if (
            len(cleaned_color) != 7
            or not cleaned_color.startswith("#")
        ):
            raise ValueError(
                "Category color must use the format #RRGGBB."
            )

        valid_characters = set(
            "0123456789ABCDEF"
        )

        if any(
            character not in valid_characters
            for character in cleaned_color[1:]
        ):
            raise ValueError(
                "Category color contains invalid characters."
            )

        return cleaned_color