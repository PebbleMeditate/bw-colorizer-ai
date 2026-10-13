"""GUI entry point. Tkinter shell — thin, delegates to handlers.

Tkinter ships with CPython on Windows, so we get a desktop window with
zero extra deps. All real work happens in services via the handlers.
"""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from colorizer.bootstrap.container import build_container
from colorizer.config.settings import Settings
from colorizer.handlers.colorize_handler import ColorizeHandler


class ColorizerApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("bw-colorizer-ai")
        self.geometry("520x260")
        self.resizable(False, False)
        self._container = build_container(Settings.from_env())
        self._handler = ColorizeHandler(self._container.colorize)
        self._input: Path | None = None
        self._build_widgets()

    def _build_widgets(self) -> None:
        frm = ttk.Frame(self, padding=16)
        frm.pack(fill="both", expand=True)
        ttk.Label(frm, text="Input image:").grid(row=0, column=0, sticky="w")
        self._in_var = tk.StringVar(value="(none)")
        ttk.Label(frm, textvariable=self._in_var, width=44).grid(row=0, column=1, sticky="w")
        ttk.Button(frm, text="Browse", command=self._pick).grid(row=0, column=2)
        ttk.Button(frm, text="Colorize", command=self._run).grid(row=1, column=1, pady=16)

    def _pick(self) -> None:
        chosen = filedialog.askopenfilename(
            filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp *.tif *.tiff")]
        )
        if chosen:
            self._input = Path(chosen)
            self._in_var.set(self._input.name)

    def _run(self) -> None:
        if self._input is None:
            messagebox.showwarning("bw-colorizer-ai", "Pick an image first.")
            return
        try:
            out = self._handler.run(self._input, None)
        except Exception as exc:  # surface to the user, log the rest
            messagebox.showerror("bw-colorizer-ai", str(exc))
            return
        messagebox.showinfo("bw-colorizer-ai", f"Wrote {out}")


def main() -> int:
    ColorizerApp().mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())