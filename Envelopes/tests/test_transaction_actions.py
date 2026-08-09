from datetime import date

import pytest


def test_user_can_add_income_and_expense_and_balances_update(
    app,
    account_by_name,
    category_by_name,
) -> None:
    checking = account_by_name("Checking")
    paycheck = category_by_name("Paycheck", "Income")
    groceries = category_by_name("Groceries", "Expense")

    app.transactions.create_transaction(
        account_id=checking.account_id,
        category_id=paycheck.category_id,
        payee="Employer",
        amount=1000,
        transaction_date=date.today(),
        is_cleared=True,
    )
    app.transactions.create_transaction(
        account_id=checking.account_id,
        category_id=groceries.category_id,
        payee="Market",
        amount=125.50,
        transaction_date=date.today(),
        is_cleared=False,
    )

    assert (
        app.balances.get_current_balance_cents(checking)
        == 87_450
    )


def test_pending_to_cleared_changes_status_only(
    app,
    account_by_name,
    category_by_name,
) -> None:
    checking = account_by_name("Checking")
    groceries = category_by_name("Groceries", "Expense")

    original = app.transactions.create_transaction(
        account_id=checking.account_id,
        category_id=groceries.category_id,
        payee="Market",
        amount=75,
        transaction_date=date.today(),
        notes="Weekly groceries",
        is_cleared=False,
    )
    balance_before = app.balances.get_current_balance_cents(
        checking
    )

    updated = app.transactions.update_transaction(
        transaction_id=original.transaction_id,
        account_id=checking.account_id,
        category_id=groceries.category_id,
        payee="Market",
        amount=75,
        transaction_date=date.today(),
        notes="Weekly groceries",
        is_cleared=True,
    )

    assert updated.is_cleared is True
    assert updated.amount_cents == original.amount_cents
    assert updated.account_id == original.account_id
    assert len(app.transactions.get_transactions()) == 1
    assert (
        app.balances.get_current_balance_cents(checking)
        == balance_before
    )


def test_cleared_to_pending_changes_status_only(
    app,
    account_by_name,
    category_by_name,
) -> None:
    checking = account_by_name("Checking")
    groceries = category_by_name("Groceries", "Expense")

    original = app.transactions.create_transaction(
        account_id=checking.account_id,
        category_id=groceries.category_id,
        payee="Market",
        amount=40,
        transaction_date=date.today(),
        is_cleared=True,
    )

    updated = app.transactions.update_transaction(
        transaction_id=original.transaction_id,
        account_id=checking.account_id,
        category_id=groceries.category_id,
        payee="Market",
        amount=40,
        transaction_date=date.today(),
        is_cleared=False,
    )

    assert updated.is_cleared is False
    assert len(app.transactions.get_transactions()) == 1


def test_user_can_change_transaction_amount_account_and_category(
    app,
    account_by_name,
    category_by_name,
) -> None:
    checking = account_by_name("Checking")
    cash = account_by_name("Cash")
    groceries = category_by_name("Groceries", "Expense")
    fuel = category_by_name("Fuel", "Expense")

    transaction = app.transactions.create_transaction(
        account_id=checking.account_id,
        category_id=groceries.category_id,
        payee="Store",
        amount=25,
        transaction_date=date.today(),
    )

    updated = app.transactions.update_transaction(
        transaction_id=transaction.transaction_id,
        account_id=cash.account_id,
        category_id=fuel.category_id,
        payee="Gas Station",
        amount=60,
        transaction_date=date.today(),
        notes="Road trip",
        is_cleared=True,
    )

    assert updated.account_id == cash.account_id
    assert updated.category_id == fuel.category_id
    assert updated.amount_cents == -6000
    assert app.balances.get_current_balance_cents(checking) == 0
    assert app.balances.get_current_balance_cents(cash) == -6000


def test_user_can_delete_normal_transaction(
    app,
    account_by_name,
    category_by_name,
) -> None:
    checking = account_by_name("Checking")
    groceries = category_by_name("Groceries", "Expense")

    transaction = app.transactions.create_transaction(
        account_id=checking.account_id,
        category_id=groceries.category_id,
        payee="Store",
        amount=25,
        transaction_date=date.today(),
    )

    app.transactions.delete_transaction(
        transaction.transaction_id
    )

    assert app.transactions.get_transactions() == []
    assert app.balances.get_current_balance_cents(checking) == 0


def test_zero_amount_is_rejected(
    app,
    account_by_name,
    category_by_name,
) -> None:
    checking = account_by_name("Checking")
    groceries = category_by_name("Groceries", "Expense")

    with pytest.raises(ValueError):
        app.transactions.create_transaction(
            account_id=checking.account_id,
            category_id=groceries.category_id,
            payee="Store",
            amount=0,
            transaction_date=date.today(),
        )


def test_blank_payee_is_rejected(
    app,
    account_by_name,
    category_by_name,
) -> None:
    checking = account_by_name("Checking")
    groceries = category_by_name("Groceries", "Expense")

    with pytest.raises(ValueError, match="Payee"):
        app.transactions.create_transaction(
            account_id=checking.account_id,
            category_id=groceries.category_id,
            payee="   ",
            amount=20,
            transaction_date=date.today(),
        )


def test_archived_category_cannot_be_used_for_new_transaction(
    app,
    account_by_name,
) -> None:
    checking = account_by_name("Checking")
    category = app.categories.create_category(
        name="Temporary",
        category_type="Expense",
        color="#123456",
    )
    app.categories.archive_category(category.category_id)

    with pytest.raises(ValueError, match="Archived"):
        app.transactions.create_transaction(
            account_id=checking.account_id,
            category_id=category.category_id,
            payee="Store",
            amount=20,
            transaction_date=date.today(),
        )
