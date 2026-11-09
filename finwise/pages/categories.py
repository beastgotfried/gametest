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

class CategoriesPageMixin:

    def build_categories(self, parent: tk.Misc) -> None:
        self.make_page_header(parent, "Categories", "Organize income and spending with clear labels")
        card = self.make_card(parent)
        card.pack(fill="x", pady=(0, 16), ipadx=20, ipady=16)
        body = tk.Frame(card, bg=self.CARD)
        body.pack(fill="x", padx=20, pady=18)
        name = tk.StringVar()
        kind = tk.StringVar(value="expense")
        message_host = tk.Frame(body, bg=self.CARD)
        message_host.pack(fill="x")
        self.make_form_field(body, "New category", name)
        row = tk.Frame(body, bg=self.CARD)
        row.pack(fill="x", pady=(0, 14))
        tk.Label(row, text="Type", bg=self.CARD, fg=self.INK, font=("TkDefaultFont", 10, "bold")).pack(anchor="w", pady=(0, 6))
        ttk.Combobox(row, textvariable=kind, state="readonly", values=("expense", "income"), style="Finwise.TCombobox").pack(fill="x")

        def add() -> None:
            cleaned = name.get().strip()
            if not cleaned:
                self.show_inline_message(message_host, "Enter a category name.")
                return
            if any(category.name.lower() == cleaned.lower() and category.type == kind.get() for category in self.state.categories):
                self.show_inline_message(message_host, "That category already exists.")
                return
            next_id = f"cat-custom-{len(self.state.categories) + 1:03d}"
            self.state.categories.append(Category(next_id, cleaned, kind.get(), self.EMERALD if kind.get() == "income" else self.CORAL))
            self._flash_message = f"{cleaned} category added."
            self.navigate("Categories")

        self.make_button(body, "Add category", add).pack(anchor="w")
        listing = self.make_card(parent)
        listing.pack(fill="x")
        self._card_title(listing, "Your categories", "Categories used by transactions stay protected")
        for category in self.state.categories:
            row = tk.Frame(listing, bg=self.CARD)
            row.pack(fill="x", padx=18, pady=5)
            tk.Label(row, text="●", bg=self.CARD, fg=category.color, font=("TkDefaultFont", 10)).pack(side="left", padx=(0, 8))
            tk.Label(row, text=category.name, bg=self.CARD, fg=self.INK, font=("TkDefaultFont", 10, "bold")).pack(side="left")
            tk.Label(row, text=category.type.title(), bg=self.CARD, fg=self.MUTED, font=("TkDefaultFont", 9)).pack(side="left", padx=12)
            if category.id.startswith("cat-custom-"):
                self.make_button(row, "Delete", lambda category_id=category.id: self._delete_category(category_id), kind="secondary").pack(side="right")

    def _delete_category(self, category_id: str) -> None:
        category = next((item for item in self.state.categories if item.id == category_id), None)
        if category is None:
            return
        if any(tx.category == category.name for tx in self.state.transactions):
            self._flash_message = f"{category.name} is used by a transaction and cannot be deleted."
            self.navigate("Categories")
            return
        self.state.categories = [item for item in self.state.categories if item.id != category_id]
        self._flash_message = f"{category.name} category deleted."
        self.navigate("Categories")
