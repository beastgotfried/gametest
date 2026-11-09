from finance_app import (
    AppState,
    SavingsGoal,
    add_transaction,
    authenticate,
    budget_progress,
    delete_transaction,
    goal_progress,
    parse_amount,
    monthly_cashflow_buckets,
    register_user,
    spending_by_category,
    totals_for_month,
)
import pytest


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
    for value in ("nan", "inf", "-inf"):
        with pytest.raises(ValueError):
            parse_amount(value)


def test_seeded_state_spans_three_months_and_has_chart_buckets():
    state = AppState.seeded()
    buckets = monthly_cashflow_buckets(state, months=3, end_date="2026-11-30")
    assert [bucket[0] for bucket in buckets] == ["2026-09", "2026-10", "2026-11"]
    assert all(income >= 0 and expenses >= 0 for _, income, expenses in buckets)


def test_month_totals_and_category_spending_are_derived_from_transactions():
    state = AppState.seeded()
    income, expenses = totals_for_month(state, 2026, 11)
    assert income > 0
    assert expenses > 0
    categories = spending_by_category(state, 2026, 11)
    assert categories[0][1] >= categories[-1][1]


def test_budget_progress_reports_spent_and_ratio():
    state = AppState.seeded()
    budget, spent, ratio = budget_progress(state, 2026, 11)[0]
    assert budget.category == "Housing"
    assert spent == 1650.0
    assert ratio == pytest.approx(1650 / 1800)


def test_goal_progress_is_clamped():
    goal = SavingsGoal("g", "Emergency fund", 1000.0, 1200.0, "2027-01-01")
    assert goal_progress(goal) == 1.0


def test_adding_expense_changes_month_total_and_delete_restores_it():
    state = AppState.seeded()
    before = totals_for_month(state, 2026, 11)[1]
    tx = add_transaction(state, "expense", 42.0, "Dining", "Test lunch", "2026-11-09", "Checking")
    assert totals_for_month(state, 2026, 11)[1] == before + 42.0
    assert delete_transaction(state, tx.id) is True
    assert totals_for_month(state, 2026, 11)[1] == before


def test_registered_user_is_session_only():
    state = AppState.seeded()
    user = register_user(state, "Taylor Reed", "taylor@example.com", "secret1")
    assert user in state.users
    assert state.current_user is user
    assert authenticate("taylor@example.com", "secret1", state.users) is user


def test_added_transaction_id_does_not_collide_after_deletion():
    state = AppState.seeded()
    delete_transaction(state, "tx-015")
    tx = add_transaction(state, "expense", 9, "Food", "Snack", "2026-11-09", "Checking")
    assert tx.id == "tx-015"
    delete_transaction(state, "tx-001")
    replacement = add_transaction(state, "expense", 10, "Food", "Snack", "2026-11-09", "Checking")
    assert replacement.id != "tx-001"
