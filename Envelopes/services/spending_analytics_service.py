from datetime import date

from models.dashboard_summary import (
    DashboardCategorySpendingItem,
)
from services.category_service import CategoryService
from services.transaction_service import TransactionService


class SpendingAnalyticsService:
    """Calculates reusable spending analytics."""

    def __init__(
        self,
        transaction_service: TransactionService,
        category_service: CategoryService,
    ) -> None:
        self._transaction_service = transaction_service
        self._category_service = category_service

    def get_category_spending(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
        maximum_categories: int = 6,
    ) -> list[DashboardCategorySpendingItem]:
        """
        Return expense totals grouped by category.

        When no date range is supplied, spending from the
        current calendar month is returned.
        """

        range_start, range_end = (
            self._resolve_date_range(
                start_date=start_date,
                end_date=end_date,
            )
        )

        categories = (
            self._category_service.get_categories(
                include_archived=True
            )
        )

        transactions = (
            self._transaction_service.get_transactions()
        )

        category_lookup = {
            category.category_id: category
            for category in categories
        }

        spending_by_category: dict[str, int] = {}

        for transaction in transactions:
            if transaction.is_transfer:
                continue

            if transaction.amount_cents >= 0:
                continue

            if not (
                range_start
                <= transaction.transaction_date
                <= range_end
            ):
                continue

            spending_by_category[
                transaction.category_id
            ] = (
                spending_by_category.get(
                    transaction.category_id,
                    0,
                )
                + abs(transaction.amount_cents)
            )

        spending_items: list[
            DashboardCategorySpendingItem
        ] = []

        for (
            category_id,
            amount_cents,
        ) in spending_by_category.items():
            category = category_lookup.get(
                category_id
            )

            if category is None:
                category_name = "Unknown Category"
                category_color = "#667085"
            else:
                category_name = category.name
                category_color = category.color

            spending_items.append(
                DashboardCategorySpendingItem(
                    category_name=category_name,
                    amount_cents=amount_cents,
                    color=category_color,
                )
            )

        spending_items.sort(
            key=lambda item: item.amount_cents,
            reverse=True,
        )

        return self._group_smaller_categories(
            spending_items=spending_items,
            maximum_categories=maximum_categories,
        )

    def _resolve_date_range(
        self,
        start_date: date | None,
        end_date: date | None,
    ) -> tuple[date, date]:
        """Validate or create the requested spending period."""

        if start_date is None and end_date is None:
            today = date.today()

            month_start = date(
                today.year,
                today.month,
                1,
            )

            return month_start, today

        if start_date is None or end_date is None:
            raise ValueError(
                "Both a start date and end date are required."
            )

        if start_date > end_date:
            raise ValueError(
                "The spending start date cannot be "
                "after the end date."
            )

        return start_date, end_date

    def _group_smaller_categories(
        self,
        spending_items: list[
            DashboardCategorySpendingItem
        ],
        maximum_categories: int,
    ) -> list[DashboardCategorySpendingItem]:
        """Group smaller categories into an Other item."""

        if maximum_categories < 2:
            raise ValueError(
                "Maximum categories must be at least two."
            )

        if len(spending_items) <= maximum_categories:
            return spending_items

        visible_item_count = maximum_categories - 1

        visible_items = spending_items[
            :visible_item_count
        ]

        grouped_items = spending_items[
            visible_item_count:
        ]

        other_total_cents = sum(
            item.amount_cents
            for item in grouped_items
        )

        visible_items.append(
            DashboardCategorySpendingItem(
                category_name="Other",
                amount_cents=other_total_cents,
                color="#667085",
            )
        )

        return visible_items