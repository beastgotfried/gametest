"""Dependency-free functional core for the Finwise personal finance demo.

The module intentionally contains no Tk initialization at import time.  The
small data model and pure helpers are used by the GUI as well as by tests.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
import math
from typing import Optional


@dataclass
class Transaction:
    id: str
    type: str  # "income" or "expense"
    amount: float
    category: str
    description: str
    date: str
    account: str


@dataclass
class Category:
    id: str
    name: str
    type: str = "expense"
    color: str = "#2FAE83"


@dataclass
class Budget:
    id: str
    category: str
    limit: float
    month: str = "2026-11"


@dataclass
class SavingsGoal:
    id: str
    name: str
    target: float
    current: float
    deadline: str


@dataclass
class RecurringPayment:
    id: str
    name: str
    amount: float
    due_day: int
    category: str = "Bills"
    active: bool = True
    account: str = "Checking"


@dataclass
class Account:
    id: str
    name: str
    kind: str
    balance: float
    institution: str = ""


@dataclass
class User:
    id: str
    name: str
    email: str
    password: str


@dataclass
class AppState:
    current_user: Optional[User] = None
    users: list[User] = field(default_factory=list)
    transactions: list[Transaction] = field(default_factory=list)
    categories: list[Category] = field(default_factory=list)
    budgets: list[Budget] = field(default_factory=list)
    goals: list[SavingsGoal] = field(default_factory=list)
    recurring_payments: list[RecurringPayment] = field(default_factory=list)
    accounts: list[Account] = field(default_factory=list)
    preferences: dict[str, str] = field(default_factory=dict)

    @classmethod
    def seeded(cls) -> "AppState":
        """Build a fresh, deterministic demo state for November 2026."""
        user = User("user-demo", "Alex Morgan", "demo@finwise.app", "demo123")
        categories = [
            Category("cat-salary", "Salary", "income", "#2FAE83"),
            Category("cat-freelance", "Freelance", "income", "#72C8A5"),
            Category("cat-housing", "Housing", "expense", "#D9776A"),
            Category("cat-food", "Food", "expense", "#E6A56D"),
            Category("cat-transport", "Transport", "expense", "#8B9FE8"),
            Category("cat-bills", "Bills", "expense", "#9A7FC1"),
            Category("cat-shopping", "Shopping", "expense", "#D28BA6"),
        ]
        transactions = [
            Transaction("tx-001", "income", 5200.0, "Salary", "November salary", "2026-11-01", "Checking"),
            Transaction("tx-002", "expense", 1650.0, "Housing", "Rent", "2026-11-02", "Checking"),
            Transaction("tx-003", "expense", 86.40, "Food", "Weekly groceries", "2026-11-03", "Checking"),
            Transaction("tx-004", "expense", 42.50, "Transport", "Metro and rides", "2026-11-04", "Checking"),
            Transaction("tx-005", "expense", 68.00, "Bills", "Utilities", "2026-11-05", "Checking"),
            Transaction("tx-006", "income", 850.0, "Freelance", "Design retainer", "2026-11-06", "Checking"),
            Transaction("tx-007", "expense", 125.75, "Shopping", "Home supplies", "2026-11-07", "Credit Card"),
            Transaction("tx-008", "expense", 54.20, "Food", "Dinner with friends", "2026-11-08", "Credit Card"),
            Transaction("tx-009", "expense", 14.99, "Bills", "Music subscription", "2026-11-09", "Credit Card"),
            Transaction("tx-010", "income", 210.0, "Freelance", "Small project", "2026-10-22", "Checking"),
            Transaction("tx-011", "expense", 1610.0, "Housing", "October rent", "2026-10-02", "Checking"),
            Transaction("tx-012", "expense", 72.15, "Food", "October groceries", "2026-10-12", "Checking"),
            Transaction("tx-013", "income", 4800.0, "Salary", "September salary", "2026-09-01", "Checking"),
            Transaction("tx-014", "expense", 1610.0, "Housing", "September rent", "2026-09-02", "Checking"),
            Transaction("tx-015", "expense", 310.25, "Food", "September groceries", "2026-09-11", "Checking"),
        ]
        return cls(
            current_user=user,
            users=[user],
            transactions=transactions,
            categories=categories,
            budgets=[
                Budget("budget-housing", "Housing", 1800.0),
                Budget("budget-food", "Food", 450.0),
                Budget("budget-transport", "Transport", 200.0),
                Budget("budget-bills", "Bills", 250.0),
                Budget("budget-shopping", "Shopping", 300.0),
            ],
            goals=[
                SavingsGoal("goal-emergency", "Emergency fund", 10000.0, 6400.0, "2027-06-01"),
                SavingsGoal("goal-travel", "Japan trip", 3500.0, 1900.0, "2027-04-15"),
            ],
            recurring_payments=[
                RecurringPayment("rec-rent", "Rent", 1650.0, 2, "Housing"),
                RecurringPayment("rec-music", "Music subscription", 14.99, 9, "Bills"),
                RecurringPayment("rec-cloud", "Cloud storage", 9.99, 18, "Bills", False),
            ],
            accounts=[
                Account("acct-checking", "Checking", "checking", 4250.30, "Northstar Bank"),
                Account("acct-savings", "Savings", "savings", 6400.00, "Northstar Bank"),
                Account("acct-card", "Credit Card", "credit", -820.45, "Summit Card"),
            ],
            preferences={"currency": "USD", "theme": "light", "start_page": "Dashboard", "compact": "false"},
        )


def authenticate(email: str, password: str, users: list[User]) -> Optional[User]:
    for user in users:
        if user.email.strip().lower() == email.strip().lower() and user.password == password:
            return user
    return None


def parse_amount(value: str) -> float:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Amount is required")
    try:
        amount = float(value.replace(",", "").strip())
    except (TypeError, ValueError) as exc:
        raise ValueError("Amount must be numeric") from exc
    if not math.isfinite(amount) or amount <= 0:
        raise ValueError("Amount must be positive")
    return amount


def _in_month(tx: Transaction, year: int, month: int) -> bool:
    try:
        parsed = date.fromisoformat(tx.date[:10])
    except (TypeError, ValueError):
        return False
    return parsed.year == year and parsed.month == month


def totals_for_month(state: AppState, year: int, month: int) -> tuple[float, float]:
    income = sum(tx.amount for tx in state.transactions if tx.type == "income" and _in_month(tx, year, month))
    expenses = sum(tx.amount for tx in state.transactions if tx.type == "expense" and _in_month(tx, year, month))
    return income, expenses


def spending_by_category(state: AppState, year: int, month: int) -> list[tuple[str, float]]:
    totals: dict[str, float] = {}
    for tx in state.transactions:
        if tx.type == "expense" and _in_month(tx, year, month):
            totals[tx.category] = totals.get(tx.category, 0.0) + tx.amount
    return sorted(totals.items(), key=lambda item: (-item[1], item[0]))


def budget_progress(state: AppState, year: int, month: int) -> list[tuple[Budget, float, float]]:
    spent_by_category = dict(spending_by_category(state, year, month))
    result = []
    for budget in state.budgets:
        spent = spent_by_category.get(budget.category, 0.0)
        ratio = spent / budget.limit if budget.limit > 0 else 0.0
        result.append((budget, spent, ratio))
    return result


def monthly_cashflow_buckets(
    state: AppState,
    months: int = 6,
    end_date: date | datetime | str | None = None,
) -> list[tuple[str, float, float]]:
    """Return chronological ``(YYYY-MM, income, expenses)`` chart buckets."""
    if months < 1:
        return []
    if end_date is None:
        end = max((date.fromisoformat(tx.date[:10]) for tx in state.transactions), default=date.today())
    elif isinstance(end_date, datetime):
        end = end_date.date()
    elif isinstance(end_date, date):
        end = end_date
    else:
        end = date.fromisoformat(str(end_date)[:10])
    # Anchor on the first day of the ending month, then walk backwards.
    cursor = end.replace(day=1)
    buckets: list[tuple[str, float, float]] = []
    for offset in range(months - 1, -1, -1):
        month_index = cursor.year * 12 + cursor.month - 1 - offset
        year, month_zero_based = divmod(month_index, 12)
        month = month_zero_based + 1
        income, expenses = totals_for_month(state, year, month)
        buckets.append((f"{year:04d}-{month:02d}", income, expenses))
    return buckets


def goal_progress(goal: SavingsGoal) -> float:
    if goal.target <= 0:
        return 1.0 if goal.current > 0 else 0.0
    return max(0.0, min(1.0, goal.current / goal.target))


def add_transaction(
    state: AppState,
    type: str,
    amount: float,
    category: str,
    description: str,
    date: str,
    account: str,
) -> Transaction:
    if type not in {"income", "expense"}:
        raise ValueError("Transaction type must be income or expense")
    amount = parse_amount(str(amount))
    try:
        datetime.strptime(date[:10], "%Y-%m-%d")
    except (TypeError, ValueError) as exc:
        raise ValueError("Date must use YYYY-MM-DD") from exc
    used_ids = {tx.id for tx in state.transactions}
    numeric_ids = []
    for used_id in used_ids:
        if used_id.startswith("tx-") and used_id[3:].isdigit():
            numeric_ids.append(int(used_id[3:]))
    sequence = max(numeric_ids, default=0) + 1
    while f"tx-{sequence:03d}" in used_ids:
        sequence += 1
    tx = Transaction(f"tx-{sequence:03d}", type, amount, category, description, date[:10], account)
    state.transactions.append(tx)
    return tx


def delete_transaction(state: AppState, transaction_id: str) -> bool:
    for index, tx in enumerate(state.transactions):
        if tx.id == transaction_id:
            del state.transactions[index]
            return True
    return False


def register_user(state: AppState, name: str, email: str, password: str) -> User:
    if not name.strip() or not email.strip() or not password:
        raise ValueError("Name, email, and password are required")
    if any(user.email.lower() == email.strip().lower() for user in state.users):
        raise ValueError("Email is already registered")
    user = User(f"user-{len(state.users) + 1:03d}", name.strip(), email.strip(), password)
    state.users.append(user)
    state.current_user = user
    return user


def contribute_to_goal(goal: SavingsGoal, amount: float) -> None:
    goal.current += parse_amount(str(amount))


if __name__ == "__main__":
    # The Tk shell is added in a later task.  Keeping this entry point inert
    # makes the functional core safe to import and useful on headless systems.
    pass
