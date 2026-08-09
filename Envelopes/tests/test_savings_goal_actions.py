from datetime import date

import pytest


def fund_savings(app, account_by_name, amount: float = 1000):
    checking = account_by_name("Checking")
    savings = account_by_name("Savings")
    return app.transactions.create_transfer(
        source_account_id=checking.account_id,
        destination_account_id=savings.account_id,
        amount=amount,
        transaction_date=date.today(),
        is_cleared=True,
    )


def test_user_can_create_edit_and_archive_goal(
    app,
) -> None:
    goal = app.goals.create_goal(
        name="Emergency Fund",
        target_amount_cents=500_000,
        target_date=date(2030, 1, 1),
    )

    goal.name = "Rainy Day Fund"
    goal.target_amount_cents = 600_000
    app.goals.save_goal(goal)

    saved = app.goals.get_goal(goal.goal_id)
    assert saved.name == "Rainy Day Fund"
    assert saved.target_amount_cents == 600_000

    app.goals.archive_goal(goal.goal_id)

    assert goal.goal_id not in {
        item.goal_id
        for item in app.goals.get_goals()
    }


def test_user_can_allocate_existing_savings_to_goal(
    app,
    account_by_name,
) -> None:
    fund_savings(app, account_by_name, 500)
    goal = app.goals.create_goal(
        name="Emergency Fund",
        target_amount_cents=100_000,
    )

    allocation = app.allocations.create_allocation(
        goal_id=goal.goal_id,
        amount_cents=30_000,
        source_type="manual",
        notes="Initial allocation",
    )
    app.allocations.sync_goal_current_amount(
        goal.goal_id
    )

    updated = app.goals.get_goal(goal.goal_id)

    assert allocation.amount_cents == 30_000
    assert updated.current_amount_cents == 30_000
    assert app.allocations.get_unallocated_savings_cents() == 20_000


def test_user_cannot_allocate_more_than_available_savings(
    app,
    account_by_name,
) -> None:
    fund_savings(app, account_by_name, 100)
    goal = app.goals.create_goal(
        name="Vacation",
        target_amount_cents=50_000,
    )

    with pytest.raises(ValueError, match="unallocated savings"):
        app.allocations.create_allocation(
            goal_id=goal.goal_id,
            amount_cents=20_000,
        )


def test_user_cannot_allocate_more_than_goal_target(
    app,
    account_by_name,
) -> None:
    fund_savings(app, account_by_name, 1000)
    goal = app.goals.create_goal(
        name="Laptop",
        target_amount_cents=50_000,
    )

    with pytest.raises(ValueError, match="remaining"):
        app.allocations.create_allocation(
            goal_id=goal.goal_id,
            amount_cents=60_000,
        )


def test_user_can_move_money_between_goals_without_changing_savings_balance(
    app,
    account_by_name,
) -> None:
    fund_savings(app, account_by_name, 500)
    source = app.goals.create_goal(
        name="Emergency Fund",
        target_amount_cents=100_000,
    )
    destination = app.goals.create_goal(
        name="Vacation",
        target_amount_cents=100_000,
    )

    app.allocations.create_allocation(
        goal_id=source.goal_id,
        amount_cents=40_000,
    )
    app.allocations.sync_goal_current_amount(
        source.goal_id
    )
    balance_before = app.allocations.get_savings_balance_cents()

    app.allocations.transfer_between_goals(
        source_goal_id=source.goal_id,
        destination_goal_id=destination.goal_id,
        amount_cents=15_000,
        notes="Vacation priority",
    )

    source_after = app.goals.get_goal(source.goal_id)
    destination_after = app.goals.get_goal(
        destination.goal_id
    )

    assert source_after.current_amount_cents == 25_000
    assert destination_after.current_amount_cents == 15_000
    assert app.allocations.get_savings_balance_cents() == balance_before


def test_user_cannot_move_more_than_source_goal_contains(
    app,
    account_by_name,
) -> None:
    fund_savings(app, account_by_name, 500)
    source = app.goals.create_goal(
        name="Emergency Fund",
        target_amount_cents=100_000,
    )
    destination = app.goals.create_goal(
        name="Vacation",
        target_amount_cents=100_000,
    )
    app.allocations.create_allocation(
        goal_id=source.goal_id,
        amount_cents=10_000,
    )
    app.allocations.sync_goal_current_amount(
        source.goal_id
    )

    with pytest.raises(ValueError, match="source goal"):
        app.allocations.transfer_between_goals(
            source_goal_id=source.goal_id,
            destination_goal_id=destination.goal_id,
            amount_cents=20_000,
        )


def test_deleting_goal_allocations_returns_money_to_unallocated_savings(
    app,
    account_by_name,
) -> None:
    fund_savings(app, account_by_name, 500)
    goal = app.goals.create_goal(
        name="Vacation",
        target_amount_cents=100_000,
    )
    app.allocations.create_allocation(
        goal_id=goal.goal_id,
        amount_cents=20_000,
    )

    app.allocations.delete_allocations_for_goal(
        goal.goal_id
    )

    assert app.allocations.get_goal_allocated_cents(
        goal.goal_id
    ) == 0
    assert app.allocations.get_unallocated_savings_cents() == 50_000


def test_user_can_move_goal_money_back_to_specific_savings_account(
    app,
    account_by_name,
) -> None:
    fund_savings(app, account_by_name, 500)
    savings = account_by_name("Savings")
    goal = app.goals.create_goal(
        name="Emergency Fund",
        target_amount_cents=100_000,
    )
    app.allocations.create_allocation(
        goal_id=goal.goal_id,
        amount_cents=40_000,
    )
    app.allocations.sync_goal_current_amount(goal.goal_id)

    savings_balance_before = (
        app.allocations.get_savings_balance_cents()
    )

    release = (
        app.allocations.release_goal_money_to_savings_account(
            source_goal_id=goal.goal_id,
            destination_account_id=savings.account_id,
            amount_cents=15_000,
            notes="Return to general savings",
        )
    )

    updated = app.goals.get_goal(goal.goal_id)

    assert release.amount_cents == -15_000
    assert release.source_type == "goal_release"
    assert "Savings" in release.notes
    assert updated.current_amount_cents == 25_000
    assert app.allocations.get_unallocated_savings_cents() == 25_000
    assert (
        app.allocations.get_savings_balance_cents()
        == savings_balance_before
    )


def test_goal_money_can_be_released_when_no_other_goal_exists(
    app,
    account_by_name,
) -> None:
    fund_savings(app, account_by_name, 300)
    savings = account_by_name("Savings")
    goal = app.goals.create_goal(
        name="Only Goal",
        target_amount_cents=50_000,
    )
    app.allocations.create_allocation(
        goal_id=goal.goal_id,
        amount_cents=20_000,
    )
    app.allocations.sync_goal_current_amount(goal.goal_id)

    app.allocations.release_goal_money_to_savings_account(
        source_goal_id=goal.goal_id,
        destination_account_id=savings.account_id,
        amount_cents=20_000,
    )

    assert app.goals.get_goal(goal.goal_id).current_amount_cents == 0
    assert app.allocations.get_unallocated_savings_cents() == 30_000


def test_user_can_move_goal_money_to_checking_account(
    app,
    account_by_name,
) -> None:
    fund_savings(app, account_by_name, 300)
    savings = account_by_name("Savings")
    checking = account_by_name("Checking")
    goal = app.goals.create_goal(
        name="Emergency Fund",
        target_amount_cents=50_000,
    )
    app.allocations.create_allocation(
        goal_id=goal.goal_id,
        amount_cents=20_000,
    )
    app.allocations.sync_goal_current_amount(goal.goal_id)

    checking_before = app.balances.get_current_balance_cents(
        checking
    )
    savings_before = app.balances.get_current_balance_cents(
        savings
    )

    release = app.allocations.move_goal_money_to_account(
        source_goal_id=goal.goal_id,
        source_savings_account_id=savings.account_id,
        destination_account_id=checking.account_id,
        amount_cents=10_000,
        transaction_date=date.today(),
        notes="Use for checking",
    )

    assert release.amount_cents == -10_000
    assert app.goals.get_goal(goal.goal_id).current_amount_cents == 10_000
    assert (
        app.balances.get_current_balance_cents(checking)
        == checking_before + 10_000
    )
    assert (
        app.balances.get_current_balance_cents(savings)
        == savings_before - 10_000
    )


def test_goal_move_to_same_savings_account_creates_no_extra_transfer(
    app,
    account_by_name,
) -> None:
    fund_savings(app, account_by_name, 300)
    savings = account_by_name("Savings")
    goal = app.goals.create_goal(
        name="Emergency Fund",
        target_amount_cents=50_000,
    )
    app.allocations.create_allocation(
        goal_id=goal.goal_id,
        amount_cents=20_000,
    )
    app.allocations.sync_goal_current_amount(goal.goal_id)

    before = [
        transaction
        for transaction in app.transactions.get_transactions()
        if transaction.is_transfer
    ]

    app.allocations.move_goal_money_to_account(
        source_goal_id=goal.goal_id,
        source_savings_account_id=savings.account_id,
        destination_account_id=savings.account_id,
        amount_cents=10_000,
        transaction_date=date.today(),
    )

    after = [
        transaction
        for transaction in app.transactions.get_transactions()
        if transaction.is_transfer
    ]

    assert len(after) == len(before)
    assert app.goals.get_goal(goal.goal_id).current_amount_cents == 10_000



def test_user_can_fund_goal_directly_from_checking_account(
    app,
    account_by_name,
) -> None:
    checking = account_by_name("Checking")
    savings = account_by_name("Savings")

    # Give checking money through an income transaction.
    paycheck = next(
        category
        for category in app.categories.get_categories()
        if category.name == "Paycheck"
    )
    app.transactions.create_transaction(
        account_id=checking.account_id,
        category_id=paycheck.category_id,
        payee="Employer",
        amount=1000,
        transaction_date=date.today(),
        is_cleared=True,
    )

    goal = app.goals.create_goal(
        name="Emergency Fund",
        target_amount_cents=100_000,
    )

    allocation = app.allocations.fund_goal_from_account(
        goal_id=goal.goal_id,
        source_account_id=checking.account_id,
        savings_account_id=savings.account_id,
        amount_cents=25_000,
        transaction_date=date.today(),
        notes="First contribution",
    )

    assert allocation.amount_cents == 25_000
    assert allocation.source_type == "account_funding"
    assert app.goals.get_goal(goal.goal_id).current_amount_cents == 25_000

    transfers = [
        transaction
        for transaction in app.transactions.get_transactions()
        if transaction.is_transfer
    ]
    assert len(transfers) == 2


def test_funding_goal_from_same_savings_account_does_not_create_transfer(
    app,
    account_by_name,
) -> None:
    fund_savings(app, account_by_name, 500)
    savings = account_by_name("Savings")
    goal = app.goals.create_goal(
        name="Vacation",
        target_amount_cents=100_000,
    )

    before = [
        transaction
        for transaction in app.transactions.get_transactions()
        if transaction.is_transfer
    ]

    app.allocations.fund_goal_from_account(
        goal_id=goal.goal_id,
        source_account_id=savings.account_id,
        savings_account_id=savings.account_id,
        amount_cents=20_000,
        transaction_date=date.today(),
    )

    after = [
        transaction
        for transaction in app.transactions.get_transactions()
        if transaction.is_transfer
    ]

    assert len(after) == len(before)
    assert app.goals.get_goal(goal.goal_id).current_amount_cents == 20_000


def test_direct_goal_funding_cannot_exceed_source_account_balance(
    app,
    account_by_name,
) -> None:
    checking = account_by_name("Checking")
    savings = account_by_name("Savings")
    goal = app.goals.create_goal(
        name="Laptop",
        target_amount_cents=100_000,
    )

    with pytest.raises(ValueError, match="source account balance"):
        app.allocations.fund_goal_from_account(
            goal_id=goal.goal_id,
            source_account_id=checking.account_id,
            savings_account_id=savings.account_id,
            amount_cents=10_000,
            transaction_date=date.today(),
        )
