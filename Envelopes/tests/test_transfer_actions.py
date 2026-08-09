from datetime import date

import pytest


def test_transfer_creates_two_linked_entries_and_preserves_net_worth(
    app,
    account_by_name,
) -> None:
    checking = account_by_name("Checking")
    savings = account_by_name("Savings")

    source, destination = app.transactions.create_transfer(
        source_account_id=checking.account_id,
        destination_account_id=savings.account_id,
        amount=300,
        transaction_date=date.today(),
        notes="Monthly savings",
        is_cleared=False,
    )

    linked = app.transactions.get_transfer_transactions(
        source.transfer_id
    )

    assert len(linked) == 2
    assert source.amount_cents == -30_000
    assert destination.amount_cents == 30_000
    assert source.transfer_id == destination.transfer_id
    assert (
        app.balances.get_total_balance_cents(
            app.accounts.get_accounts()
        )
        == 0
    )


def test_pending_transfer_can_be_marked_cleared_without_duplication(
    app,
    account_by_name,
) -> None:
    checking = account_by_name("Checking")
    savings = account_by_name("Savings")

    source, _ = app.transactions.create_transfer(
        source_account_id=checking.account_id,
        destination_account_id=savings.account_id,
        amount=250,
        transaction_date=date.today(),
        is_cleared=False,
    )

    updated_source, updated_destination = (
        app.transactions.update_transfer(
            transfer_id=source.transfer_id,
            source_account_id=checking.account_id,
            destination_account_id=savings.account_id,
            amount=250,
            transaction_date=date.today(),
            is_cleared=True,
        )
    )

    linked = app.transactions.get_transfer_transactions(
        source.transfer_id
    )

    assert len(linked) == 2
    assert updated_source.is_cleared is True
    assert updated_destination.is_cleared is True
    assert app.balances.get_current_balance_cents(checking) == -25_000
    assert app.balances.get_current_balance_cents(savings) == 25_000


def test_user_can_edit_transfer_amount_and_destination(
    app,
    account_by_name,
) -> None:
    checking = account_by_name("Checking")
    savings = account_by_name("Savings")
    cash = account_by_name("Cash")

    source, _ = app.transactions.create_transfer(
        source_account_id=checking.account_id,
        destination_account_id=savings.account_id,
        amount=100,
        transaction_date=date.today(),
    )

    app.transactions.update_transfer(
        transfer_id=source.transfer_id,
        source_account_id=checking.account_id,
        destination_account_id=cash.account_id,
        amount=150,
        transaction_date=date.today(),
        notes="Use cash instead",
        is_cleared=True,
    )

    assert app.balances.get_current_balance_cents(checking) == -15_000
    assert app.balances.get_current_balance_cents(savings) == 0
    assert app.balances.get_current_balance_cents(cash) == 15_000


def test_deleting_one_transfer_row_deletes_both_rows(
    app,
    account_by_name,
) -> None:
    checking = account_by_name("Checking")
    savings = account_by_name("Savings")

    source, _ = app.transactions.create_transfer(
        source_account_id=checking.account_id,
        destination_account_id=savings.account_id,
        amount=100,
        transaction_date=date.today(),
    )

    app.transactions.delete_transaction(
        source.transaction_id
    )

    assert app.transactions.get_transactions() == []
    assert app.balances.get_current_balance_cents(checking) == 0
    assert app.balances.get_current_balance_cents(savings) == 0


def test_transfer_to_same_account_is_rejected(
    app,
    account_by_name,
) -> None:
    checking = account_by_name("Checking")

    with pytest.raises(ValueError, match="must be different"):
        app.transactions.create_transfer(
            source_account_id=checking.account_id,
            destination_account_id=checking.account_id,
            amount=100,
            transaction_date=date.today(),
        )


def test_zero_transfer_amount_is_rejected(
    app,
    account_by_name,
) -> None:
    checking = account_by_name("Checking")
    savings = account_by_name("Savings")

    with pytest.raises(ValueError):
        app.transactions.create_transfer(
            source_account_id=checking.account_id,
            destination_account_id=savings.account_id,
            amount=0,
            transaction_date=date.today(),
        )
