# Personal Finance Tkinter Demo Design

**Date:** 2026-11-09  
**Repository:** `beastgotfried/gametest`  
**Status:** Approved for implementation

## Goal

Create a lightweight, polished desktop personal finance demo in Tkinter with 15 navigable pages, seeded authentication, realistic in-memory data, and no database or third-party runtime dependencies.

## Product shape

The app is a single-user prototype for demonstrating a personal finance product. It has a login screen, a registration screen, and an authenticated app shell. Registration and all edits update only the current process. Restarting the app resets the seeded demo state.

The 15 pages are:

1. Login
2. Register
3. Dashboard
4. Profile
5. Transactions
6. Add Income
7. Add Expense
8. Categories
9. Budgets
10. Savings Goals
11. Recurring Payments
12. Accounts
13. Reports
14. Analytics
15. Settings

## Architecture

`finance_app.py` is the only runtime module. It owns:

- typed, in-memory data models represented as dataclasses;
- an `AppState` object containing the current user and seeded finance records;
- pure helper functions for currency formatting, date labels, totals, and chart buckets;
- a `FinanceApp` Tk root that manages authentication state and page navigation;
- small page-builder methods that render one page at a time into a shared content frame;
- reusable Tkinter helpers for cards, buttons, labels, form rows, tables, empty states, and charts.

The UI is intentionally built with `tkinter` and `tkinter.ttk` only. Charts use `tkinter.Canvas`. There is no network access, persistence layer, ORM, or dependency installation step.

## Data model and seeded state

The seeded login is:

- Email: `demo@finwise.app`
- Password: `demo123`

The seeded state contains:

- one profile for Alex Morgan;
- checking, savings, and credit card accounts;
- income and expense transactions across at least three months;
- category records with income or expense type;
- monthly category budgets;
- two savings goals with current progress;
- recurring payments with active or paused state;
- preferences for currency, theme, and dashboard start page.

All monetary values are stored as positive `float` amounts with a transaction type determining whether they increase income or expense totals. Form handlers validate required fields, numeric values, and positive amounts before mutating state.

## Navigation and page behavior

The authenticated shell has a dark left rail and a light content canvas. The rail groups navigation into Overview, Money, Planning, and Insights. Every item maps to one page-builder method and updates the page title in the top bar. The top bar also shows the current user's initials and a logout button.

Required live demo behaviors:

- Login accepts the seeded account and rejects invalid credentials with inline feedback.
- Register validates name, email, and password, then enters the app as a session-only user.
- Dashboard totals, recent transactions, budget progress, and a spending chart derive from current state.
- Transactions supports category/type filtering, deleting a transaction, and linking to add-income or add-expense.
- Add Income and Add Expense validate and append transactions.
- Categories supports adding a category and deleting user-created categories when not used by a transaction.
- Budgets supports changing monthly limits and reflects progress immediately.
- Savings Goals supports creating a goal and recording a contribution.
- Recurring Payments supports adding a payment and toggling active/paused state.
- Accounts supports adding an account and deleting an account with confirmation.
- Profile and Settings update session-only preferences and show a saved state.
- Reports and Analytics render current totals with custom canvas charts and compact insight callouts.

## Visual system

The visual read is a calm, trustworthy personal finance workspace with a premium desktop-app feel.

### Tokens

- Window background: graphite `#111827`.
- Content background: cool white `#F6F8F7`.
- Primary text: ink `#17202A` on content, white smoke `#F4F7F5` on rail.
- Muted text: `#6B7785`.
- Single primary accent: emerald `#2FAE83`.
- Expense and warning accent: coral `#D9776A`.
- Soft accent surface: mint `#E2F4EC`.
- Border: `#E1E7E4`.
- Card radius: 10 px, consistently applied to panels, buttons, and fields.

The app uses a single theme with no dark/light switch. It uses native system fonts with a clear hierarchy: bold 22 px page titles, 13 px section headings, 11 px labels, and 12 to 13 px body/table copy.

### Layout

- Minimum window size is 1180 by 760.
- Left rail is 220 px wide.
- Top bar is 72 px tall.
- Content uses a 24 px outer gutter and 16 px panel gaps.
- Metric cards use a four-column row on the dashboard, collapsing to two columns when the window narrows.
- Tables use clear column headings, alternating subtle row backgrounds, and enough padding for scanability.

### States

Buttons have hover and pressed states. Forms have inline validation text. Empty lists explain how to populate them. Mutating actions show a compact saved confirmation in the page header or form footer. Destructive account deletion uses a confirmation dialog.

## Error handling

No exception should close the app during normal demo use. Form parsing catches invalid values and displays a concise inline message. Missing categories or accounts fall back to a valid seeded option. The app uses message boxes only for confirmation and logout; routine feedback stays in the page.

## Testing and verification

The functional core is testable without opening a Tk window. `tests/test_finance_app.py` covers:

- seeded credentials and authentication success/failure;
- positive amount validation;
- income and expense totals;
- adding and deleting transactions;
- budget and savings-goal progress calculations;
- chart bucket aggregation;
- session-only registration.

Manual verification runs `python finance_app.py`, logs in with the seeded account, visits all 15 pages, exercises the primary add/edit/toggle actions, resizes the window, and logs out.

## Scope exclusions

- No persistent storage or database.
- No real bank connections or payment integrations.
- No external authentication service.
- No export or import flow.
- No third-party charting or UI packages.
