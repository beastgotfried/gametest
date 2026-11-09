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

class ReportsPageMixin:

    def build_reports(self, parent: tk.Misc) -> None:
        year,month=self._period(); income,expenses=totals_for_month(self.state,year,month); self.make_page_header(parent,"Reports",f"Cash flow for {self._month_label(year,month)}")
        card=self.make_card(parent); card.pack(fill="x",pady=(0,16)); self._card_title(card,"Income versus expenses"); self._draw_bar_chart(card,[("Income",income),("Expenses",expenses)],colour=self.EMERALD)
        net=income-expenses; tk.Label(parent,text=f"Net cash flow: {self._currency(net)}",bg=self.MINT if net>=0 else "#FCE8E5",fg=self.EMERALD if net>=0 else self.CORAL,font=("TkDefaultFont",14,"bold"),padx=16,pady=12).pack(fill="x")
