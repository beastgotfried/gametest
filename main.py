"""Main launcher for the modular Finwise Tkinter demo."""

from finwise.app import FinanceApp


def main() -> None:
    app = FinanceApp()
    app.mainloop()


if __name__ == "__main__":
    main()
