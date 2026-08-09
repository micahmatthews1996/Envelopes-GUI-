import pytest


def test_default_accounts_are_available_to_new_user(
    app,
) -> None:
    accounts = app.accounts.get_accounts()

    assert [(a.name, a.account_type) for a in accounts] == [
        ("Cash", "Cash"),
        ("Checking", "Checking"),
        ("Savings", "Savings"),
    ]


def test_user_can_create_edit_and_delete_account(
    app,
) -> None:
    created = app.accounts.create_account(
        name="Travel Checking",
        account_type="Checking",
        opening_balance=125.50,
    )

    updated = app.accounts.update_account(
        account_id=created.account_id,
        name="Vacation Account",
        account_type="Savings",
        opening_balance=200.00,
    )

    assert updated.name == "Vacation Account"
    assert updated.account_type == "Savings"
    assert updated.opening_balance_cents == 20_000

    app.accounts.delete_account(updated.account_id)

    assert all(
        account.account_id != updated.account_id
        for account in app.accounts.get_accounts()
    )


@pytest.mark.parametrize(
    ("name", "account_type", "message"),
    [
        ("", "Checking", "Account name is required"),
        ("A" * 51, "Checking", "cannot exceed 50"),
        ("Brokerage", "Investment", "must be Checking"),
    ],
)
def test_invalid_account_input_is_rejected(
    app,
    name,
    account_type,
    message,
) -> None:
    with pytest.raises(ValueError, match=message):
        app.accounts.create_account(
            name=name,
            account_type=account_type,
            opening_balance=0,
        )


def test_duplicate_account_name_is_rejected_case_insensitively(
    app,
) -> None:
    with pytest.raises(
        ValueError,
        match="already exists",
    ):
        app.accounts.create_account(
            name="checking",
            account_type="Checking",
            opening_balance=0,
        )


def test_accounts_are_sorted_for_display(
    app,
) -> None:
    app.accounts.create_account(
        name="Zebra",
        account_type="Cash",
        opening_balance=0,
    )
    app.accounts.create_account(
        name="Alpha",
        account_type="Cash",
        opening_balance=0,
    )

    names = [
        account.name
        for account in app.accounts.get_accounts()
    ]

    assert names == sorted(names, key=str.casefold)
