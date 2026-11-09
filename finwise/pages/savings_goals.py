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

class SavingsGoalsPageMixin:

    def build_savings_goals(self, parent: tk.Misc) -> None:
        self.make_page_header(parent, "Savings Goals", "Make progress on what matters")
        if getattr(self, "_flash_message", ""): tk.Label(parent, text=self._flash_message, bg=self.CONTENT, fg=self.EMERALD).pack(anchor="w"); self._flash_message = ""
        form = self.make_card(parent); form.pack(fill="x", pady=(0, 16)); self._card_title(form, "Create a goal")
        body = tk.Frame(form, bg=self.CARD); body.pack(fill="x", padx=18, pady=(0, 16)); name=tk.StringVar(); target=tk.StringVar(); deadline=tk.StringVar(value="2027-12-31"); msg=tk.Frame(body,bg=self.CARD); msg.pack(fill="x")
        self.make_form_field(body,"Goal name",name); self.make_form_field(body,"Target amount",target); self.make_form_field(body,"Deadline (YYYY-MM-DD)",deadline)
        def add():
            try: amount=parse_amount(target.get()); datetime.strptime(deadline.get(), "%Y-%m-%d")
            except (ValueError, TypeError): self.show_inline_message(msg,"Enter a valid target and deadline."); return
            if not name.get().strip(): self.show_inline_message(msg,"Enter a goal name."); return
            self.state.goals.append(SavingsGoal(f"goal-{len(self.state.goals)+1:03d}",name.get().strip(),amount,0.0,deadline.get().strip())); self._flash_message="Goal created."; self.navigate("Savings Goals")
        self.make_button(body,"Create goal",add).pack(anchor="w")
        for goal in self.state.goals:
            card=self.make_card(parent); card.pack(fill="x", pady=5); row=tk.Frame(card,bg=self.CARD); row.pack(fill="x", padx=18, pady=12)
            tk.Label(row,text=goal.name,bg=self.CARD,fg=self.INK,font=("TkDefaultFont",11,"bold")).pack(side="left"); tk.Label(row,text=f"{self._currency(goal.current)} / {self._currency(goal.target)} · due {goal.deadline}",bg=self.CARD,fg=self.MUTED).pack(side="left",padx=16)
            amount=tk.StringVar(); ttk.Entry(row,textvariable=amount,width=10,style="Finwise.TEntry").pack(side="right",padx=5)
            def contribute(g=goal,var=amount):
                try: contribute_to_goal(g,var.get()); self._flash_message="Contribution saved."; self.navigate("Savings Goals")
                except ValueError: self._flash_message="Contribution must be positive."; self.navigate("Savings Goals")
            self.make_button(row,"Contribute",contribute,kind="secondary").pack(side="right")
            ttk.Progressbar(card,maximum=1.0,value=goal_progress(goal)).pack(fill="x",padx=18,pady=(0,4)); tk.Label(card,text=f"{goal_progress(goal):.0%} complete",bg=self.CARD,fg=self.EMERALD).pack(anchor="e",padx=18,pady=(0,8))
