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

class RecurringPaymentsPageMixin:

    def build_recurring_payments(self, parent: tk.Misc) -> None:
        self.make_page_header(parent, "Recurring Payments", "Keep regular bills visible")
        form=self.make_card(parent); form.pack(fill="x",pady=(0,16)); self._card_title(form,"Add recurring payment")
        body=tk.Frame(form,bg=self.CARD); body.pack(fill="x",padx=18,pady=(0,16)); name=tk.StringVar(); amount=tk.StringVar(); day=tk.StringVar(value="1"); msg=tk.Frame(body,bg=self.CARD); msg.pack(fill="x")
        self.make_form_field(body,"Name",name); self.make_form_field(body,"Amount",amount); self.make_form_field(body,"Due day (1-31)",day)
        def add():
            try: value=parse_amount(amount.get()); due=int(day.get()); assert 1<=due<=31
            except (ValueError,TypeError,AssertionError): self.show_inline_message(msg,"Enter a valid amount and due day."); return
            if not name.get().strip(): self.show_inline_message(msg,"Enter a payment name."); return
            self.state.recurring_payments.append(RecurringPayment(f"rec-{len(self.state.recurring_payments)+1:03d}",name.get().strip(),value,due)); self._flash_message="Recurring payment added."; self.navigate("Recurring Payments")
        self.make_button(body,"Add payment",add).pack(anchor="w")
        listing=self.make_card(parent); listing.pack(fill="x"); self._card_title(listing,"Your recurring payments")
        for payment in self.state.recurring_payments:
            row=tk.Frame(listing,bg=self.CARD); row.pack(fill="x",padx=18,pady=7); tk.Label(row,text=payment.name,bg=self.CARD,fg=self.INK,font=("TkDefaultFont",10,"bold")).pack(side="left"); tk.Label(row,text=f"{self._currency(payment.amount)} · day {payment.due_day} · {payment.category}",bg=self.CARD,fg=self.MUTED).pack(side="left",padx=16)
            def toggle(item=payment): item.active=not item.active; self.navigate("Recurring Payments")
            self.make_button(row,"Pause" if payment.active else "Resume",toggle,kind="secondary").pack(side="right"); tk.Label(row,text="Active" if payment.active else "Paused",bg=self.CARD,fg=self.EMERALD if payment.active else self.MUTED).pack(side="right",padx=10)
