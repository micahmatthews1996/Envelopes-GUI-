import pytest


def test_default_categories_include_transfer_system_category(
    app,
) -> None:
    transfer = app.categories.get_transfer_category()

    assert transfer.name == "Transfer"
    assert transfer.category_type == "Transfer"
    assert transfer.is_system is True


def test_user_can_create_edit_archive_restore_and_delete_category(
    app,
) -> None:
    category = app.categories.create_category(
        name="Pets",
        category_type="Expense",
        color="#123ABC",
    )

    edited = app.categories.update_category(
        category_id=category.category_id,
        name="Pet Care",
        category_type="Expense",
        color="#ABC123",
    )
    assert edited.name == "Pet Care"
    assert edited.color == "#ABC123"

    archived = app.categories.archive_category(
        edited.category_id
    )
    assert archived.is_archived is True
    assert archived.category_id not in {
        item.category_id
        for item in app.categories.get_categories()
    }

    restored = app.categories.restore_category(
        edited.category_id
    )
    assert restored.is_archived is False

    app.categories.delete_category(edited.category_id)
    with pytest.raises(ValueError, match="could not be found"):
        app.categories.get_category_by_id(
            edited.category_id
        )


def test_duplicate_category_name_with_same_type_is_rejected(
    app,
) -> None:
    app.categories.create_category(
        name="Pets",
        category_type="Expense",
        color="#123456",
    )

    with pytest.raises(ValueError, match="already exists"):
        app.categories.create_category(
            name="pets",
            category_type="Expense",
            color="#654321",
        )


def test_same_category_name_can_be_used_for_income_and_expense(
    app,
) -> None:
    expense = app.categories.create_category(
        name="Side Work",
        category_type="Expense",
        color="#112233",
    )
    income = app.categories.create_category(
        name="Side Work",
        category_type="Income",
        color="#334455",
    )

    assert expense.category_type == "Expense"
    assert income.category_type == "Income"


@pytest.mark.parametrize(
    ("name", "category_type", "color", "message"),
    [
        ("", "Expense", "#123456", "required"),
        ("A" * 51, "Expense", "#123456", "cannot exceed"),
        ("Pets", "Unknown", "#123456", "must be Expense"),
        ("Pets", "Expense", "red", "format #RRGGBB"),
        ("Pets", "Expense", "#ZZZZZZ", "invalid characters"),
    ],
)
def test_invalid_category_input_is_rejected(
    app,
    name,
    category_type,
    color,
    message,
) -> None:
    with pytest.raises(ValueError, match=message):
        app.categories.create_category(
            name=name,
            category_type=category_type,
            color=color,
        )


def test_system_category_cannot_be_edited_archived_or_deleted(
    app,
) -> None:
    transfer = app.categories.get_transfer_category()

    with pytest.raises(ValueError, match="cannot be edited"):
        app.categories.update_category(
            category_id=transfer.category_id,
            name="Transfers",
            category_type="Transfer",
            color="#123456",
        )

    with pytest.raises(ValueError, match="cannot be archived"):
        app.categories.archive_category(
            transfer.category_id
        )

    with pytest.raises(ValueError, match="cannot be deleted"):
        app.categories.delete_category(
            transfer.category_id
        )
