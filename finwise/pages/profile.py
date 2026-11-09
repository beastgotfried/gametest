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

class ProfilePageMixin:

    def build_profile(self, parent: tk.Misc) -> None:
        self.make_page_header(parent, "Profile", "Keep your personal details up to date")
        user = self.current_user or self.state.current_user
        if user is None:
            return
        card = self.make_card(parent)
        card.pack(fill="x", pady=(0, 16), ipadx=22, ipady=18)
        body = tk.Frame(card, bg=self.CARD)
        body.pack(fill="x", padx=22, pady=20)
        name = tk.StringVar(value=user.name)
        email = tk.StringVar(value=user.email)
        message_host = tk.Frame(body, bg=self.CARD)
        message_host.pack(fill="x")
        self.make_form_field(body, "Full name", name)
        self.make_form_field(body, "Email", email)

        def save() -> None:
            if not name.get().strip() or not email.get().strip() or "@" not in email.get():
                self.show_inline_message(message_host, "Enter a valid name and email address.")
                return
            if any(other is not user and other.email.lower() == email.get().strip().lower() for other in self.state.users):
                self.show_inline_message(message_host, "That email is already registered.")
                return
            user.name = name.get().strip()
            user.email = email.get().strip()
            self.state.current_user = user
            self.current_user = user
            self.show_inline_message(message_host, "Profile saved for this session.", kind="success")
            self._page_subtitle_var.set("Profile saved · changes are kept for this session")

        self.make_button(body, "Save profile", save).pack(anchor="w", pady=(0, 8))
