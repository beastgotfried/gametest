"""Tk application shell, authentication, navigation, and shared UI helpers."""

from __future__ import annotations

from datetime import date
from typing import Optional
import tkinter as tk
from tkinter import ttk

from .core import AppState, User, authenticate, register_user
from .widgets import RoundedCard
from .pages.accounts import AccountsPageMixin
from .pages.add_income_expense import AddIncomeExpensePageMixin
from .pages.analytics import AnalyticsPageMixin
from .pages.budgets import BudgetsPageMixin
from .pages.categories import CategoriesPageMixin
from .pages.dashboard import DashboardPageMixin
from .pages.profile import ProfilePageMixin
from .pages.recurring_payments import RecurringPaymentsPageMixin
from .pages.reports import ReportsPageMixin
from .pages.savings_goals import SavingsGoalsPageMixin
from .pages.settings import SettingsPageMixin
from .pages.transactions import TransactionsPageMixin

class FinanceApp(DashboardPageMixin, ProfilePageMixin, TransactionsPageMixin, AddIncomeExpensePageMixin, CategoriesPageMixin, AccountsPageMixin, BudgetsPageMixin, SavingsGoalsPageMixin, RecurringPaymentsPageMixin, ReportsPageMixin, AnalyticsPageMixin, SettingsPageMixin, tk.Tk):
    GRAPHITE = "#111827"
    CONTENT = "#F6F8F7"
    INK = "#17202A"
    RAIL_TEXT = "#F4F7F5"
    MUTED = "#6B7785"
    EMERALD = "#2FAE83"
    CORAL = "#D9776A"
    MINT = "#E2F4EC"
    BORDER = "#E1E7E4"
    CARD = "#FFFFFF"
    NAV_GROUPS = (
        ("Overview", ("Dashboard", "Profile")),
        ("Money", ("Transactions", "Add Income", "Add Expense", "Categories", "Accounts")),
        ("Planning", ("Budgets", "Savings Goals", "Recurring Payments")),
        ("Insights", ("Reports", "Analytics", "Settings")),
    )
    PAGE_METHODS = {
        "Dashboard": "build_dashboard",
        "Profile": "build_profile",
        "Transactions": "build_transactions",
        "Add Income": "build_add_income",
        "Add Expense": "build_add_expense",
        "Categories": "build_categories",
        "Budgets": "build_budgets",
        "Savings Goals": "build_savings_goals",
        "Recurring Payments": "build_recurring_payments",
        "Accounts": "build_accounts",
        "Reports": "build_reports",
        "Analytics": "build_analytics",
        "Settings": "build_settings",
    }

    def __init__(self) -> None:
        super().__init__()
        self.title("Finwise · Personal finance, clearly")
        self.minsize(1180, 760)
        self.geometry("1280x820")
        self.configure(bg=self.CONTENT)

        self.state = AppState.seeded()
        # ``AppState.seeded`` contains the demo profile for calculations, but
        # the UI starts logged out so the authentication flow is visible.
        self.state.current_user = None
        self.current_user: Optional[User] = None
        self.active_page = "Login"
        self._shell_built = False
        self._content_frame: Optional[tk.Frame] = None
        self._page_title_var = tk.StringVar(value="Welcome back")
        self._page_subtitle_var = tk.StringVar(value="")
        self._status_var = tk.StringVar(value="")
        self._configure_styles()
        self.show_login()

    def _configure_styles(self) -> None:
        """Configure a compact ttk vocabulary used by every screen."""
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            # A platform may not ship ``clam``; native styles still render
            # correctly with the explicit colours below.
            pass
        style.configure("Finwise.TButton", font=("TkDefaultFont", 10, "bold"), padding=(14, 9))
        style.configure("Primary.TButton", background=self.EMERALD, foreground="white")
        style.map("Primary.TButton", background=[("active", "#248967"), ("pressed", "#1F7658")])
        style.configure("Secondary.TButton", background=self.CARD, foreground=self.INK)
        style.map("Secondary.TButton", background=[("active", self.MINT), ("pressed", "#D6EEE3")])
        style.configure("Rail.TButton", background=self.GRAPHITE, foreground="#C7D4CE", anchor="w", padding=(16, 9))
        style.map("Rail.TButton", background=[("active", "#1D2A3B")], foreground=[("active", "white")])
        style.configure("SelectedRail.TButton", background="#1F3B35", foreground="white", anchor="w", padding=(16, 9))
        style.configure("Finwise.TEntry", padding=(10, 8), fieldbackground=self.CARD)
        style.configure("Finwise.TCombobox", padding=(8, 6), fieldbackground=self.CARD)

    def clear_root(self) -> None:
        """Destroy all children of the root before drawing a new screen."""
        for child in self.winfo_children():
            child.destroy()
        self._shell_built = False
        self._content_frame = None

    def make_button(
        self,
        parent: tk.Misc,
        text: str,
        command,
        *,
        kind: str = "primary",
        **kwargs,
    ) -> ttk.Button:
        """Create a consistently styled button for pages and forms."""
        style = {"primary": "Primary.TButton", "secondary": "Secondary.TButton", "rail": "Rail.TButton"}.get(
            kind, "Finwise.TButton"
        )
        return ttk.Button(parent, text=text, command=command, style=style, **kwargs)

    def make_card(self, parent: tk.Misc, *, padding: int = 16, **kwargs) -> tk.Frame:
        """Return a light panel with the shared border and card surface."""
        frame = RoundedCard(parent, fill=self.CARD, border=self.BORDER, **kwargs)
        # Consumers can use this value when they need a standard inset.
        frame.card_padding = padding  # type: ignore[attr-defined]
        return frame

    def make_page_header(self, parent: tk.Misc, title: str, subtitle: str = "") -> tk.Frame:
        header = tk.Frame(parent, bg=self.CONTENT)
        header.pack(fill="x", pady=(0, 20))
        tk.Label(header, text=title, bg=self.CONTENT, fg=self.INK, font=("TkDefaultFont", 22, "bold")).pack(anchor="w")
        if subtitle:
            tk.Label(header, text=subtitle, bg=self.CONTENT, fg=self.MUTED, font=("TkDefaultFont", 10)).pack(anchor="w", pady=(5, 0))
        return header

    def make_form_field(
        self,
        parent: tk.Misc,
        label: str,
        variable: tk.Variable,
        *,
        show: Optional[str] = None,
    ) -> ttk.Entry:
        row = tk.Frame(parent, bg=self.CARD)
        row.pack(fill="x", pady=(0, 14))
        tk.Label(row, text=label, bg=self.CARD, fg=self.INK, font=("TkDefaultFont", 10, "bold")).pack(anchor="w", pady=(0, 6))
        entry = ttk.Entry(row, textvariable=variable, style="Finwise.TEntry", show=show or "")
        entry.pack(fill="x")
        return entry

    def show_inline_message(self, parent: tk.Misc, message: str, *, kind: str = "error") -> tk.Label:
        """Show routine form feedback without interrupting the Tk event loop."""
        colour = self.CORAL if kind == "error" else self.EMERALD
        label = tk.Label(parent, text=message, bg=self.CARD, fg=colour, justify="left", anchor="w", wraplength=420)
        label.pack(fill="x", pady=(0, 12))
        return label

    def _screen_card(self, heading: str, intro: str = "") -> tuple[tk.Frame, tk.Frame]:
        """Create the two-column auth screen and return (card, form_body)."""
        self.clear_root()
        self.active_page = heading
        outer = tk.Frame(self, bg=self.CONTENT)
        outer.pack(fill="both", expand=True)
        outer.columnconfigure(0, weight=1)
        outer.columnconfigure(1, weight=1)
        outer.rowconfigure(0, weight=1)

        aside = tk.Frame(outer, bg=self.GRAPHITE, padx=56)
        aside.grid(row=0, column=0, sticky="nsew")
        tk.Label(aside, text="finwise", bg=self.GRAPHITE, fg=self.EMERALD, font=("TkDefaultFont", 25, "bold")).pack(anchor="w", pady=(70, 28))
        tk.Label(aside, text="A calmer view of\nyour money.", bg=self.GRAPHITE, fg=self.RAIL_TEXT, justify="left", font=("TkDefaultFont", 26, "bold")).pack(anchor="w")
        tk.Label(aside, text="Plan confidently, see the whole picture,\nand make progress one clear step at a time.", bg=self.GRAPHITE, fg="#A8B8B2", justify="left", font=("TkDefaultFont", 11), pady=24).pack(anchor="w")
        tk.Label(aside, text="PRIVATE · IN-MEMORY DEMO", bg=self.GRAPHITE, fg="#708178", font=("TkDefaultFont", 9, "bold")).pack(anchor="w", side="bottom", pady=34)

        right = tk.Frame(outer, bg=self.CONTENT, padx=70)
        right.grid(row=0, column=1, sticky="nsew")
        card = self.make_card(right, padding=32)
        card.pack(anchor="center", pady=70, ipadx=28, ipady=28)
        body = tk.Frame(card, bg=self.CARD)
        body.pack(fill="both", expand=True, padx=32, pady=28)
        tk.Label(body, text=heading, bg=self.CARD, fg=self.INK, font=("TkDefaultFont", 22, "bold")).pack(anchor="w")
        if intro:
            tk.Label(body, text=intro, bg=self.CARD, fg=self.MUTED, justify="left", wraplength=420, font=("TkDefaultFont", 10)).pack(anchor="w", pady=(7, 22))
        return card, body

    def show_login(self) -> None:
        self.current_user = None
        self.state.current_user = None
        _, body = self._screen_card("Welcome back", "Sign in to pick up where you left off.")
        email = tk.StringVar(value="demo@finwise.app")
        password = tk.StringVar()
        message_host = tk.Frame(body, bg=self.CARD)
        message_host.pack(fill="x", before=body.winfo_children()[0] if body.winfo_children() else None)
        # The host is intentionally empty; feedback labels are inserted before
        # the fields on each failed submit.
        self.make_form_field(body, "Email", email)
        self.make_form_field(body, "Password", password, show="•")

        def submit() -> None:
            user = authenticate(email.get(), password.get(), self.state.users)
            if user is None:
                self.show_inline_message(message_host, "We couldn't match that email and password. Try the demo credentials below.")
                return
            self.current_user = user
            self.state.current_user = user
            self.show_shell()

        self.make_button(body, "Sign in", submit).pack(fill="x", pady=(2, 12))
        demo = tk.Frame(body, bg=self.MINT, padx=12, pady=10)
        demo.pack(fill="x", pady=(0, 14))
        tk.Label(demo, text="Demo access", bg=self.MINT, fg=self.INK, font=("TkDefaultFont", 9, "bold")).pack(anchor="w")
        tk.Label(demo, text="demo@finwise.app  ·  demo123", bg=self.MINT, fg=self.INK, font=("TkDefaultFont", 10)).pack(anchor="w", pady=(3, 0))
        footer = tk.Frame(body, bg=self.CARD)
        footer.pack(fill="x")
        tk.Label(footer, text="New to Finwise?", bg=self.CARD, fg=self.MUTED, font=("TkDefaultFont", 10)).pack(side="left")
        self.make_button(footer, "Create an account", self.show_register, kind="secondary").pack(side="right")

    def show_register(self) -> None:
        _, body = self._screen_card("Create your account", "Start with a private, session-only workspace. No bank connection required.")
        name = tk.StringVar()
        email = tk.StringVar()
        password = tk.StringVar()
        message_host = tk.Frame(body, bg=self.CARD)
        message_host.pack(fill="x")
        self.make_form_field(body, "Full name", name)
        self.make_form_field(body, "Email", email)
        self.make_form_field(body, "Password", password, show="•")

        def submit() -> None:
            try:
                user = register_user(self.state, name.get(), email.get(), password.get())
            except ValueError as exc:
                self.show_inline_message(message_host, str(exc))
                return
            self.current_user = user
            self.state.current_user = user
            self.show_shell()

        self.make_button(body, "Create account", submit).pack(fill="x", pady=(2, 12))
        footer = tk.Frame(body, bg=self.CARD)
        footer.pack(fill="x")
        tk.Label(footer, text="Already have an account?", bg=self.CARD, fg=self.MUTED, font=("TkDefaultFont", 10)).pack(side="left")
        self.make_button(footer, "Back to sign in", self.show_login, kind="secondary").pack(side="right")

    def build_shell(self) -> None:
        """Render the authenticated rail, top bar, and flexible content host."""
        self.clear_root()
        self._shell_built = True
        self.active_page = "Dashboard"
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        rail = tk.Frame(self, bg=self.GRAPHITE, width=220)
        rail.grid(row=0, column=0, sticky="nsew")
        rail.grid_propagate(False)
        tk.Label(rail, text="finwise", bg=self.GRAPHITE, fg=self.EMERALD, font=("TkDefaultFont", 20, "bold")).pack(anchor="w", padx=18, pady=(24, 36))
        self._nav_buttons: dict[str, ttk.Button] = {}
        for group, pages in self.NAV_GROUPS:
            tk.Label(rail, text=group.upper(), bg=self.GRAPHITE, fg="#718078", font=("TkDefaultFont", 8, "bold")).pack(anchor="w", padx=18, pady=(7, 5))
            for page in pages:
                button = self.make_button(rail, f"  {page}", lambda p=page: self.navigate(p), kind="rail")
                button.pack(fill="x", padx=8, pady=1)
                self._nav_buttons[page] = button
        tk.Label(rail, text="", bg=self.GRAPHITE).pack(fill="both", expand=True)
        tk.Label(rail, text="PRIVATE WORKSPACE", bg=self.GRAPHITE, fg="#708178", font=("TkDefaultFont", 8, "bold")).pack(anchor="w", padx=18, pady=(0, 24))

        main = tk.Frame(self, bg=self.CONTENT)
        main.grid(row=0, column=1, sticky="nsew")
        main.columnconfigure(0, weight=1)
        main.rowconfigure(1, weight=1)
        top = tk.Frame(main, bg=self.CARD, height=72, padx=24)
        top.grid(row=0, column=0, sticky="ew")
        top.grid_propagate(False)
        top.columnconfigure(0, weight=1)
        tk.Label(top, textvariable=self._page_title_var, bg=self.CARD, fg=self.INK, font=("TkDefaultFont", 17, "bold")).grid(row=0, column=0, sticky="w", pady=(14, 0))
        tk.Label(top, textvariable=self._page_subtitle_var, bg=self.CARD, fg=self.MUTED, font=("TkDefaultFont", 9)).grid(row=1, column=0, sticky="w", pady=(0, 13))
        user = self.current_user or self.state.current_user
        initials = "?"
        if user:
            initials = "".join(part[0] for part in user.name.split()[:2]).upper()
        profile = tk.Frame(top, bg=self.CARD)
        profile.grid(row=0, column=1, rowspan=2, sticky="e")
        tk.Label(profile, text=initials, bg=self.MINT, fg=self.EMERALD, width=3, height=1, font=("TkDefaultFont", 10, "bold")).pack(side="left", padx=(0, 10))
        tk.Label(profile, text=user.name if user else "Guest", bg=self.CARD, fg=self.INK, font=("TkDefaultFont", 10, "bold")).pack(side="left", padx=(0, 16))
        self.make_button(profile, "Log out", self._logout, kind="secondary").pack(side="left")

        content = tk.Frame(main, bg=self.CONTENT, padx=24, pady=24)
        content.grid(row=1, column=0, sticky="nsew")
        content.columnconfigure(0, weight=1)
        content.rowconfigure(0, weight=1)
        canvas = tk.Canvas(content, bg=self.CONTENT, highlightthickness=0)
        scrollbar = ttk.Scrollbar(content, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        inner = tk.Frame(canvas, bg=self.CONTENT)
        inner.columnconfigure(0, weight=1)
        window_id = canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>", lambda _event: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda event: canvas.itemconfigure(window_id, width=event.width))
        self._content_frame = inner
        self._canvas = canvas

    def show_shell(self) -> None:
        """Enter the authenticated shell and open the configured start page."""
        self.build_shell()
        start_page = self.state.preferences.get("start_page", "Dashboard")
        self.navigate(start_page if start_page in self.PAGE_METHODS else "Dashboard")

    def _logout(self) -> None:
        self.current_user = None
        self.state.current_user = None
        self.show_login()

    def navigate(self, page_name: str) -> None:
        """Render one of the authenticated pages into the shared content host."""
        if page_name not in self.PAGE_METHODS:
            page_name = "Dashboard"
        if self.current_user is None:
            self.show_login()
            return
        if not self._shell_built or self._content_frame is None:
            self.build_shell()
        self.active_page = page_name
        for child in self._content_frame.winfo_children():
            child.destroy()
        self._page_title_var.set(page_name)
        self._page_subtitle_var.set("Your private workspace · changes are kept for this session")
        for name, button in getattr(self, "_nav_buttons", {}).items():
            button.configure(style="SelectedRail.TButton" if name == page_name else "Rail.TButton")
        builder = getattr(self, self.PAGE_METHODS[page_name])
        builder(self._content_frame)
        self._content_frame.update_idletasks()
        if hasattr(self, "_canvas"):
            self._canvas.yview_moveto(0)

    def _currency(self, value: float) -> str:
        symbols = {"USD": "$", "EUR": "€", "GBP": "£", "INR": "₹"}
        symbol = symbols.get(self.state.preferences.get("currency", "USD"), "$ ".strip())
        return f"{symbol}{value:,.2f}"

    def _period(self) -> tuple[int, int]:
        """Use the newest transaction month so demo changes are immediately visible."""
        dates: list[date] = []
        for tx in self.state.transactions:
            try:
                dates.append(date.fromisoformat(tx.date[:10]))
            except (TypeError, ValueError):
                continue
        latest = max(dates, default=date(2026, 11, 1))
        return latest.year, latest.month

    def _month_label(self, year: int, month: int) -> str:
        return date(year, month, 1).strftime("%B %Y")

    def _card_title(self, parent: tk.Misc, title: str, subtitle: str = "") -> None:
        tk.Label(parent, text=title, bg=self.CARD, fg=self.INK, font=("TkDefaultFont", 13, "bold")).pack(anchor="w", padx=18, pady=(18, 2))
        if subtitle:
            tk.Label(parent, text=subtitle, bg=self.CARD, fg=self.MUTED, font=("TkDefaultFont", 9)).pack(anchor="w", padx=18, pady=(0, 12))

    def _draw_bar_chart(self, parent: tk.Misc, values: list[tuple[str, float]], *, colour: str = "#2FAE83", height: int = 210) -> tk.Canvas:
        """Draw a small responsive category bar chart using only Canvas primitives."""
        canvas = tk.Canvas(parent, height=height, bg=self.CARD, highlightthickness=0)
        canvas.pack(fill="x", padx=18, pady=(4, 18))

        def render(_event=None) -> None:
            canvas.delete("all")
            width = max(canvas.winfo_width(), 280)
            if not values:
                canvas.create_text(width / 2, height / 2, text="No spending recorded yet", fill=self.MUTED, font=("TkDefaultFont", 10))
                return
            top = max(value for _, value in values) or 1.0
            left, right, top_pad, bottom = 100, 24, 14, 28
            usable = max(width - left - right, 100)
            row_h = max((height - top_pad - bottom) / len(values), 24)
            for index, (label, value) in enumerate(values):
                y = top_pad + index * row_h + row_h / 2
                canvas.create_text(left - 8, y, text=label[:15], anchor="e", fill=self.INK, font=("TkDefaultFont", 9))
                canvas.create_rectangle(left, y - 8, left + usable, y + 8, fill="#EDF2EF", outline="")
                bar_width = usable * value / top
                canvas.create_rectangle(left, y - 8, left + bar_width, y + 8, fill=colour, outline="")
                canvas.create_text(left + usable + 4, y, text=self._currency(value), anchor="w", fill=self.MUTED, font=("TkDefaultFont", 8))

        canvas.bind("<Configure>", render)
        canvas.after_idle(render)
        return canvas

    def _action_link(self, parent: tk.Misc, text: str, command, *, colour: Optional[str] = None) -> ttk.Button:
        button = ttk.Button(parent, text=text, command=command, style="Secondary.TButton")
        button.pack(side="left", padx=(0, 8))
        return button
