# Envelopes behavior test suite

This suite was written against the exact source code in `Envelopes(12).zip`.
It tests user-facing backend workflows rather than standalone model internals.

## Install

1. Extract `envelopes_behavior_test_suite.zip`.
2. Open the extracted folder.
3. Copy the entire `tests` folder into the root of your Envelopes project.
4. Copy `pytest.ini` and `requirements-test.txt` into the same root folder.

The result should look like:

```text
Envelopes/
├── core/
├── data/
├── gui/
├── models/
├── repositories/
├── services/
├── tests/
│   ├── conftest.py
│   ├── test_account_actions.py
│   ├── test_budget_actions.py
│   ├── test_category_actions.py
│   ├── test_reports_dashboard_actions.py
│   ├── test_savings_goal_actions.py
│   ├── test_transaction_actions.py
│   └── test_transfer_actions.py
├── main.py
├── pytest.ini
└── requirements-test.txt
```

## Install pytest

From the project root:

```powershell
py -m pip install -r requirements-test.txt
```

## Run every test

```powershell
py -m pytest -v
```

## Run one workflow area

```powershell
py -m pytest tests/test_transaction_actions.py -v
```

## Run coverage

```powershell
py -m pytest --cov=services --cov=repositories --cov-report=term-missing
```

The tests create temporary JSON files. They do not modify the real files in
your `data` folder.
