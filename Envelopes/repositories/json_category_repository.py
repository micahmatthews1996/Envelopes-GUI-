import json
from json import JSONDecodeError
from pathlib import Path

from models.category import Category


class JsonCategoryRepository:
    """Stores and retrieves categories using a JSON file."""

    def __init__(self, file_path: Path) -> None:
        self._file_path = file_path
        self._prepare_storage()

    def get_all(self) -> list[Category]:
        """Return every valid category stored in the JSON file."""

        try:
            file_contents = self._file_path.read_text(
                encoding="utf-8",
            )
            stored_data = json.loads(file_contents)
        except FileNotFoundError:
            return []
        except JSONDecodeError as error:
            raise RuntimeError(
                "The categories data file contains invalid JSON."
            ) from error
        except OSError as error:
            raise RuntimeError(
                f"Unable to read categories: {error}"
            ) from error

        if not isinstance(stored_data, list):
            raise RuntimeError(
                "The categories data file must contain a JSON list."
            )

        categories: list[Category] = []

        for item in stored_data:
            if not isinstance(item, dict):
                continue

            try:
                category = Category.from_dictionary(item)
            except (KeyError, TypeError, ValueError):
                continue

            categories.append(category)

        return categories

    def get_by_id(
        self,
        category_id: str,
    ) -> Category | None:
        """Return a category by ID, or None when it does not exist."""

        for category in self.get_all():
            if category.category_id == category_id:
                return category

        return None

    def add(self, category: Category) -> None:
        """Add a category to storage."""

        categories = self.get_all()
        categories.append(category)

        self.save_all(categories)

    def update(
        self,
        updated_category: Category,
    ) -> None:
        """Replace an existing stored category."""

        categories = self.get_all()
        category_found = False

        for index, category in enumerate(categories):
            if (
                category.category_id
                == updated_category.category_id
            ):
                categories[index] = updated_category
                category_found = True
                break

        if not category_found:
            raise ValueError(
                "The category being updated could not be found."
            )

        self.save_all(categories)

    def delete(
        self,
        category_id: str,
    ) -> None:
        """Delete a category from storage."""

        categories = self.get_all()

        updated_categories = [
            category
            for category in categories
            if category.category_id != category_id
        ]

        if len(updated_categories) == len(categories):
            raise ValueError(
                "The category being deleted could not be found."
            )

        self.save_all(updated_categories)

    def save_all(
        self,
        categories: list[Category],
    ) -> None:
        """Replace the stored category collection."""

        serialized_categories = [
            category.to_dictionary()
            for category in categories
        ]

        try:
            self._file_path.write_text(
                json.dumps(
                    serialized_categories,
                    indent=4,
                ),
                encoding="utf-8",
            )
        except OSError as error:
            raise RuntimeError(
                f"Unable to save categories: {error}"
            ) from error

    def _prepare_storage(self) -> None:
        """Create the data directory and category file when necessary."""

        try:
            self._file_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            if not self._file_path.exists():
                self._file_path.write_text(
                    "[]",
                    encoding="utf-8",
                )
        except OSError as error:
            raise RuntimeError(
                f"Unable to prepare category storage: {error}"
            ) from error