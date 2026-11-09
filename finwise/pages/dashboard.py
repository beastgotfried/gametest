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

class DashboardPageMixin:

    def build_dashboard(self, parent: tk.Misc) -> None:
        year, month = self._period()
        self.make_page_header(parent, "Dashboard", f"A quick read on your money in {self._month_label(year, month)}")
        income, expenses = totals_for_month(self.state, year, month)
        total_balance = sum(account.balance for account in self.state.accounts)
        metrics = (
            ("Income", income, self.EMERALD, self._currency(income)),
            ("Expenses", expenses, self.CORAL, self._currency(expenses)),
            ("Net cash flow", income - expenses, self.EMERALD if income >= expenses else self.CORAL, self._currency(income - expenses)),
            ("Total balance", total_balance, self.INK, self._currency(total_balance)),
        )
        metrics_row = tk.Frame(parent, bg=self.CONTENT)
        metrics_row.pack(fill="x", pady=(0, 18))
        for index in range(4):
            metrics_row.columnconfigure(index, weight=1)
        for index, (label, _value, colour, text) in enumerate(metrics):
            card = self.make_card(metrics_row)
            card.grid(row=0, column=index, sticky="nsew", padx=(0 if index == 0 else 6, 0 if index == 3 else 6))
            tk.Label(card, text=label.upper(), bg=self.CARD, fg=self.MUTED, font=("TkDefaultFont", 8, "bold")).pack(anchor="w", padx=16, pady=(15, 5))
            tk.Label(card, text=text, bg=self.CARD, fg=colour, font=("TkDefaultFont", 17, "bold")).pack(anchor="w", padx=16, pady=(0, 16))

        lower = tk.Frame(parent, bg=self.CONTENT)
        lower.pack(fill="x", pady=(0, 16))
        lower.columnconfigure(0, weight=3)
        lower.columnconfigure(1, weight=2)
        recent = self.make_card(lower)
        recent.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self._card_title(recent, "Recent transactions", "The latest activity across your accounts")
        for tx in sorted(self.state.transactions, key=lambda item: item.date, reverse=True)[:6]:
            row = tk.Frame(recent, bg=self.CARD)
            row.pack(fill="x", padx=18, pady=5)
            marker = self.EMERALD if tx.type == "income" else self.CORAL
            tk.Label(row, text="●", bg=self.CARD, fg=marker, font=("TkDefaultFont", 9)).pack(side="left", padx=(0, 8))
            detail = tk.Frame(row, bg=self.CARD)
            detail.pack(side="left", fill="x", expand=True)
            tk.Label(detail, text=tx.description, bg=self.CARD, fg=self.INK, font=("TkDefaultFont", 10)).pack(anchor="w")
            tk.Label(detail, text=f"{tx.category} · {tx.date[:10]}", bg=self.CARD, fg=self.MUTED, font=("TkDefaultFont", 8)).pack(anchor="w")
            tk.Label(row, text=f"{'+' if tx.type == 'income' else '-'}{self._currency(tx.amount)}", bg=self.CARD, fg=marker, font=("TkDefaultFont", 10, "bold")).pack(side="right")
        if not self.state.transactions:
            tk.Label(recent, text="Add your first income or expense to see it here.", bg=self.CARD, fg=self.MUTED).pack(anchor="w", padx=18, pady=(8, 22))

        budget_card = self.make_card(lower)
        budget_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        self._card_title(budget_card, "Budget pulse", f"{self._month_label(year, month)} category limits")
        for budget, spent, ratio in budget_progress(self.state, year, month)[:5]:
            colour = self.CORAL if ratio > 1 else self.EMERALD
            tk.Label(budget_card, text=f"{budget.category}  ·  {self._currency(spent)} / {self._currency(budget.limit)}", bg=self.CARD, fg=self.INK, font=("TkDefaultFont", 9)).pack(fill="x", padx=18, pady=(4, 2))
            bar = ttk.Progressbar(budget_card, maximum=1.0, value=min(ratio, 1.0))
            bar.pack(fill="x", padx=18, pady=(0, 5))
            tk.Label(budget_card, text="Over budget" if ratio > 1 else f"{ratio:.0%} used", bg=self.CARD, fg=colour, font=("TkDefaultFont", 8, "bold")).pack(anchor="e", padx=18)
        if not self.state.budgets:
            tk.Label(budget_card, text="No budgets yet.", bg=self.CARD, fg=self.MUTED).pack(anchor="w", padx=18, pady=(5, 20))

        chart_card = self.make_card(parent)
        chart_card.pack(fill="x", pady=(0, 16))
        self._card_title(chart_card, "Spending by category", f"Where {self._month_label(year, month)} expenses are going")
        self._draw_bar_chart(chart_card, spending_by_category(self.state, year, month)[:6], colour=self.CORAL)
