"""Compatibility import for the modular Finwise app.

Run ``python main.py`` for the explicit launcher, or keep using
``python finance_app.py`` for backwards compatibility.
"""

from finwise.app import FinanceApp
from finwise.core import (
    Account, AppState, Budget, Category, RecurringPayment, SavingsGoal,
    Transaction, User, add_transaction, authenticate, budget_progress,
    contribute_to_goal, delete_transaction, goal_progress,
    monthly_cashflow_buckets, parse_amount, register_user,
    spending_by_category, totals_for_month,
)


def main() -> None:
    app = FinanceApp()
    app.mainloop()


if __name__ == "__main__":
    main()
