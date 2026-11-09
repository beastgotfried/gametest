from __future__ import annotations

from datetime import date, datetime
import math
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Optional

from ..core import (
    Account, AppState, Budget, Category, RecurringPayment, SavingsGoal,
    add_transaction, budget_progress, contribute_to_goal, delete_transaction,
    goal_progress, monthly_cashflow_buckets, parse_amount,
    spending_by_category, totals_for_month,
)

class AnalyticsPageMixin:

    def build_analytics(self, parent: tk.Misc) -> None:
        year,month=self._period(); self.make_page_header(parent,"Analytics","Spot useful patterns in your recent activity")
        buckets=monthly_cashflow_buckets(self.state,6); card=self.make_card(parent); card.pack(fill="x",pady=(0,16)); self._card_title(card,"Six-month cash flow","Income and expenses by month")
        self._draw_bar_chart(card,[(label,income) for label,income,_ in buckets],colour=self.EMERALD)
        cat=self.make_card(parent); cat.pack(fill="x",pady=(0,16)); self._card_title(cat,"Top spending categories"); self._draw_bar_chart(cat,spending_by_category(self.state,year,month)[:5],colour=self.CORAL)
        income,expenses=totals_for_month(self.state,year,month); insights=[f"You earned {self._currency(income)} this month.",f"You spent {self._currency(expenses)} across {len(spending_by_category(self.state,year,month))} categories.","Keep an eye on categories approaching their budget limits."]
        for text in insights: tk.Label(parent,text="• "+text,bg=self.CONTENT,fg=self.INK,anchor="w",font=("TkDefaultFont",10)).pack(fill="x",pady=3)
