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

class SettingsPageMixin:

    def build_settings(self, parent: tk.Misc) -> None:
        self.make_page_header(parent,"Settings","Tune your workspace")
        card=self.make_card(parent); card.pack(fill="x"); body=tk.Frame(card,bg=self.CARD); body.pack(fill="x",padx=18,pady=18)
        currency=tk.StringVar(value=self.state.preferences.get("currency","USD")); start=tk.StringVar(value=self.state.preferences.get("start_page","Dashboard")); compact=tk.BooleanVar(value=self.state.preferences.get("compact","false")=="true")
        for label,var,values in (("Currency",currency,("USD","EUR","GBP","INR")),("Start page",start,tuple(self.PAGE_METHODS))):
            row=tk.Frame(body,bg=self.CARD); row.pack(fill="x",pady=6); tk.Label(row,text=label,bg=self.CARD,fg=self.INK,width=18,anchor="w").pack(side="left"); ttk.Combobox(row,textvariable=var,state="readonly",values=values,style="Finwise.TCombobox",width=24).pack(side="left")
        ttk.Checkbutton(body,text="Use compact layout",variable=compact).pack(anchor="w",pady=10)
        tk.Label(body,text="Theme: Light (fixed demo theme)",bg=self.CARD,fg=self.MUTED).pack(anchor="w",pady=(0,10))
        def save(): self.state.preferences.update(currency=currency.get(),start_page=start.get(),compact="true" if compact.get() else "false"); self._flash_message="Settings saved for this session."; self.navigate("Settings")
        self.make_button(body,"Save settings",save).pack(anchor="w")
