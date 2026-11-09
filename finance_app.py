"""Dependency-free functional core for the Finwise personal finance demo.

The module intentionally contains no Tk initialization at import time.  The
small data model and pure helpers are used by the GUI as well as by tests.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
import math
from typing import Optional

# ``tkinter`` is part of Python's standard library.  Importing the module is
# safe on headless systems because a root window is created only by
# ``FinanceApp`` (and therefore by ``main``), never at import time.
import tkinter as tk
from tkinter import messagebox, ttk


@dataclass
class Transaction:
    id: str
    type: str  # "income" or "expense"
    amount: float
    category: str
    description: str
    date: str
    account: str


@dataclass
class Category:
    id: str
    name: str
    type: str = "expense"
    color: str = "#2FAE83"


@dataclass
class Budget:
    id: str
    category: str
    limit: float
    month: str = "2026-11"


@dataclass
class SavingsGoal:
    id: str
    name: str
    target: float
    current: float
    deadline: str


@dataclass
class RecurringPayment:
    id: str
    name: str
    amount: float
    due_day: int
    category: str = "Bills"
    active: bool = True
    account: str = "Checking"


@dataclass
class Account:
    id: str
    name: str
    kind: str
    balance: float
    institution: str = ""


@dataclass
class User:
    id: str
    name: str
    email: str
    password: str


@dataclass
class AppState:
    current_user: Optional[User] = None
    users: list[User] = field(default_factory=list)
    transactions: list[Transaction] = field(default_factory=list)
    categories: list[Category] = field(default_factory=list)
    budgets: list[Budget] = field(default_factory=list)
    goals: list[SavingsGoal] = field(default_factory=list)
    recurring_payments: list[RecurringPayment] = field(default_factory=list)
    accounts: list[Account] = field(default_factory=list)
    preferences: dict[str, str] = field(default_factory=dict)

    @classmethod
    def seeded(cls) -> "AppState":
        """Build a fresh, deterministic demo state for November 2026."""
        user = User("user-demo", "Alex Morgan", "demo@finwise.app", "demo123")
        categories = [
            Category("cat-salary", "Salary", "income", "#2FAE83"),
            Category("cat-freelance", "Freelance", "income", "#72C8A5"),
            Category("cat-housing", "Housing", "expense", "#D9776A"),
            Category("cat-food", "Food", "expense", "#E6A56D"),
            Category("cat-transport", "Transport", "expense", "#8B9FE8"),
            Category("cat-bills", "Bills", "expense", "#9A7FC1"),
            Category("cat-shopping", "Shopping", "expense", "#D28BA6"),
        ]
        transactions = [
            Transaction("tx-001", "income", 5200.0, "Salary", "November salary", "2026-11-01", "Checking"),
            Transaction("tx-002", "expense", 1650.0, "Housing", "Rent", "2026-11-02", "Checking"),
            Transaction("tx-003", "expense", 86.40, "Food", "Weekly groceries", "2026-11-03", "Checking"),
            Transaction("tx-004", "expense", 42.50, "Transport", "Metro and rides", "2026-11-04", "Checking"),
            Transaction("tx-005", "expense", 68.00, "Bills", "Utilities", "2026-11-05", "Checking"),
            Transaction("tx-006", "income", 850.0, "Freelance", "Design retainer", "2026-11-06", "Checking"),
            Transaction("tx-007", "expense", 125.75, "Shopping", "Home supplies", "2026-11-07", "Credit Card"),
            Transaction("tx-008", "expense", 54.20, "Food", "Dinner with friends", "2026-11-08", "Credit Card"),
            Transaction("tx-009", "expense", 14.99, "Bills", "Music subscription", "2026-11-09", "Credit Card"),
            Transaction("tx-010", "income", 210.0, "Freelance", "Small project", "2026-10-22", "Checking"),
            Transaction("tx-011", "expense", 1610.0, "Housing", "October rent", "2026-10-02", "Checking"),
            Transaction("tx-012", "expense", 72.15, "Food", "October groceries", "2026-10-12", "Checking"),
            Transaction("tx-013", "income", 4800.0, "Salary", "September salary", "2026-09-01", "Checking"),
            Transaction("tx-014", "expense", 1610.0, "Housing", "September rent", "2026-09-02", "Checking"),
            Transaction("tx-015", "expense", 310.25, "Food", "September groceries", "2026-09-11", "Checking"),
        ]
        return cls(
            current_user=user,
            users=[user],
            transactions=transactions,
            categories=categories,
            budgets=[
                Budget("budget-housing", "Housing", 1800.0),
                Budget("budget-food", "Food", 450.0),
                Budget("budget-transport", "Transport", 200.0),
                Budget("budget-bills", "Bills", 250.0),
                Budget("budget-shopping", "Shopping", 300.0),
            ],
            goals=[
                SavingsGoal("goal-emergency", "Emergency fund", 10000.0, 6400.0, "2027-06-01"),
                SavingsGoal("goal-travel", "Japan trip", 3500.0, 1900.0, "2027-04-15"),
            ],
            recurring_payments=[
                RecurringPayment("rec-rent", "Rent", 1650.0, 2, "Housing"),
                RecurringPayment("rec-music", "Music subscription", 14.99, 9, "Bills"),
                RecurringPayment("rec-cloud", "Cloud storage", 9.99, 18, "Bills", False),
            ],
            accounts=[
                Account("acct-checking", "Checking", "checking", 4250.30, "Northstar Bank"),
                Account("acct-savings", "Savings", "savings", 6400.00, "Northstar Bank"),
                Account("acct-card", "Credit Card", "credit", -820.45, "Summit Card"),
            ],
            preferences={"currency": "USD", "theme": "light", "start_page": "Dashboard", "compact": "false"},
        )


def authenticate(email: str, password: str, users: list[User]) -> Optional[User]:
    for user in users:
        if user.email.strip().lower() == email.strip().lower() and user.password == password:
            return user
    return None


def parse_amount(value: str) -> float:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Amount is required")
    try:
        amount = float(value.replace(",", "").strip())
    except (TypeError, ValueError) as exc:
        raise ValueError("Amount must be numeric") from exc
    if not math.isfinite(amount) or amount <= 0:
        raise ValueError("Amount must be positive")
    return amount


def _in_month(tx: Transaction, year: int, month: int) -> bool:
    try:
        parsed = date.fromisoformat(tx.date[:10])
    except (TypeError, ValueError):
        return False
    return parsed.year == year and parsed.month == month


def totals_for_month(state: AppState, year: int, month: int) -> tuple[float, float]:
    income = sum(tx.amount for tx in state.transactions if tx.type == "income" and _in_month(tx, year, month))
    expenses = sum(tx.amount for tx in state.transactions if tx.type == "expense" and _in_month(tx, year, month))
    return income, expenses


def spending_by_category(state: AppState, year: int, month: int) -> list[tuple[str, float]]:
    totals: dict[str, float] = {}
    for tx in state.transactions:
        if tx.type == "expense" and _in_month(tx, year, month):
            totals[tx.category] = totals.get(tx.category, 0.0) + tx.amount
    return sorted(totals.items(), key=lambda item: (-item[1], item[0]))


def budget_progress(state: AppState, year: int, month: int) -> list[tuple[Budget, float, float]]:
    spent_by_category = dict(spending_by_category(state, year, month))
    result = []
    for budget in state.budgets:
        spent = spent_by_category.get(budget.category, 0.0)
        ratio = spent / budget.limit if budget.limit > 0 else 0.0
        result.append((budget, spent, ratio))
    return result


def monthly_cashflow_buckets(
    state: AppState,
    months: int = 6,
    end_date: date | datetime | str | None = None,
) -> list[tuple[str, float, float]]:
    """Return chronological ``(YYYY-MM, income, expenses)`` chart buckets."""
    if months < 1:
        return []
    if end_date is None:
        end = max((date.fromisoformat(tx.date[:10]) for tx in state.transactions), default=date.today())
    elif isinstance(end_date, datetime):
        end = end_date.date()
    elif isinstance(end_date, date):
        end = end_date
    else:
        end = date.fromisoformat(str(end_date)[:10])
    # Anchor on the first day of the ending month, then walk backwards.
    cursor = end.replace(day=1)
    buckets: list[tuple[str, float, float]] = []
    for offset in range(months - 1, -1, -1):
        month_index = cursor.year * 12 + cursor.month - 1 - offset
        year, month_zero_based = divmod(month_index, 12)
        month = month_zero_based + 1
        income, expenses = totals_for_month(state, year, month)
        buckets.append((f"{year:04d}-{month:02d}", income, expenses))
    return buckets


def goal_progress(goal: SavingsGoal) -> float:
    if goal.target <= 0:
        return 1.0 if goal.current > 0 else 0.0
    return max(0.0, min(1.0, goal.current / goal.target))


def add_transaction(
    state: AppState,
    type: str,
    amount: float,
    category: str,
    description: str,
    date: str,
    account: str,
) -> Transaction:
    if type not in {"income", "expense"}:
        raise ValueError("Transaction type must be income or expense")
    amount = parse_amount(str(amount))
    try:
        datetime.strptime(date[:10], "%Y-%m-%d")
    except (TypeError, ValueError) as exc:
        raise ValueError("Date must use YYYY-MM-DD") from exc
    used_ids = {tx.id for tx in state.transactions}
    numeric_ids = []
    for used_id in used_ids:
        if used_id.startswith("tx-") and used_id[3:].isdigit():
            numeric_ids.append(int(used_id[3:]))
    sequence = max(numeric_ids, default=0) + 1
    while f"tx-{sequence:03d}" in used_ids:
        sequence += 1
    tx = Transaction(f"tx-{sequence:03d}", type, amount, category, description, date[:10], account)
    state.transactions.append(tx)
    return tx


def delete_transaction(state: AppState, transaction_id: str) -> bool:
    for index, tx in enumerate(state.transactions):
        if tx.id == transaction_id:
            del state.transactions[index]
            return True
    return False


def register_user(state: AppState, name: str, email: str, password: str) -> User:
    if not name.strip() or not email.strip() or not password:
        raise ValueError("Name, email, and password are required")
    if any(user.email.lower() == email.strip().lower() for user in state.users):
        raise ValueError("Email is already registered")
    user = User(f"user-{len(state.users) + 1:03d}", name.strip(), email.strip(), password)
    state.users.append(user)
    state.current_user = user
    return user


def contribute_to_goal(goal: SavingsGoal, amount: float) -> None:
    goal.current += parse_amount(str(amount))


class FinanceApp(tk.Tk):
    """Tk controller for the in-memory Finwise demo.

    The functional core above deliberately has no UI concerns.  This class is
    a small controller that owns the current session and replaces the contents
    of a shared shell frame whenever the user navigates.  Keeping the shell in
    one root window makes every page resize naturally and keeps the app easy to
    extend in later tasks.
    """

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

    # Login and Register are top-level screens.  The other thirteen pages are
    # available from the authenticated navigation rail.
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
        frame = tk.Frame(
            parent,
            bg=self.CARD,
            highlightbackground=self.BORDER,
            highlightcolor=self.BORDER,
            highlightthickness=1,
            bd=0,
            **kwargs,
        )
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

    def _build_stub_page(self, parent: tk.Misc, title: str, detail: str) -> None:
        self.make_page_header(parent, title, detail)
        card = self.make_card(parent)
        card.pack(fill="x", pady=(0, 16), ipadx=24, ipady=26)
        tk.Label(card, text="Coming next", bg=self.CARD, fg=self.EMERALD, font=("TkDefaultFont", 13, "bold")).pack(anchor="w", padx=24, pady=(22, 6))
        tk.Label(card, text="This page is ready in the shell. Its data workflows will land in the next build.", bg=self.CARD, fg=self.MUTED, font=("TkDefaultFont", 10)).pack(anchor="w", padx=24, pady=(0, 22))

    def build_dashboard(self, parent: tk.Misc) -> None:
        self.make_page_header(parent, "Dashboard", "A quick read on your money this month")
        year, month = 2026, 11
        income, expenses = totals_for_month(self.state, year, month)
        metrics = (("Income", income, self.EMERALD), ("Expenses", expenses, self.CORAL), ("Net cash flow", income - expenses, self.EMERALD if income >= expenses else self.CORAL), ("Accounts", len(self.state.accounts), self.INK))
        metrics_row = tk.Frame(parent, bg=self.CONTENT)
        metrics_row.pack(fill="x", pady=(0, 18))
        for index in range(4):
            metrics_row.columnconfigure(index, weight=1)
        for index, (label, value, colour) in enumerate(metrics):
            card = self.make_card(metrics_row)
            card.grid(row=0, column=index, sticky="nsew", padx=(0 if index == 0 else 6, 0 if index == 3 else 6))
            text = f"${value:,.2f}" if label != "Accounts" else str(value)
            tk.Label(card, text=label.upper(), bg=self.CARD, fg=self.MUTED, font=("TkDefaultFont", 8, "bold")).pack(anchor="w", padx=16, pady=(15, 5))
            tk.Label(card, text=text, bg=self.CARD, fg=colour, font=("TkDefaultFont", 17, "bold")).pack(anchor="w", padx=16, pady=(0, 16))

        lower = tk.Frame(parent, bg=self.CONTENT)
        lower.pack(fill="both", expand=True)
        lower.columnconfigure(0, weight=3)
        lower.columnconfigure(1, weight=2)
        recent = self.make_card(lower)
        recent.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        tk.Label(recent, text="Recent transactions", bg=self.CARD, fg=self.INK, font=("TkDefaultFont", 13, "bold")).pack(anchor="w", padx=18, pady=(18, 2))
        tk.Label(recent, text="Your latest activity", bg=self.CARD, fg=self.MUTED, font=("TkDefaultFont", 9)).pack(anchor="w", padx=18, pady=(0, 12))
        for tx in list(reversed(self.state.transactions))[:6]:
            row = tk.Frame(recent, bg=self.CARD)
            row.pack(fill="x", padx=18, pady=5)
            colour = self.EMERALD if tx.type == "income" else self.CORAL
            tk.Label(row, text=tx.description, bg=self.CARD, fg=self.INK, font=("TkDefaultFont", 10)).pack(side="left")
            tk.Label(row, text=f"{'+' if tx.type == 'income' else '-'}${tx.amount:,.2f}", bg=self.CARD, fg=colour, font=("TkDefaultFont", 10, "bold")).pack(side="right")
        budget_card = self.make_card(lower)
        budget_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        tk.Label(budget_card, text="Budget pulse", bg=self.CARD, fg=self.INK, font=("TkDefaultFont", 13, "bold")).pack(anchor="w", padx=18, pady=(18, 2))
        tk.Label(budget_card, text="November spending", bg=self.CARD, fg=self.MUTED, font=("TkDefaultFont", 9)).pack(anchor="w", padx=18, pady=(0, 12))
        for budget, spent, ratio in budget_progress(self.state, year, month)[:4]:
            tk.Label(budget_card, text=f"{budget.category}  ·  ${spent:,.0f} / ${budget.limit:,.0f}", bg=self.CARD, fg=self.INK, font=("TkDefaultFont", 9)).pack(fill="x", padx=18, pady=(5, 2))
            bar = ttk.Progressbar(budget_card, maximum=1.0, value=min(ratio, 1.0))
            bar.pack(fill="x", padx=18, pady=(0, 4))

    # Pages below are intentionally small placeholders for the later task.
    def build_profile(self, parent: tk.Misc) -> None:
        self._build_stub_page(parent, "Profile", "Your personal details")

    def build_transactions(self, parent: tk.Misc) -> None:
        self._build_stub_page(parent, "Transactions", "Review your income and expenses")

    def build_add_income(self, parent: tk.Misc) -> None:
        self._build_stub_page(parent, "Add Income", "Record money coming in")

    def build_add_expense(self, parent: tk.Misc) -> None:
        self._build_stub_page(parent, "Add Expense", "Record money going out")

    def build_categories(self, parent: tk.Misc) -> None:
        self._build_stub_page(parent, "Categories", "Keep spending organized")

    def build_budgets(self, parent: tk.Misc) -> None:
        self._build_stub_page(parent, "Budgets", "Set category limits")

    def build_savings_goals(self, parent: tk.Misc) -> None:
        self._build_stub_page(parent, "Savings Goals", "Make progress on what matters")

    def build_recurring_payments(self, parent: tk.Misc) -> None:
        self._build_stub_page(parent, "Recurring Payments", "Keep regular bills visible")

    def build_accounts(self, parent: tk.Misc) -> None:
        self._build_stub_page(parent, "Accounts", "See your connected accounts")

    def build_reports(self, parent: tk.Misc) -> None:
        self._build_stub_page(parent, "Reports", "Understand your cash flow")

    def build_analytics(self, parent: tk.Misc) -> None:
        self._build_stub_page(parent, "Analytics", "Spot useful patterns")

    def build_settings(self, parent: tk.Misc) -> None:
        self._build_stub_page(parent, "Settings", "Tune your workspace")


def main() -> None:
    """Start the desktop app when executed as a script."""
    app = FinanceApp()
    app.mainloop()


if __name__ == "__main__":
    main()
