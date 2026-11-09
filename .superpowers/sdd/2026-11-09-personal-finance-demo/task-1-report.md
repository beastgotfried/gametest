# Task 1 report: functional core and tests

## Files

- `finance_app.py`: standard-library-only dataclasses, seeded in-memory state, authentication, amount parsing, month/category/budget/goal helpers, and transaction mutation helpers.
- `tests/test_finance_app.py`: focused tests for seeded auth, rejected credentials, amount validation, month totals, category ordering, budget progress, clamped goal progress, and add/delete mutation behavior.

## Verification

Command:

```text
python -m pytest tests/test_finance_app.py -q && python -m py_compile finance_app.py
```

Output:

```text
.......                                                                  [100%]
7 passed in 0.01s
```

## Concerns

- The Tkinter shell and `FinanceApp` controller are intentionally deferred to later tasks; running `finance_app.py` is currently inert.
- State is deliberately in-memory and resets whenever `AppState.seeded()` is called, as required by the demo scope.
