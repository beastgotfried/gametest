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

class AddIncomeExpensePageMixin:

    def build_add_transaction(self, kind: str) -> None:
        kind = "income" if kind.lower().startswith("in") else "expense"
        label = "Income" if kind == "income" else "Expense"
        self.make_page_header(self._content_frame, f"Add {label}", f"Record {label.lower()} and keep your totals current")
        parent = self._content_frame
        card = self.make_card(parent)
        card.pack(fill="x", pady=(0, 16), ipadx=22, ipady=18)
        body = tk.Frame(card, bg=self.CARD)
        body.pack(fill="x", padx=22, pady=20)
        amount = tk.StringVar()
        description = tk.StringVar()
        tx_date = tk.StringVar(value=f"{self._period()[0]:04d}-{self._period()[1]:02d}-09")
        categories = [category.name for category in self.state.categories if category.type == kind]
        if not categories:
            categories = sorted({tx.category for tx in self.state.transactions if tx.type == kind})
        category = tk.StringVar(value=categories[0] if categories else "")
        accounts = [account.name for account in self.state.accounts]
        account = tk.StringVar(value=accounts[0] if accounts else "")
        message_host = tk.Frame(body, bg=self.CARD)
        message_host.pack(fill="x")
        self.make_form_field(body, "Amount", amount)
        self.make_form_field(body, "Description", description)
        self.make_form_field(body, "Date (YYYY-MM-DD)", tx_date)
        def combo_field(title: str, variable: tk.StringVar, values: list[str]) -> None:
            row = tk.Frame(body, bg=self.CARD)
            row.pack(fill="x", pady=(0, 14))
            tk.Label(row, text=title, bg=self.CARD, fg=self.INK, font=("TkDefaultFont", 10, "bold")).pack(anchor="w", pady=(0, 6))
            ttk.Combobox(row, textvariable=variable, state="readonly", values=values, style="Finwise.TCombobox").pack(fill="x")
        combo_field("Category", category, categories)
        combo_field("Account", account, accounts)

        def save() -> None:
            try:
                parsed_amount = parse_amount(amount.get())
                if not description.get().strip() or not category.get().strip() or not account.get().strip():
                    raise ValueError("Description, category, and account are required")
                datetime.strptime(tx_date.get().strip(), "%Y-%m-%d")
                add_transaction(self.state, kind, parsed_amount, category.get().strip(), description.get().strip(), tx_date.get().strip(), account.get().strip())
            except (ValueError, TypeError) as exc:
                self.show_inline_message(message_host, str(exc))
                return
            self._flash_message = f"{label} saved. Your dashboard totals are updated."
            self.navigate("Transactions")

        button_row = tk.Frame(body, bg=self.CARD)
        button_row.pack(fill="x", pady=(2, 0))
        self.make_button(button_row, f"Save {label.lower()}", save).pack(side="left", padx=(0, 8))
        self.make_button(button_row, "Cancel", lambda: self.navigate("Transactions"), kind="secondary").pack(side="left")

    def build_add_income(self, parent: tk.Misc) -> None:
        self.build_add_transaction("income")

    def build_add_expense(self, parent: tk.Misc) -> None:
        self.build_add_transaction("expense")
