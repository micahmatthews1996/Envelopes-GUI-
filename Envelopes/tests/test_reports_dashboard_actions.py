from datetime import date


def test_reports_show_income_expense_cash_flow_and_transaction_count(
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
        amount=2000,
        transaction_date=date.today(),
    )
    app.transactions.create_transaction(
        account_id=checking.account_id,
        category_id=groceries.category_id,
        payee="Market",
        amount=500,
        transaction_date=date.today(),
    )

    summary = app.reports.get_monthly_summary(
        date.today()
    )

    assert summary.total_income_cents == 200_000
    assert summary.total_expense_cents == 50_000
    assert summary.net_cash_flow_cents == 150_000
    assert summary.transaction_count == 2


def test_reports_exclude_transfers_from_totals_and_month_list(
    app,
    account_by_name,
) -> None:
    checking = account_by_name("Checking")
    savings = account_by_name("Savings")

    app.transactions.create_transfer(
        source_account_id=checking.account_id,
        destination_account_id=savings.account_id,
        amount=300,
        transaction_date=date(2024, 1, 15),
    )

    summary = app.reports.get_monthly_summary(
        date(2024, 1, 1)
    )

    assert summary.total_income_cents == 0
    assert summary.total_expense_cents == 0
    assert summary.transaction_count == 0
    assert date(2024, 1, 1) not in (
        app.reports.get_available_months()
    )


def test_category_spending_excludes_income_and_transfers(
    app,
    account_by_name,
    category_by_name,
) -> None:
    checking = account_by_name("Checking")
    savings = account_by_name("Savings")
    paycheck = category_by_name("Paycheck", "Income")
    groceries = category_by_name("Groceries", "Expense")

    app.transactions.create_transaction(
        account_id=checking.account_id,
        category_id=paycheck.category_id,
        payee="Employer",
        amount=1000,
        transaction_date=date.today(),
    )
    app.transactions.create_transaction(
        account_id=checking.account_id,
        category_id=groceries.category_id,
        payee="Market",
        amount=200,
        transaction_date=date.today(),
    )
    app.transactions.create_transfer(
        source_account_id=checking.account_id,
        destination_account_id=savings.account_id,
        amount=100,
        transaction_date=date.today(),
    )

    items = app.reports.get_category_spending(
        date.today()
    )

    assert [(item.category_name, item.amount_cents) for item in items] == [
        ("Groceries", 20_000)
    ]


def test_dashboard_net_worth_and_recent_transactions_update(
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
    )
    app.transactions.create_transaction(
        account_id=checking.account_id,
        category_id=groceries.category_id,
        payee="Market",
        amount=100,
        transaction_date=date.today(),
    )

    dashboard = app.dashboard.get_dashboard_summary()

    assert dashboard.net_worth_cents == 90_000
    assert dashboard.total_income_cents == 100_000
    assert dashboard.total_expense_cents == 10_000
    assert len(dashboard.recent_transactions) == 2


def test_dashboard_should_exclude_transfers_from_income_and_expenses(
    app,
    account_by_name,
) -> None:
    checking = account_by_name("Checking")
    savings = account_by_name("Savings")

    app.transactions.create_transfer(
        source_account_id=checking.account_id,
        destination_account_id=savings.account_id,
        amount=300,
        transaction_date=date.today(),
    )

    dashboard = app.dashboard.get_dashboard_summary()

    assert dashboard.total_income_cents == 0
    assert dashboard.total_expense_cents == 0


def test_dashboard_should_identify_savings_by_account_type_after_rename(
    app,
    account_by_name,
) -> None:
    checking = account_by_name("Checking")
    savings = account_by_name("Savings")

    app.accounts.update_account(
        account_id=savings.account_id,
        name="High Yield Account",
        account_type="Savings",
        opening_balance=0,
    )
    renamed_savings = next(
        account
        for account in app.accounts.get_accounts()
        if account.account_id == savings.account_id
    )

    app.transactions.create_transfer(
        source_account_id=checking.account_id,
        destination_account_id=renamed_savings.account_id,
        amount=400,
        transaction_date=date.today(),
    )

    dashboard = app.dashboard.get_dashboard_summary()

    assert dashboard.total_savings_cents == 40_000
