from datetime import date

import pytest


def test_user_can_create_edit_archive_restore_and_delete_budget(
    app,
    category_by_name,
) -> None:
    groceries = category_by_name("Groceries", "Expense")

    budget = app.budgets.create_budget(
        category_id=groceries.category_id,
        monthly_limit=500,
    )
    edited = app.budgets.update_budget(
        budget_id=budget.budget_id,
        category_id=groceries.category_id,
        monthly_limit=650,
    )
    assert edited.monthly_limit_cents == 65_000

    archived = app.budgets.archive_budget(
        budget.budget_id
    )
    assert archived.is_archived is True
    assert app.budgets.get_budgets() == []

    restored = app.budgets.restore_budget(
        budget.budget_id
    )
    assert restored.is_archived is False

    app.budgets.delete_budget(budget.budget_id)
    assert app.budgets.get_budgets(
        include_archived=True
    ) == []


def test_duplicate_active_budget_for_category_is_rejected(
    app,
    category_by_name,
) -> None:
    groceries = category_by_name("Groceries", "Expense")
    app.budgets.create_budget(
        category_id=groceries.category_id,
        monthly_limit=500,
    )

    with pytest.raises(ValueError, match="already has"):
        app.budgets.create_budget(
            category_id=groceries.category_id,
            monthly_limit=600,
        )


def test_income_category_cannot_be_budgeted(
    app,
    category_by_name,
) -> None:
    paycheck = category_by_name("Paycheck", "Income")

    with pytest.raises(ValueError, match="expense categories"):
        app.budgets.create_budget(
            category_id=paycheck.category_id,
            monthly_limit=1000,
        )


def test_budget_progress_reflects_current_month_spending(
    app,
    account_by_name,
    category_by_name,
) -> None:
    checking = account_by_name("Checking")
    groceries = category_by_name("Groceries", "Expense")
    budget = app.budgets.create_budget(
        category_id=groceries.category_id,
        monthly_limit=500,
    )

    app.transactions.create_transaction(
        account_id=checking.account_id,
        category_id=groceries.category_id,
        payee="Market",
        amount=125,
        transaction_date=date.today(),
    )

    progress = app.budgets.get_budget_progress(
        budget,
        month=date.today(),
    )

    assert progress.spent_cents == 12_500
    assert progress.remaining_cents == 37_500
    assert progress.progress_percent == 25
    assert progress.is_overspent is False


def test_budget_marks_category_overspent(
    app,
    account_by_name,
    category_by_name,
) -> None:
    checking = account_by_name("Checking")
    groceries = category_by_name("Groceries", "Expense")
    budget = app.budgets.create_budget(
        category_id=groceries.category_id,
        monthly_limit=100,
    )
    app.transactions.create_transaction(
        account_id=checking.account_id,
        category_id=groceries.category_id,
        payee="Market",
        amount=125,
        transaction_date=date.today(),
    )

    progress = app.budgets.get_budget_progress(
        budget,
        month=date.today(),
    )

    assert progress.is_overspent is True
    assert progress.remaining_cents == -2_500


def test_transfer_does_not_count_against_budget(
    app,
    account_by_name,
    category_by_name,
) -> None:
    checking = account_by_name("Checking")
    savings = account_by_name("Savings")
    groceries = category_by_name("Groceries", "Expense")
    budget = app.budgets.create_budget(
        category_id=groceries.category_id,
        monthly_limit=100,
    )

    app.transactions.create_transfer(
        source_account_id=checking.account_id,
        destination_account_id=savings.account_id,
        amount=75,
        transaction_date=date.today(),
    )

    progress = app.budgets.get_budget_progress(
        budget,
        month=date.today(),
    )

    assert progress.spent_cents == 0


def test_budgets_are_independent_by_calendar_month(
    app,
    category_by_name,
) -> None:
    groceries = category_by_name("Groceries", "Expense")
    january = date(2026, 1, 1)
    february = date(2026, 2, 1)

    january_budget = app.budgets.create_budget(
        category_id=groceries.category_id,
        monthly_limit=500,
        month=january,
    )
    february_budget = app.budgets.create_budget(
        category_id=groceries.category_id,
        monthly_limit=650,
        month=february,
    )

    assert app.budgets.get_budgets(month=january) == [january_budget]
    assert app.budgets.get_budgets(month=february) == [february_budget]


def test_rollover_uses_only_positive_unused_amount(
    app,
    account_by_name,
    category_by_name,
) -> None:
    checking = account_by_name("Checking")
    groceries = category_by_name("Groceries", "Expense")
    january = date(2026, 1, 1)
    february = date(2026, 2, 1)

    january_budget = app.budgets.create_budget(
        category_id=groceries.category_id,
        monthly_limit=500,
        month=january,
    )
    app.transactions.create_transaction(
        account_id=checking.account_id,
        category_id=groceries.category_id,
        payee="Market",
        amount=125,
        transaction_date=date(2026, 1, 15),
    )

    item = app.budgets.get_rollover_items(february)[0]
    assert item.unused_cents == 37_500

    rolled = app.budgets.create_rollover_budget(
        january_budget,
        february,
        item.unused_cents,
    )
    assert rolled.monthly_limit_cents == 87_500
    assert rolled.budget_month == february


def test_copy_previous_month_budgets_copies_regular_limits_and_skips_existing(
    app,
    category_by_name,
) -> None:
    groceries = category_by_name("Groceries", "Expense")
    dining = category_by_name("Restaurants", "Expense")
    january = date(2026, 1, 1)
    february = date(2026, 2, 1)

    app.budgets.create_budget(
        category_id=groceries.category_id,
        monthly_limit=500,
        month=january,
    )
    app.budgets.create_budget(
        category_id=dining.category_id,
        monthly_limit=200,
        month=january,
    )

    existing_february = app.budgets.create_budget(
        category_id=groceries.category_id,
        monthly_limit=650,
        month=february,
    )

    copied_count, skipped_count = (
        app.budgets.copy_previous_month_budgets(february)
    )

    assert copied_count == 1
    assert skipped_count == 1

    february_budgets = {
        budget.category_id: budget
        for budget in app.budgets.get_budgets(month=february)
    }

    assert (
        february_budgets[groceries.category_id].budget_id
        == existing_february.budget_id
    )
    assert (
        february_budgets[groceries.category_id].monthly_limit_cents
        == 65_000
    )
    assert (
        february_budgets[dining.category_id].monthly_limit_cents
        == 20_000
    )


def test_rollover_ledger_prevents_same_budget_from_processing_twice(
    app,
    category_by_name,
) -> None:
    groceries = category_by_name("Groceries", "Expense")
    january = date(2026, 1, 1)
    february = date(2026, 2, 1)

    app.budgets.create_budget(
        category_id=groceries.category_id,
        monthly_limit=500,
        month=january,
    )

    item = app.rollovers.get_available_items(february)[0]

    first_record = app.rollovers.process_choice(
        item=item,
        destination_month=february,
        destination_type="unassigned",
    )

    assert first_record.destination_type == "unassigned"
    assert app.rollovers.get_available_items(february) == []

    with pytest.raises(ValueError, match="already been processed"):
        app.rollovers.process_choice(
            item=item,
            destination_month=february,
            destination_type="unassigned",
        )


def test_rollover_ledger_blocks_duplicate_general_savings_transfer(
    app,
    account_by_name,
    category_by_name,
) -> None:
    groceries = category_by_name("Groceries", "Expense")
    checking = account_by_name("Checking")
    savings = account_by_name("Savings")
    january = date(2026, 1, 1)
    february = date(2026, 2, 1)

    app.budgets.create_budget(
        category_id=groceries.category_id,
        monthly_limit=100,
        month=january,
    )

    item = app.rollovers.get_available_items(february)[0]

    app.rollovers.process_choice(
        item=item,
        destination_month=february,
        destination_type="savings",
        source_account_id=checking.account_id,
        savings_account_id=savings.account_id,
    )

    transfers_after_first = [
        transaction
        for transaction in app.transactions.get_transactions()
        if transaction.is_transfer
    ]
    assert len(transfers_after_first) == 2

    with pytest.raises(ValueError, match="already been processed"):
        app.rollovers.process_choice(
            item=item,
            destination_month=february,
            destination_type="savings",
            source_account_id=checking.account_id,
            savings_account_id=savings.account_id,
        )

    transfers_after_second = [
        transaction
        for transaction in app.transactions.get_transactions()
        if transaction.is_transfer
    ]
    assert len(transfers_after_second) == 2


def test_copy_then_rollover_adds_unused_amount_to_copied_budget(
    app,
    account_by_name,
    category_by_name,
) -> None:
    checking = account_by_name("Checking")
    groceries = category_by_name("Groceries", "Expense")
    january = date(2026, 1, 1)
    february = date(2026, 2, 1)

    app.budgets.create_budget(
        category_id=groceries.category_id,
        monthly_limit=500,
        month=january,
    )
    app.transactions.create_transaction(
        account_id=checking.account_id,
        category_id=groceries.category_id,
        payee="Market",
        amount=350,
        transaction_date=date(2026, 1, 15),
    )

    copied_count, skipped_count = (
        app.budgets.copy_previous_month_budgets(february)
    )
    assert copied_count == 1
    assert skipped_count == 0

    copied = app.budgets.get_budgets(month=february)[0]
    assert copied.monthly_limit_cents == 50_000
    assert copied.origin == "copied"

    item = app.rollovers.get_available_items(february)[0]
    record = app.rollovers.process_choice(
        item=item,
        destination_month=february,
        destination_type="budget",
    )

    rolled = app.budgets.get_budgets(month=february)[0]
    assert rolled.budget_id == copied.budget_id
    assert rolled.monthly_limit_cents == 65_000
    assert rolled.origin == "rollover"
    assert record.result_id == copied.budget_id
    assert app.rollovers.get_available_items(february) == []


def test_rollover_does_not_modify_manual_destination_budget(
    app,
    category_by_name,
) -> None:
    groceries = category_by_name("Groceries", "Expense")
    january = date(2026, 1, 1)
    february = date(2026, 2, 1)

    app.budgets.create_budget(
        category_id=groceries.category_id,
        monthly_limit=500,
        month=january,
    )
    manual_february = app.budgets.create_budget(
        category_id=groceries.category_id,
        monthly_limit=700,
        month=february,
    )

    item = app.rollovers.get_available_items(february)[0]

    with pytest.raises(ValueError, match="Only a budget copied"):
        app.rollovers.process_choice(
            item=item,
            destination_month=february,
            destination_type="budget",
        )

    unchanged = app.budgets.get_budgets(month=february)[0]
    assert unchanged.budget_id == manual_february.budget_id
    assert unchanged.monthly_limit_cents == 70_000
    assert unchanged.origin == "manual"
    assert app.rollovers.get_available_items(february) != []


def test_copy_after_rollover_skips_existing_rollover_budget(
    app,
    category_by_name,
) -> None:
    groceries = category_by_name("Groceries", "Expense")
    january = date(2026, 1, 1)
    february = date(2026, 2, 1)

    app.budgets.create_budget(
        category_id=groceries.category_id,
        monthly_limit=100,
        month=january,
    )

    item = app.rollovers.get_available_items(february)[0]
    app.rollovers.process_choice(
        item=item,
        destination_month=february,
        destination_type="budget",
    )

    before = app.budgets.get_budgets(month=february)[0]
    copied_count, skipped_count = (
        app.budgets.copy_previous_month_budgets(february)
    )
    after = app.budgets.get_budgets(month=february)[0]

    assert copied_count == 0
    assert skipped_count == 1
    assert after.budget_id == before.budget_id
    assert after.monthly_limit_cents == before.monthly_limit_cents
    assert after.origin == "rollover"
