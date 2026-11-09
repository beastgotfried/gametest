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
    if not isinstance(category, str) or not category.strip():
        raise ValueError("Category is required")
    if not isinstance(description, str) or not description.strip():
        raise ValueError("Description is required")
    if not isinstance(account, str) or not account.strip():
        raise ValueError("Account is required")
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


class RoundedCard(tk.Frame):
    """A Tk-safe rounded panel approximation using a lowered Canvas backdrop."""

    def __init__(self, parent: tk.Misc, *, fill: str, border: str, radius: int = 10, **kwargs) -> None:
        super().__init__(parent, bg=parent.cget("bg") if "bg" in parent.keys() else fill, bd=0, highlightthickness=0, **kwargs)
        self._fill = fill
        self._border = border
        self._radius = radius
        self._backdrop = tk.Canvas(self, bg=self.cget("bg"), highlightthickness=0, bd=0)
        self._backdrop.place(relx=0, rely=0, relwidth=1, relheight=1)
        # Canvas overrides ``lower`` for lowering canvas items, so calling it
        # with no item argument raises ``TclError``. Lower the widget itself
        # through Tk's widget command so child controls remain above the
        # painted rounded backdrop on every platform.
        self._backdrop.tk.call("lower", self._backdrop._w)
        self.bind("<Configure>", self._paint, add="+")

    def _paint(self, _event=None) -> None:
        canvas = self._backdrop
        canvas.delete("all")
        width, height = max(canvas.winfo_width(), 2), max(canvas.winfo_height(), 2)
        radius = min(self._radius, width // 2, height // 2)
        # Four corner arcs plus center rectangles keep the visual smooth while
        # remaining available on Tk builds without a rounded-rectangle primitive.
        canvas.create_rectangle(radius, 1, width - radius, height - 1, fill=self._border, outline=self._border)
        canvas.create_rectangle(1, radius, width - 1, height - radius, fill=self._border, outline=self._border)
        canvas.create_arc(1, 1, radius * 2, radius * 2, start=90, extent=90, fill=self._border, outline=self._border)
        canvas.create_arc(width - radius * 2, 1, width - 1, radius * 2, start=0, extent=90, fill=self._border, outline=self._border)
        canvas.create_arc(1, height - radius * 2, radius * 2, height - 1, start=180, extent=90, fill=self._border, outline=self._border)
        canvas.create_arc(width - radius * 2, height - radius * 2, width - 1, height - 1, start=270, extent=90, fill=self._border, outline=self._border)
        inset = 1
        inner_r = max(radius - inset, 1)
        canvas.create_rectangle(inner_r + inset, inset + 1, width - inner_r - inset, height - inset - 1, fill=self._fill, outline=self._fill)
        canvas.create_rectangle(inset + 1, inner_r + inset, width - inset - 1, height - inner_r - inset, fill=self._fill, outline=self._fill)
        canvas.create_arc(inset + 1, inset + 1, inner_r * 2 + inset + 1, inner_r * 2 + inset + 1, start=90, extent=90, fill=self._fill, outline=self._fill)
        canvas.create_arc(width - inner_r * 2 - inset - 1, inset + 1, width - inset - 1, inner_r * 2 + inset + 1, start=0, extent=90, fill=self._fill, outline=self._fill)
        canvas.create_arc(inset + 1, height - inner_r * 2 - inset - 1, inner_r * 2 + inset + 1, height - inset - 1, start=180, extent=90, fill=self._fill, outline=self._fill)
        canvas.create_arc(width - inner_r * 2 - inset - 1, height - inner_r * 2 - inset - 1, width - inset - 1, height - inset - 1, start=270, extent=90, fill=self._fill, outline=self._fill)



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

    def build_dashboard(self, parent: tk.Misc) -> None:
        year, month = self._period()
        self.make_page_header(parent, "Dashboard", f"A quick read on your money in {self._month_label(year, month)}")
        income, expenses = totals_for_month(self.state, year, month)
        total_balance = sum(account.balance for account in self.state.accounts)
        metrics = (
            ("Income", income, self.EMERALD, self._currency(income)),
            ("Expenses", expenses, self.CORAL, self._currency(expenses)),
            ("Net cash flow", income - expenses, self.EMERALD if income >= expenses else self.CORAL, self._currency(income - expenses)),
            ("Total balance", total_balance, self.INK, self._currency(total_balance)),
        )
        metrics_row = tk.Frame(parent, bg=self.CONTENT)
        metrics_row.pack(fill="x", pady=(0, 18))
        for index in range(4):
            metrics_row.columnconfigure(index, weight=1)
        for index, (label, _value, colour, text) in enumerate(metrics):
            card = self.make_card(metrics_row)
            card.grid(row=0, column=index, sticky="nsew", padx=(0 if index == 0 else 6, 0 if index == 3 else 6))
            tk.Label(card, text=label.upper(), bg=self.CARD, fg=self.MUTED, font=("TkDefaultFont", 8, "bold")).pack(anchor="w", padx=16, pady=(15, 5))
            tk.Label(card, text=text, bg=self.CARD, fg=colour, font=("TkDefaultFont", 17, "bold")).pack(anchor="w", padx=16, pady=(0, 16))

        lower = tk.Frame(parent, bg=self.CONTENT)
        lower.pack(fill="x", pady=(0, 16))
        lower.columnconfigure(0, weight=3)
        lower.columnconfigure(1, weight=2)
        recent = self.make_card(lower)
        recent.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self._card_title(recent, "Recent transactions", "The latest activity across your accounts")
        for tx in sorted(self.state.transactions, key=lambda item: item.date, reverse=True)[:6]:
            row = tk.Frame(recent, bg=self.CARD)
            row.pack(fill="x", padx=18, pady=5)
            marker = self.EMERALD if tx.type == "income" else self.CORAL
            tk.Label(row, text="●", bg=self.CARD, fg=marker, font=("TkDefaultFont", 9)).pack(side="left", padx=(0, 8))
            detail = tk.Frame(row, bg=self.CARD)
            detail.pack(side="left", fill="x", expand=True)
            tk.Label(detail, text=tx.description, bg=self.CARD, fg=self.INK, font=("TkDefaultFont", 10)).pack(anchor="w")
            tk.Label(detail, text=f"{tx.category} · {tx.date[:10]}", bg=self.CARD, fg=self.MUTED, font=("TkDefaultFont", 8)).pack(anchor="w")
            tk.Label(row, text=f"{'+' if tx.type == 'income' else '-'}{self._currency(tx.amount)}", bg=self.CARD, fg=marker, font=("TkDefaultFont", 10, "bold")).pack(side="right")
        if not self.state.transactions:
            tk.Label(recent, text="Add your first income or expense to see it here.", bg=self.CARD, fg=self.MUTED).pack(anchor="w", padx=18, pady=(8, 22))

        budget_card = self.make_card(lower)
        budget_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        self._card_title(budget_card, "Budget pulse", f"{self._month_label(year, month)} category limits")
        for budget, spent, ratio in budget_progress(self.state, year, month)[:5]:
            colour = self.CORAL if ratio > 1 else self.EMERALD
            tk.Label(budget_card, text=f"{budget.category}  ·  {self._currency(spent)} / {self._currency(budget.limit)}", bg=self.CARD, fg=self.INK, font=("TkDefaultFont", 9)).pack(fill="x", padx=18, pady=(4, 2))
            bar = ttk.Progressbar(budget_card, maximum=1.0, value=min(ratio, 1.0))
            bar.pack(fill="x", padx=18, pady=(0, 5))
            tk.Label(budget_card, text="Over budget" if ratio > 1 else f"{ratio:.0%} used", bg=self.CARD, fg=colour, font=("TkDefaultFont", 8, "bold")).pack(anchor="e", padx=18)
        if not self.state.budgets:
            tk.Label(budget_card, text="No budgets yet.", bg=self.CARD, fg=self.MUTED).pack(anchor="w", padx=18, pady=(5, 20))

        chart_card = self.make_card(parent)
        chart_card.pack(fill="x", pady=(0, 16))
        self._card_title(chart_card, "Spending by category", f"Where {self._month_label(year, month)} expenses are going")
        self._draw_bar_chart(chart_card, spending_by_category(self.state, year, month)[:6], colour=self.CORAL)

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


    def _build_stub_page(self, parent: tk.Misc, title: str, detail: str) -> None:
        self.make_page_header(parent, title, detail)

    def build_budgets(self, parent: tk.Misc) -> None:
        year, month = self._period()
        self.make_page_header(parent, "Budgets", f"Set category limits for {self._month_label(year, month)}")
        card = self.make_card(parent); card.pack(fill="x", pady=(0, 16))
        self._card_title(card, "Monthly budgets", "Edit a limit and save to refresh progress immediately")
        for budget, spent, ratio in budget_progress(self.state, year, month):
            row = tk.Frame(card, bg=self.CARD); row.pack(fill="x", padx=18, pady=6)
            tk.Label(row, text=budget.category, bg=self.CARD, fg=self.INK, width=16, anchor="w", font=("TkDefaultFont", 10, "bold")).pack(side="left")
            limit = tk.StringVar(value=f"{budget.limit:.2f}")
            entry = ttk.Entry(row, textvariable=limit, width=12, style="Finwise.TEntry"); entry.pack(side="left", padx=8)
            tk.Label(row, text=f"spent {self._currency(spent)}", bg=self.CARD, fg=self.MUTED).pack(side="left", padx=8)
            def save(b=budget, var=limit):
                try:
                    value = parse_amount(var.get()); b.limit = value
                    self._flash_message = f"{b.category} budget updated."; self.navigate("Budgets")
                except ValueError as exc: self._flash_message = str(exc); self.navigate("Budgets")
            self.make_button(row, "Save", save, kind="secondary").pack(side="right")
            bar = ttk.Progressbar(card, maximum=1.0, value=min(ratio, 1.0)); bar.pack(fill="x", padx=18, pady=(0, 3))
            tk.Label(card, text="Over budget" if ratio > 1 else f"{ratio:.0%} used", bg=self.CARD, fg=self.CORAL if ratio > 1 else self.EMERALD, font=("TkDefaultFont", 8, "bold")).pack(anchor="e", padx=18)

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

    def build_reports(self, parent: tk.Misc) -> None:
        year,month=self._period(); income,expenses=totals_for_month(self.state,year,month); self.make_page_header(parent,"Reports",f"Cash flow for {self._month_label(year,month)}")
        card=self.make_card(parent); card.pack(fill="x",pady=(0,16)); self._card_title(card,"Income versus expenses"); self._draw_bar_chart(card,[("Income",income),("Expenses",expenses)],colour=self.EMERALD)
        net=income-expenses; tk.Label(parent,text=f"Net cash flow: {self._currency(net)}",bg=self.MINT if net>=0 else "#FCE8E5",fg=self.EMERALD if net>=0 else self.CORAL,font=("TkDefaultFont",14,"bold"),padx=16,pady=12).pack(fill="x")

    def build_analytics(self, parent: tk.Misc) -> None:
        year,month=self._period(); self.make_page_header(parent,"Analytics","Spot useful patterns in your recent activity")
        buckets=monthly_cashflow_buckets(self.state,6); card=self.make_card(parent); card.pack(fill="x",pady=(0,16)); self._card_title(card,"Six-month cash flow","Income and expenses by month")
        self._draw_bar_chart(card,[(label,income) for label,income,_ in buckets],colour=self.EMERALD)
        cat=self.make_card(parent); cat.pack(fill="x",pady=(0,16)); self._card_title(cat,"Top spending categories"); self._draw_bar_chart(cat,spending_by_category(self.state,year,month)[:5],colour=self.CORAL)
        income,expenses=totals_for_month(self.state,year,month); insights=[f"You earned {self._currency(income)} this month.",f"You spent {self._currency(expenses)} across {len(spending_by_category(self.state,year,month))} categories.","Keep an eye on categories approaching their budget limits."]
        for text in insights: tk.Label(parent,text="• "+text,bg=self.CONTENT,fg=self.INK,anchor="w",font=("TkDefaultFont",10)).pack(fill="x",pady=3)

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


def main() -> None:
    """Start the desktop app when executed as a script."""
    app = FinanceApp()
    app.mainloop()


if __name__ == "__main__":
    main()
