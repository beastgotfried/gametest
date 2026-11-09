# Personal Finance Tkinter Demo Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a polished, dependency-free Tkinter personal finance demo with seeded authentication, 15 navigable pages, and in-memory interactions.

**Architecture:** Keep the runtime in one top-level `finance_app.py` with dataclasses for demo data, pure helpers for calculations, and a `FinanceApp` controller that renders authenticated pages into a shared content frame. Use `tkinter.ttk` for layout and controls and `Canvas` for charts; no persistence or external services.

**Tech Stack:** Python 3.11+, `tkinter`, `tkinter.ttk`, `dataclasses`, `datetime`, `unittest` or pytest-compatible tests.

**Spec:** `docs/superpowers/specs/2026-11-09-personal-finance-demo-design.md`

## Global Constraints

- Keep the runtime dependency-free beyond Python's standard library.
- Store all app data in memory and reset it on process restart.
- Use seeded credentials `demo@finwise.app` / `demo123`.
- Keep all 15 pages reachable from the authenticated navigation rail.
- Use the graphite, cool-white, emerald, and coral visual tokens from the spec.
- Keep the minimum window size at 1180 by 760 and support window resizing.
- Never let normal form errors terminate the Tk process; show inline feedback.

---

### Task 1: Functional core and tests

**Files:**
- Create: `tests/test_finance_app.py`
- Create: `finance_app.py`

**Interfaces:**
- `Transaction`, `Category`, `Budget`, `SavingsGoal`, `RecurringPayment`, `Account`, and `User` dataclasses.
- `AppState.seeded()` returns a complete demo state.
- `authenticate(email: str, password: str, users: list[User]) -> User | None`.
- `parse_amount(value: str) -> float` raises `ValueError` for blank, non-numeric, or non-positive values.
- `totals_for_month(state: AppState, year: int, month: int) -> tuple[float, float]` returns income and expense totals.
- `spending_by_category(state: AppState, year: int, month: int) -> list[tuple[str, float]]` returns descending expense totals.
- `budget_progress(state: AppState, year: int, month: int) -> list[tuple[Budget, float, float]]` returns each budget with spent amount and ratio.
- `goal_progress(goal: SavingsGoal) -> float` returns a clamped 0.0 to 1.0 ratio.

- [ ] **Step 1: Write failing tests for seeded auth and validation**

```python
def test_seeded_login_accepts_demo_credentials():
    state = AppState.seeded()
    assert authenticate("demo@finwise.app", "demo123", state.users).name == "Alex Morgan"

def test_auth_rejects_wrong_password():
    state = AppState.seeded()
    assert authenticate("demo@finwise.app", "wrong", state.users) is None

def test_parse_amount_requires_positive_number():
    with pytest.raises(ValueError):
        parse_amount("0")
    assert parse_amount("1,250.50") == 1250.50
```

- [ ] **Step 2: Run the focused tests and confirm they fail because `finance_app.py` is absent**

Run: `python -m pytest tests/test_finance_app.py -q`

Expected: collection failure mentioning the missing `finance_app` module.

- [ ] **Step 3: Add the dataclasses, seeded state, authentication, and amount parser**

Implement all data classes with simple fields, `AppState.seeded()` with three accounts, at least 10 transactions, categories, budgets, goals, recurring payments, and preferences, plus the exact helper signatures in the Interfaces section.

- [ ] **Step 4: Run the focused tests and confirm the auth and parser tests pass**

Run: `python -m pytest tests/test_finance_app.py -q`

- [ ] **Step 5: Add failing tests for totals, category aggregation, budget progress, goal progress, and mutation helpers**

```python
def test_month_totals_and_category_spending_are_derived_from_transactions():
    state = AppState.seeded()
    income, expenses = totals_for_month(state, 2026, 11)
    assert income > 0
    assert expenses > 0
    assert spending_by_category(state, 2026, 11)[0][1] >= spending_by_category(state, 2026, 11)[-1][1]

def test_goal_progress_is_clamped():
    goal = SavingsGoal("g", "Emergency fund", 1000.0, 1200.0, "2027-01-01")
    assert goal_progress(goal) == 1.0
```

- [ ] **Step 6: Run the tests and confirm the new tests fail for missing helpers**

Run: `python -m pytest tests/test_finance_app.py -q`

- [ ] **Step 7: Implement pure calculation and mutation helpers**

Implement `totals_for_month`, `spending_by_category`, `budget_progress`, and `goal_progress`. Add small helpers for adding and deleting transactions and for registering a session-only user so the UI can call real behavior without duplicating business logic.

- [ ] **Step 8: Run the full core test file and commit the functional core**

Run: `python -m pytest tests/test_finance_app.py -q`

Commit: `git add finance_app.py tests/test_finance_app.py && git commit -m "feat: add finance demo data core"`

### Task 2: Tk shell, authentication, and reusable visual primitives

**Files:**
- Modify: `finance_app.py`

**Interfaces:**
- `FinanceApp(tk.Tk)` owns `state`, `current_user`, `active_page`, `show_login`, `show_register`, `show_shell`, and `navigate(page_name)`.
- Shared methods include `clear_root`, `make_button`, `make_card`, `make_page_header`, `make_form_field`, `show_inline_message`, and `build_shell`.

- [ ] **Step 1: Add failing controller tests that do not require a display**

```python
def test_registered_user_is_session_only():
    state = AppState.seeded()
    user = register_user(state, "Taylor Reed", "taylor@example.com", "secret1")
    assert user in state.users
    assert authenticate("taylor@example.com", "secret1", state.users) is user
```

- [ ] **Step 2: Run the test and confirm registration behavior is missing**

Run: `python -m pytest tests/test_finance_app.py::test_registered_user_is_session_only -q`

- [ ] **Step 3: Implement registration helper and the root controller skeleton**

Create the app with `self.minsize(1180, 760)`, configure the color palette and ttk styles, keep the current state in memory, and render the login screen first. Add a `main()` guarded by `if __name__ == "__main__":`.

- [ ] **Step 4: Build the login and register screens**

Use clear labels, prefill the demo email, show the demo credentials in a small helper panel, validate inline, and provide links between login and registration. Successful login enters the shell at Dashboard.

- [ ] **Step 5: Build the authenticated shell and navigation rail**

Render the fixed-width graphite rail, grouped nav items for all pages, the top bar with user initials and logout, and a scrollable content frame. Apply one consistent radius and accent color through ttk styles and custom canvas panels.

- [ ] **Step 6: Run the app manually and verify login, registration, logout, and resize behavior**

Run: `python finance_app.py`

Verify the window opens, `demo@finwise.app` / `demo123` reaches Dashboard, invalid login stays on Login, registration reaches Dashboard, Logout returns to Login, and resizing does not overlap the shell.

- [ ] **Step 7: Commit shell and auth**

Commit: `git add finance_app.py tests/test_finance_app.py && git commit -m "feat: add finance app shell and auth"`

### Task 3: Dashboard and core money pages

**Files:**
- Modify: `finance_app.py`

**Interfaces:**
- Page builders: `build_dashboard`, `build_profile`, `build_transactions`, `build_add_transaction(kind)`, `build_categories`, and `build_accounts`.

- [ ] **Step 1: Add tests for transaction mutations and totals updating**

```python
def test_adding_expense_changes_month_total_and_delete_restores_it():
    state = AppState.seeded()
    before = totals_for_month(state, 2026, 11)[1]
    tx = add_transaction(state, "expense", 42.0, "Dining", "Test lunch", "2026-11-09", "Checking")
    assert totals_for_month(state, 2026, 11)[1] == before + 42.0
    delete_transaction(state, tx.id)
    assert totals_for_month(state, 2026, 11)[1] == before
```

- [ ] **Step 2: Run the test and confirm the mutation helper is missing or incomplete**

Run: `python -m pytest tests/test_finance_app.py::test_adding_expense_changes_month_total_and_delete_restores_it -q`

- [ ] **Step 3: Implement the dashboard and transaction pages**

Dashboard should show four metric cards, a recent-transactions table, a budget progress panel, and a spending-by-category bar chart. Transactions should include a filter row, type-colored rows, delete buttons, and links to Add Income and Add Expense.

- [ ] **Step 4: Implement Add Income and Add Expense forms**

Use the same builder with an income/expense mode. Validate date, amount, category, account, and description, then append to state and navigate to Transactions with a saved message.

- [ ] **Step 5: Implement Profile, Categories, and Accounts**

Profile updates name and contact fields. Categories adds and deletes safe categories. Accounts adds and deletes with confirmation while preventing deletion of the final account.

- [ ] **Step 6: Run the app and exercise the core money flows**

Add one income and one expense, filter Transactions, delete one row, add a category, update profile, add an account, and confirm the Dashboard totals change immediately.

- [ ] **Step 7: Commit core money pages**

Commit: `git add finance_app.py tests/test_finance_app.py && git commit -m "feat: add dashboard and money pages"`

### Task 4: Planning, recurring payments, reports, analytics, and settings

**Files:**
- Modify: `finance_app.py`

**Interfaces:**
- Page builders: `build_budgets`, `build_savings_goals`, `build_recurring_payments`, `build_reports`, `build_analytics`, and `build_settings`.
- Chart helpers: `draw_bar_chart`, `draw_line_chart`, and `draw_donut_chart`.

- [ ] **Step 1: Add tests for budget and savings-goal updates**

```python
def test_budget_update_and_goal_contribution_are_reflected_in_helpers():
    state = AppState.seeded()
    budget = state.budgets[0]
    budget.limit = 999.0
    assert budget_progress(state, 2026, 11)[0][0].limit == 999.0
    goal = state.goals[0]
    starting = goal.current
    contribute_to_goal(goal, 25.0)
    assert goal.current == starting + 25.0
```

- [ ] **Step 2: Run the test and confirm the helper behavior is missing**

Run: `python -m pytest tests/test_finance_app.py::test_budget_update_and_goal_contribution_are_reflected_in_helpers -q`

- [ ] **Step 3: Implement planning pages**

Budgets shows current-month category limits, spent amounts, and progress bars with editable limits. Savings Goals shows progress cards, deadlines, create-goal form, and contribution action. Recurring Payments shows active and paused subscriptions with add and toggle actions.

- [ ] **Step 4: Implement Reports and Analytics with Canvas charts**

Reports shows income versus expenses for the selected month and a net cash-flow callout. Analytics shows six-month trend lines, category bars, and three plain-language insights derived from current data. Charts must resize with their host frame and use the emerald/coral palette.

- [ ] **Step 5: Implement Settings**

Settings includes currency selection, start-page selection, compact-mode preference, and a save confirmation. Theme is displayed as the fixed demo theme and is not changed by the controls.

- [ ] **Step 6: Run a page-by-page smoke pass**

Run: `python finance_app.py`

Navigate through all 15 pages, confirm every nav item renders without an exception, create a goal, contribute to it, edit a budget, toggle a recurring payment, and check both chart pages after adding a transaction.

- [ ] **Step 7: Commit all page builders**

Commit: `git add finance_app.py tests/test_finance_app.py && git commit -m "feat: complete finance demo pages"`

### Task 5: Documentation, static checks, and delivery

**Files:**
- Modify: `README.md`
- Modify: `finance_app.py` only if verification finds a bug

- [ ] **Step 1: Add launch instructions and seeded credentials to README**

Document `python finance_app.py`, the demo email/password, the in-memory reset behavior, and the supported Python version.

- [ ] **Step 2: Run automated tests and syntax checks**

Run: `python -m pytest -q` and `python -m py_compile finance_app.py`.

- [ ] **Step 3: Run the manual GUI smoke pass**

Open the app, verify all 15 pages, check the main actions, resize the window, and use Logout. Capture any exception and fix it with a focused regression test before proceeding.

- [ ] **Step 4: Inspect git diff and verify no unrelated files changed**

Run: `git status --short` and `git diff --check`.

- [ ] **Step 5: Commit documentation and final verification**

Commit: `git add README.md && git commit -m "docs: add finance demo run instructions"`

