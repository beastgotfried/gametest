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

class AccountsPageMixin:

    def build_accounts(self, parent: tk.Misc) -> None:
        self.make_page_header(parent, "Accounts", "Keep balances and connected institutions in one place")
        if getattr(self, "_flash_message", ""):
            tk.Label(parent, text=self._flash_message, bg=self.CONTENT, fg=self.EMERALD, font=("TkDefaultFont", 10, "bold")).pack(anchor="w", pady=(0, 12))
            self._flash_message = ""
        card = self.make_card(parent)
        card.pack(fill="x", pady=(0, 16), ipadx=20, ipady=16)
        body = tk.Frame(card, bg=self.CARD)
        body.pack(fill="x", padx=20, pady=18)
        name = tk.StringVar()
        kind = tk.StringVar(value="checking")
        balance = tk.StringVar(value="0")
        institution = tk.StringVar()
        message_host = tk.Frame(body, bg=self.CARD)
        message_host.pack(fill="x")
        self.make_form_field(body, "Account name", name)
        row = tk.Frame(body, bg=self.CARD)
        row.pack(fill="x", pady=(0, 14))
        tk.Label(row, text="Account type", bg=self.CARD, fg=self.INK, font=("TkDefaultFont", 10, "bold")).pack(anchor="w", pady=(0, 6))
        ttk.Combobox(row, textvariable=kind, state="readonly", values=("checking", "savings", "credit", "cash"), style="Finwise.TCombobox").pack(fill="x")
        self.make_form_field(body, "Current balance", balance)
        self.make_form_field(body, "Institution (optional)", institution)

        def add() -> None:
            cleaned = name.get().strip()
            if not cleaned:
                self.show_inline_message(message_host, "Enter an account name.")
                return
            try:
                numeric_balance = float(balance.get().replace(",", "").strip() or "0")
                if not math.isfinite(numeric_balance):
                    raise ValueError
            except (TypeError, ValueError):
                self.show_inline_message(message_host, "Balance must be a valid number.")
                return
            if any(account.name.lower() == cleaned.lower() for account in self.state.accounts):
                self.show_inline_message(message_host, "That account already exists.")
                return
            account_id = f"acct-custom-{len(self.state.accounts) + 1:03d}"
            self.state.accounts.append(Account(account_id, cleaned, kind.get(), numeric_balance, institution.get().strip()))
            self._flash_message = f"{cleaned} account added."
            self.navigate("Accounts")

        self.make_button(body, "Add account", add).pack(anchor="w")
        listing = self.make_card(parent)
        listing.pack(fill="x")
        self._card_title(listing, "Your accounts", f"{len(self.state.accounts)} account{'s' if len(self.state.accounts) != 1 else ''}")
        for account in self.state.accounts:
            row = tk.Frame(listing, bg=self.CARD)
            row.pack(fill="x", padx=18, pady=7)
            detail = tk.Frame(row, bg=self.CARD)
            detail.pack(side="left", fill="x", expand=True)
            tk.Label(detail, text=account.name, bg=self.CARD, fg=self.INK, font=("TkDefaultFont", 10, "bold")).pack(anchor="w")
            tk.Label(detail, text=f"{account.kind.title()} · {account.institution or 'Personal'}", bg=self.CARD, fg=self.MUTED, font=("TkDefaultFont", 9)).pack(anchor="w")
            tk.Label(row, text=self._currency(account.balance), bg=self.CARD, fg=self.CORAL if account.balance < 0 else self.EMERALD, font=("TkDefaultFont", 10, "bold")).pack(side="left", padx=14)
            self.make_button(row, "Delete", lambda account_id=account.id: self._delete_account(account_id), kind="secondary").pack(side="right")

    def _delete_account(self, account_id: str) -> None:
        if len(self.state.accounts) <= 1:
            self._flash_message = "Keep at least one account in your workspace."
            self.navigate("Accounts")
            return
        account = next((item for item in self.state.accounts if item.id == account_id), None)
        if account is None:
            return
        if any(tx.account == account.name for tx in self.state.transactions):
            self._flash_message = f"{account.name} is used by a transaction and cannot be deleted yet."
            self.navigate("Accounts")
            return
        if not messagebox.askyesno("Delete account?", f"Delete {account.name}? This action only affects this session.", parent=self):
            return
        self.state.accounts = [item for item in self.state.accounts if item.id != account_id]
        self._flash_message = f"{account.name} account deleted."
        self.navigate("Accounts")
