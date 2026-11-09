# Documentation QA report

## Scope

Reviewed the personal finance demo documentation in `README.md` and added a
focused regression test for its launch command and seeded credentials.

## Changes

- Added a clearly labeled **Personal finance demo** section.
- Documented the Python 3.11+ requirement and `python finance_app.py` launch
  command.
- Documented the seeded login (`demo@finwise.app` / `demo123`).
- Documented that state is held in memory and resets when the process restarts.
- Listed all 15 pages: Login, Register, Dashboard, Profile, Transactions, Add
  Income, Add Expense, Categories, Accounts, Budgets, Savings Goals, Recurring
  Payments, Reports, Analytics, and Settings.
- Added `tests/test_readme_finance.py` to protect the launch and credential
  documentation.

## Verification

Ran the repository test suite with `python -m pytest -q`.

Result: **11 passed**.

The bare `pytest -q` executable reports an environment-specific
`ModuleNotFoundError` for the top-level `finance_app` module; invoking pytest
through the active Python interpreter avoids that path issue.

## Concerns

No documentation concerns identified. `finance_app.py` was not modified as
part of this documentation task. The bare `pytest` path issue is unrelated to
the README changes.
