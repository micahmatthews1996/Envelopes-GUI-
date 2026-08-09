from dataclasses import asdict, dataclass


@dataclass(slots=True)
class Category:
    """Represents a customizable transaction category."""

    category_id: str
    name: str
    category_type: str
    color: str
    is_system: bool = False
    is_archived: bool = False

    def to_dictionary(
        self,
    ) -> dict[str, str | bool]:
        """Convert the category into JSON-compatible data."""

        return asdict(self)

    @classmethod
    def from_dictionary(
        cls,
        category_data: dict[str, object],
    ) -> "Category":
        """Create a category from stored JSON data."""

        return cls(
            category_id=str(
                category_data["category_id"]
            ),
            name=str(
                category_data["name"]
            ),
            category_type=str(
                category_data["category_type"]
            ),
            color=str(
                category_data.get(
                    "color",
                    "#2F80ED",
                )
            ),
            is_system=bool(
                category_data.get(
                    "is_system",
                    False,
                )
            ),
            is_archived=bool(
                category_data.get(
                    "is_archived",
                    False,
                )
            ),
        )