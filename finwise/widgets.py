"""Reusable Tk widgets shared by the Finwise shell and pages."""

from __future__ import annotations

import tkinter as tk

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
