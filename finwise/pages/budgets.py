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

class BudgetsPageMixin:

    def build_budgets(self, parent: tk.Misc) -> None:
        year, month = self._period()
        self.make_page_header(parent, "Budgets", f"Set category limits for {self._month_label(year, month)}")
        card = self.make_card(parent); card.pack(fill="x", pady=(0, 16))
        self._card_title(card, "Monthly budgets", "Edit a limit and save to refresh progress immediately")
        for budget, spent, ratio in budget_progress(self.state, year, month):
            row = tk.Frame(card, bg=self.CARD); row.pack(fill="x", padx=18, pady=6)
            tk.Label(row, text=budget.category, bg=self.CARD, fg=self.INK, width=16, anchor="w", font=("TkDefaultFont", 10, "bold")).pack(side="left")
            limit = tk.StringVar(value=f"{budget.limit:.2f}")
            entry = ttk.Entry(row, textvariable=limit, width=12, style="Finwise.TEntry"); entry.pack(side="left", padx=8)
            tk.Label(row, text=f"spent {self._currency(spent)}", bg=self.CARD, fg=self.MUTED).pack(side="left", padx=8)
            def save(b=budget, var=limit):
                try:
                    value = parse_amount(var.get()); b.limit = value
                    self._flash_message = f"{b.category} budget updated."; self.navigate("Budgets")
                except ValueError as exc: self._flash_message = str(exc); self.navigate("Budgets")
            self.make_button(row, "Save", save, kind="secondary").pack(side="right")
            bar = ttk.Progressbar(card, maximum=1.0, value=min(ratio, 1.0)); bar.pack(fill="x", padx=18, pady=(0, 3))
            tk.Label(card, text="Over budget" if ratio > 1 else f"{ratio:.0%} used", bg=self.CARD, fg=self.CORAL if ratio > 1 else self.EMERALD, font=("TkDefaultFont", 8, "bold")).pack(anchor="e", padx=18)
