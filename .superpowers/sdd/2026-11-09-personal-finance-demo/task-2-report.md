# Task 2 Report: Tk shell, authentication, and reusable visual primitives

## Implemented

- Added a dependency-free `FinanceApp(tk.Tk)` controller with in-memory `AppState`, `current_user`, `active_page`, and a guarded `main()` entry point.
- Added reusable shell helpers: `clear_root`, `make_button`, `make_card`, `make_page_header`, `make_form_field`, `show_inline_message`, and `build_shell`.
- Added login and registration screens with seeded demo credentials, session-only registration, inline validation feedback, and login/register links.
- Added the authenticated graphite navigation rail, top bar with initials and logout, scrollable cool-white content host, shared ttk styles, and the 1180x760 minimum window size.
- Added navigation for every authenticated page name. Dashboard is populated from the functional core; remaining page builders intentionally render a “Coming next” state for later tasks.

## Verification

- `python -m py_compile finance_app.py`
- `python -m pytest tests/test_finance_app.py -q` → **10 passed**
- `git diff --check` → clean
- Import check confirms `FinanceApp` and `main` are available without creating a root window.

A full interactive Tk manual pass could not be run in this headless environment (`DISPLAY` is unset). The app remains import-safe and creates the Tk root only from `main()`/`FinanceApp` construction.
