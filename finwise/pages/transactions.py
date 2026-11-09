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

class TransactionsPageMixin:

    def build_transactions(self, parent: tk.Misc) -> None:
        year, month = self._period()
        self.make_page_header(parent, "Transactions", "Search, filter, and manage every money movement")
        if getattr(self, "_flash_message", ""):
            host = tk.Frame(parent, bg=self.CONTENT)
            host.pack(fill="x")
            tk.Label(host, text=self._flash_message, bg=self.CONTENT, fg=self.EMERALD, font=("TkDefaultFont", 10, "bold")).pack(anchor="w", pady=(0, 12))
            self._flash_message = ""
        actions = tk.Frame(parent, bg=self.CONTENT)
        actions.pack(fill="x", pady=(0, 14))
        self._action_link(actions, "＋ Add income", lambda: self.navigate("Add Income"))
        self._action_link(actions, "＋ Add expense", lambda: self.navigate("Add Expense"))
        filters = self.make_card(parent)
        filters.pack(fill="x", pady=(0, 12))
        filter_body = tk.Frame(filters, bg=self.CARD)
        filter_body.pack(fill="x", padx=16, pady=14)
        type_var = tk.StringVar(value="All types")
        category_var = tk.StringVar(value="All categories")
        tk.Label(filter_body, text="Type", bg=self.CARD, fg=self.MUTED, font=("TkDefaultFont", 9, "bold")).pack(side="left", padx=(0, 6))
        type_box = ttk.Combobox(filter_body, textvariable=type_var, state="readonly", values=("All types", "Income", "Expense"), width=14, style="Finwise.TCombobox")
        type_box.pack(side="left", padx=(0, 20))
        tk.Label(filter_body, text="Category", bg=self.CARD, fg=self.MUTED, font=("TkDefaultFont", 9, "bold")).pack(side="left", padx=(0, 6))
        category_values = ["All categories"] + sorted({tx.category for tx in self.state.transactions})
        category_box = ttk.Combobox(filter_body, textvariable=category_var, state="readonly", values=category_values, width=18, style="Finwise.TCombobox")
        category_box.pack(side="left")
        table = self.make_card(parent)
        table.pack(fill="x")
        header = tk.Frame(table, bg=self.MINT)
        header.pack(fill="x", padx=1, pady=1)
        columns = (("Date", 12), ("Description", 28), ("Category", 18), ("Account", 18), ("Amount", 16), ("", 8))
        for title, width in columns:
            tk.Label(header, text=title.upper(), bg=self.MINT, fg=self.INK, font=("TkDefaultFont", 8, "bold"), width=width, anchor="w").pack(side="left", padx=8, pady=8)
        rows_host = tk.Frame(table, bg=self.CARD)
        rows_host.pack(fill="x", padx=1, pady=(0, 1))

        def render_rows(*_args) -> None:
            for child in rows_host.winfo_children():
                child.destroy()
            selected_type = type_var.get().lower()
            selected_category = category_var.get()
            rows = [tx for tx in sorted(self.state.transactions, key=lambda item: item.date, reverse=True) if (selected_type in {"all types", tx.type}) and (selected_category == "All categories" or tx.category == selected_category)]
            for index, tx in enumerate(rows):
                row = tk.Frame(rows_host, bg="#FBFCFB" if index % 2 == 0 else self.CARD)
                row.pack(fill="x")
                colour = self.EMERALD if tx.type == "income" else self.CORAL
                values = (tx.date[:10], tx.description[:28], tx.category, tx.account, f"{'+' if tx.type == 'income' else '-'}{self._currency(tx.amount)}")
                for (value, (_title, width)) in zip(values, columns[:-1]):
                    tk.Label(row, text=value, bg=row["bg"], fg=colour if value == values[-1] else self.INK, font=("TkDefaultFont", 9, "bold" if value == values[-1] else "normal"), width=width, anchor="w").pack(side="left", padx=8, pady=9)
                self.make_button(row, "Delete", lambda tx_id=tx.id: self._delete_transaction_from_page(tx_id), kind="secondary").pack(side="left", padx=8, pady=4)
            if not rows:
                tk.Label(rows_host, text="No transactions match those filters.", bg=self.CARD, fg=self.MUTED, font=("TkDefaultFont", 10)).pack(anchor="w", padx=18, pady=22)

        type_box.bind("<<ComboboxSelected>>", render_rows)
        category_box.bind("<<ComboboxSelected>>", render_rows)
        render_rows()

    def _delete_transaction_from_page(self, transaction_id: str) -> None:
        if delete_transaction(self.state, transaction_id):
            self._flash_message = "Transaction deleted. Dashboard totals are up to date."
            self.navigate("Transactions")
