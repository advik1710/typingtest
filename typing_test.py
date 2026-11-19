"""A small desktop typing test built with Tkinter (Python standard library only)."""

from __future__ import annotations

import csv
import os
import random
import sys
import time
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk


PASSAGES = [
    "Small steps every day can lead to remarkable progress. Focus on the next word, keep a steady rhythm, and let accuracy guide your pace.",
    "A quiet morning is a good time to think clearly. Make a simple plan, begin with care, and give each task your full attention.",
    "Learning a new skill takes patience and practice. Mistakes are useful signals, and each attempt helps build confidence and speed.",
    "Clear writing starts with clear thinking. Choose the right words, check your work, and leave enough time to make thoughtful changes.",
]

APP_NAME = "Typing Test"
CSV_COLUMNS = ["date_time", "wpm", "accuracy_percent", "duration_seconds", "typed_text"]


def log_path() -> Path:
    """Return a per-user, persistent location on Windows, macOS, or Linux."""
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    folder = base / "TypingTest"
    folder.mkdir(parents=True, exist_ok=True)
    return folder / "attempts.csv"


class TypingTestApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Typing Test")
        self.root.geometry("760x590")
        self.root.minsize(620, 500)
        self.root.configure(bg="#f4f6fa")

        self.passage = random.choice(PASSAGES)
        self.started_at: float | None = None
        self.finished = False
        self.after_id: str | None = None

        self._style()
        self._build_ui()
        self._show_passage()
        self._tick()
        self.root.protocol("WM_DELETE_WINDOW", self._close)

    def _style(self) -> None:
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TFrame", background="#f4f6fa")
        style.configure("TLabel", background="#f4f6fa", foreground="#172033", font=("Segoe UI", 11))
        style.configure("Title.TLabel", font=("Segoe UI", 22, "bold"), foreground="#172033")
        style.configure("Muted.TLabel", foreground="#68738a", font=("Segoe UI", 10))
        style.configure("Metric.TLabel", font=("Segoe UI", 18, "bold"), foreground="#2457c5")
        style.configure("MetricName.TLabel", font=("Segoe UI", 9), foreground="#68738a")
        style.configure("TButton", font=("Segoe UI", 10), padding=(14, 8))
        style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"), padding=(14, 8))

    def _build_ui(self) -> None:
        outer = ttk.Frame(self.root, padding=(28, 22))
        outer.pack(fill="both", expand=True)

        ttk.Label(outer, text="Typing Test", style="Title.TLabel").pack(anchor="w")
        ttk.Label(outer, text="Type the passage below. The clock starts with your first keystroke.", style="Muted.TLabel").pack(anchor="w", pady=(3, 18))

        card = tk.Frame(outer, bg="white", highlightbackground="#e0e5ee", highlightthickness=1)
        card.pack(fill="x", pady=(0, 16))
        self.prompt = tk.Text(card, height=4, wrap="word", padx=16, pady=14, bg="white", fg="#27344b", font=("Segoe UI", 13), relief="flat", borderwidth=0, spacing1=3, spacing3=3)
        self.prompt.pack(fill="both", expand=True)
        self.prompt.configure(state="disabled")

        ttk.Label(outer, text="Your typing", style="Muted.TLabel").pack(anchor="w", pady=(0, 6))
        self.input = tk.Text(outer, height=6, wrap="word", padx=12, pady=10, bg="white", fg="#172033", insertbackground="#2457c5", font=("Segoe UI", 12), relief="solid", borderwidth=1, highlightthickness=1, highlightbackground="#d6dce7", highlightcolor="#2457c5", undo=True)
        self.input.pack(fill="both", expand=True)
        self.input.bind("<KeyRelease>", self._on_key_release)
        self.input.bind("<<Paste>>", self._on_key_release)
        self.input.focus_set()

        metrics = ttk.Frame(outer)
        metrics.pack(fill="x", pady=(18, 14))
        self.wpm_value = self._metric(metrics, "WPM", 0)
        self.accuracy_value = self._metric(metrics, "ACCURACY", 1)
        self.time_value = self._metric(metrics, "TIME", 2)
        self.status = ttk.Label(outer, text="Ready when you are.", style="Muted.TLabel")
        self.status.pack(anchor="w")

        buttons = ttk.Frame(outer)
        buttons.pack(fill="x", pady=(14, 0))
        self.new_button = ttk.Button(buttons, text="New passage", command=self._new_passage)
        self.new_button.pack(side="left")
        self.finish_button = ttk.Button(buttons, text="Finish attempt", style="Primary.TButton", command=self._finish)
        self.finish_button.pack(side="right")

    @staticmethod
    def _metric(parent: ttk.Frame, label: str, column: int) -> ttk.Label:
        block = ttk.Frame(parent)
        block.grid(row=0, column=column, sticky="w", padx=(0, 40))
        value = ttk.Label(block, text="0", style="Metric.TLabel")
        value.pack(anchor="w")
        ttk.Label(block, text=label, style="MetricName.TLabel").pack(anchor="w")
        return value

    def _show_passage(self) -> None:
        self.prompt.configure(state="normal")
        self.prompt.delete("1.0", "end")
        self.prompt.insert("1.0", self.passage)
        self.prompt.configure(state="disabled")

    def _typed_text(self) -> str:
        return self.input.get("1.0", "end-1c")

    def _on_key_release(self, _event: tk.Event | None = None) -> None:
        if self.finished:
            return
        typed = self._typed_text()
        if typed and self.started_at is None:
            self.started_at = time.perf_counter()
            self.status.configure(text="Timer running. Keep going!")
        self._update_metrics()
        if len(typed) >= len(self.passage):
            self._finish()

    def _update_metrics(self) -> None:
        typed = self._typed_text()
        elapsed = max(0.0, time.perf_counter() - self.started_at) if self.started_at is not None else 0.0
        correct = sum(a == b for a, b in zip(typed, self.passage))
        accuracy = (correct / len(typed) * 100) if typed else 0.0
        wpm = (correct / 5) / (elapsed / 60) if elapsed > 0 else 0.0
        self.wpm_value.configure(text=f"{wpm:.0f}")
        self.accuracy_value.configure(text=f"{accuracy:.0f}%")
        self.time_value.configure(text=f"{elapsed:.1f}s")

    def _tick(self) -> None:
        if self.started_at is not None and not self.finished:
            self._update_metrics()
        self.after_id = self.root.after(150, self._tick)

    def _finish(self) -> None:
        if self.finished:
            return
        typed = self._typed_text()
        if not typed.strip():
            self.status.configure(text="Type something before finishing.")
            return
        now = time.perf_counter()
        elapsed = max(0.0, now - self.started_at) if self.started_at is not None else 0.0
        correct = sum(a == b for a, b in zip(typed, self.passage))
        accuracy = (correct / len(typed) * 100) if typed else 0.0
        wpm = (correct / 5) / (elapsed / 60) if elapsed > 0 else 0.0
        self.finished = True
        self.input.configure(state="disabled")
        self._update_metrics()
        try:
            path = log_path()
            write_header = not path.exists() or path.stat().st_size == 0
            with path.open("a", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS)
                if write_header:
                    writer.writeheader()
                writer.writerow({
                    "date_time": datetime.now().astimezone().isoformat(timespec="seconds"),
                    "wpm": f"{wpm:.2f}",
                    "accuracy_percent": f"{accuracy:.2f}",
                    "duration_seconds": f"{elapsed:.2f}",
                    "typed_text": typed,
                })
            self.status.configure(text=f"Attempt saved to {path}")
        except OSError as exc:
            self.status.configure(text=f"Could not save the log: {exc}")
            messagebox.showerror("Log could not be saved", f"Your result is shown, but the log could not be written.\n\n{exc}")

    def _new_passage(self) -> None:
        self.passage = random.choice([p for p in PASSAGES if p != self.passage] or PASSAGES)
        self.started_at = None
        self.finished = False
        self._show_passage()
        self.input.configure(state="normal")
        self.input.delete("1.0", "end")
        self.input.focus_set()
        self.status.configure(text="Ready when you are.")
        self._update_metrics()

    def _close(self) -> None:
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
        self.root.destroy()


def main() -> None:
    root = tk.Tk()
    TypingTestApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
