# ui/typing_tab.py
"""
Typing Trainer tab (Tkinter).

Features:
- Load a target text from .txt file (saved under data/texts if you want to organize)
- Paste from clipboard
- Accept text directly from SummarEase via set_target_text(title, content)
- Start/Pause/Reset a timed run with live metrics (WPM, accuracy, streak)
- Per-character correctness highlighting in the input field
- Save runs in SQLite and display/refresh global high score

Constructor signature (as expected by app.py):
    TypingTrainerFrame(parent, db_path: str, texts_dir: str)

Public method:
    set_target_text(title: str, content: str) -> None
"""

from __future__ import annotations

import os
import time
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# Storage services
try:
    from services.storage import insert_text, insert_run, get_high_score
except Exception:
    # app.py's safe_imports will catch issues, but keep a friendly fallback here.
    def insert_text(db_path: str, title: str, content: str) -> int:  # type: ignore
        raise RuntimeError("services.storage.insert_text unavailable")

    def insert_run(db_path: str, text_id, wpm, accuracy, duration_sec) -> int:  # type: ignore
        raise RuntimeError("services.storage.insert_run unavailable")

    def get_high_score(db_path: str) -> float:  # type: ignore
        return 0.0


# ---------------------------
# Utility metric functions
# ---------------------------

def _compute_wpm(chars_typed: int, elapsed_sec: float) -> int:
    """Standard typing metric: 5 chars = 1 word."""
    elapsed_min = max(elapsed_sec / 60.0, 1e-9)
    return round((chars_typed / 5.0) / elapsed_min)


def _compute_accuracy(correct: int, total: int) -> float:
    if total <= 0:
        return 100.0
    return round(100.0 * correct / total, 2)


class TypingTrainerFrame(ttk.Frame):
    def __init__(self, master, db_path: str, texts_dir: str):
        super().__init__(master)
        self.db_path = db_path
        self.texts_dir = Path(texts_dir)

        # --- State ---
        self.text_id = None                # persisted text id (if saved)
        self.title_str = "Untitled"
        self.target_text = ""              # current target
        self.started = False
        self.paused = False
        self.start_time = None            # baseline timestamp
        self.elapsed = 0.0
        self.correct = 0
        self.streak = 0
        self.time_limit_sec = 60

        # --- Layout weights ---
        self.columnconfigure(0, weight=1)
        # rows: title, toolbar, target label, target text, input label, input text, metrics
        self.rowconfigure(3, weight=0)
        self.rowconfigure(5, weight=1)

        # --- Header ---
        ttk.Label(self, text="Typing Trainer", font=("Segoe UI", 16, "bold")).grid(
            row=0, column=0, sticky="w", padx=8, pady=(8, 0)
        )

        # --- Toolbar ---
        self._build_toolbar(row=1)

        # --- Target text ---
        ttk.Label(self, text="Target text").grid(row=2, column=0, sticky="w", padx=8, pady=(8, 0))
        self.target = self._make_scrolled_text(row=3, height=8, readonly=True)

        # --- Input area ---
        ttk.Label(self, text="Your input").grid(row=4, column=0, sticky="w", padx=8, pady=(8, 0))
        self.input = self._make_scrolled_text(row=5, height=10)
        self.input.bind("<KeyRelease>", self._on_key_release)
        self.input.bind("<Control-BackSpace>", self._ctrl_backspace)  # quality-of-life

        # --- Metrics & high score ---
        self.metrics_var = tk.StringVar(value="WPM: 0 | Accuracy: 100.00% | Streak: 0 | Time: 60.00s")
        self.high_var = tk.StringVar(value=f"High Score: {int(get_high_score(self.db_path))} WPM")
        self.title_var = tk.StringVar(value="Title: (none)")
        metrics_bar = ttk.Frame(self)
        metrics_bar.grid(row=6, column=0, sticky="ew", padx=8, pady=(6, 8))
        metrics_bar.columnconfigure(0, weight=1)
        ttk.Label(metrics_bar, textvariable=self.title_var).pack(side="left")
        ttk.Label(metrics_bar, textvariable=self.metrics_var).pack(side="left", padx=(12, 0))
        ttk.Label(metrics_bar, textvariable=self.high_var).pack(side="right")

        # --- Highlighting tags ---
        self.input.tag_configure("correct", foreground="green")
        self.input.tag_configure("incorrect", foreground="red")
        # caret visibility tweak (optional): self.input.config(insertwidth=2)

        # --- Timer tick ---
        self.after(50, self._tick)

        # --- Shortcuts ---
        self.bind_all("<Control-Shift-R>", lambda e: self.reset_run())
        self.bind_all("<Control-p>", lambda e: self._toggle_pause())
        self.bind_all("<Control-Return>", lambda e: self.start_run())
        self.bind_all("<Control-KP_Enter>", lambda e: self.start_run())

    # ---------------- UI builders ----------------

    def _build_toolbar(self, row: int):
        bar = ttk.Frame(self)
        bar.grid(row=row, column=0, sticky="ew", padx=8, pady=8)

        left = ttk.Frame(bar)
        left.pack(side="left")
        ttk.Button(left, text="Load .txt", command=self._load_text_file).pack(side="left")
        ttk.Button(left, text="Use Clipboard", command=self._use_clipboard).pack(side="left", padx=(6, 0))

        mid = ttk.Frame(bar)
        mid.pack(side="left", padx=(16, 0))
        ttk.Label(mid, text="Time limit (s):").pack(side="left")
        self.tlimit_var = tk.IntVar(value=self.time_limit_sec)
        ttk.Spinbox(mid, from_=15, to=600, textvariable=self.tlimit_var, width=6).pack(side="left", padx=(6, 0))
        ttk.Button(mid, text="Start", command=self.start_run).pack(side="left", padx=(12, 0))
        self.pause_btn = ttk.Button(mid, text="Pause", command=self._toggle_pause, state="disabled")
        self.pause_btn.pack(side="left", padx=(6, 0))
        ttk.Button(mid, text="Reset", command=self.reset_run).pack(side="left", padx=(6, 0))

        right = ttk.Frame(bar)
        right.pack(side="right")
        ttk.Button(right, text="Save Target", command=self._persist_target).pack(side="left")

    def _make_scrolled_text(self, row: int, height: int, readonly: bool = False) -> tk.Text:
        wrapper = ttk.Frame(self)
        wrapper.grid(row=row, column=0, sticky="nsew", padx=8)
        self.rowconfigure(row, weight=1)

        txt = tk.Text(wrapper, height=height, wrap="word", undo=True)
        txt.grid(row=0, column=0, sticky="nsew")
        wrapper.rowconfigure(0, weight=1)
        wrapper.columnconfigure(0, weight=1)

        yscroll = ttk.Scrollbar(wrapper, orient="vertical", command=txt.yview)
        yscroll.grid(row=0, column=1, sticky="ns")
        txt.configure(yscrollcommand=yscroll.set)

        xscroll = ttk.Scrollbar(wrapper, orient="horizontal", command=txt.xview)
        xscroll.grid(row=1, column=0, sticky="ew")
        txt.configure(xscrollcommand=xscroll.set)

        txt.configure(font=("Segoe UI", 11), padx=6, pady=6)

        if readonly:
            # Disable edits but keep selectable
            txt.configure(state="disabled")

        return txt

    # ---------------- Public API ----------------

    def set_target_text(self, title: str, content: str) -> None:
        """Used by SummarEase tab to hand off content."""
        self.title_str = title or "Untitled"
        self._set_target_widget(content)
        self.text_id = None  # unknown until explicitly saved
        self.title_var.set(f"Title: {self.title_str}")
        # Reset any ongoing run to ensure consistency
        self.reset_run(clear_input_only=True)

    # ---------------- Commands ----------------

    def _load_text_file(self):
        path = filedialog.askopenfilename(
            title="Open text file",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialdir=str(self.texts_dir) if self.texts_dir.exists() else os.getcwd(),
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read().strip()
            self.title_str = os.path.basename(path)
            self._set_target_widget(content)
            self.text_id = None  # not yet saved into DB for this session
            self.title_var.set(f"Title: {self.title_str}")
            self.reset_run(clear_input_only=True)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file:\n{e}")

    def _use_clipboard(self):
        try:
            content = self.clipboard_get().strip()
        except tk.TclError:
            messagebox.showwarning("Clipboard", "No text in clipboard.")
            return
        if not content:
            messagebox.showwarning("Clipboard", "Clipboard text is empty.")
            return
        self.title_str = "Clipboard"
        self._set_target_widget(content)
        self.text_id = None
        self.title_var.set(f"Title: {self.title_str}")
        self.reset_run(clear_input_only=True)

    def _persist_target(self):
        """Save the current target text to DB (if not empty)."""
        content = self.target_text.strip()
        if not content:
            messagebox.showwarning("No target", "Nothing to save.")
            return
        try:
            self.text_id = insert_text(self.db_path, self.title_str, content)
            messagebox.showinfo("Saved", f"Saved target as '{self.title_str}' (id {self.text_id}).")
        except Exception as e:
            messagebox.showerror("Save failed", f"Could not save target:\n{e}")

    def start_run(self):
        if not self.target_text.strip():
            messagebox.showwarning("No target", "Load or paste target text first.")
            return
        # Reset run state
        self.started = True
        self.paused = False
        self.start_time = time.time()
        self.elapsed = 0.0
        self.correct = 0
        self.streak = 0
        self.time_limit_sec = int(self.tlimit_var.get())
        self.input.delete("1.0", "end")
        self.pause_btn.configure(state="normal", text="Pause")
        self._update_metrics_display(remaining=self.time_limit_sec)

    def _toggle_pause(self):
        if not self.started:
            return
        self.paused = not self.paused
        if self.paused:
            self.pause_btn.configure(text="Resume")
        else:
            # Rebase start_time so elapsed remains continuous
            now = time.time()
            self.start_time = now - self.elapsed
            self.pause_btn.configure(text="Pause")

    def reset_run(self, clear_input_only: bool = False):
        """Reset the run; optionally keep the target text."""
        self.started = False
        self.paused = False
        self.start_time = None
        self.elapsed = 0.0
        self.correct = 0
        self.streak = 0
        self.pause_btn.configure(state="disabled", text="Pause")
        self._update_metrics_display(remaining=float(self.tlimit_var.get()))
        self.input.delete("1.0", "end")
        if not clear_input_only:
            # keep target text, just ensure caret at top
            self.target.see("1.0")

    # ---------------- Event handlers ----------------

    def _on_key_release(self, _evt):
        if not self.started or self.paused:
            return
        self._highlight_input()
        self._update_runtime_metrics()
        self._check_stop_conditions()

    def _ctrl_backspace(self, evt):
        """Delete previous word (simple heuristic)."""
        self.input.delete("insert-1c wordstart", "insert")
        return "break"

    # ---------------- Core logic ----------------

    def _set_target_widget(self, content: str):
        self.target_text = content or ""
        self.target.configure(state="normal")
        self.target.delete("1.0", "end")
        self.target.insert("1.0", self.target_text)
        self.target.configure(state="disabled")

    def _highlight_input(self):
        typed = self.input.get("1.0", "end-1c")
        self.input.tag_remove("correct", "1.0", "end")
        self.input.tag_remove("incorrect", "1.0", "end")

        self.correct = 0
        self.streak = 0
        for i, ch in enumerate(typed):
            if i >= len(self.target_text):
                # Extra characters beyond target count as incorrect
                self.input.tag_add("incorrect", f"1.0+{i}c", f"1.0+{i+1}c")
                self.streak = 0
                continue
            if ch == self.target_text[i]:
                self.input.tag_add("correct", f"1.0+{i}c", f"1.0+{i+1}c")
                self.correct += 1
                self.streak += 1
            else:
                self.input.tag_add("incorrect", f"1.0+{i}c", f"1.0+{i+1}c")
                self.streak = 0

    def _update_runtime_metrics(self):
        typed = self.input.get("1.0", "end-1c")
        now = time.time()
        # Elapsed since start_time; if paused we avoid updating elapsed in tick()
        self.elapsed = (now - self.start_time) if self.start_time else 0.0
        remaining = max(self.time_limit_sec - self.elapsed, 0.0)
        wpm = _compute_wpm(len(typed), max(self.elapsed, 1e-9))
        acc = _compute_accuracy(self.correct, len(typed))
        self._update_metrics_display(wpm=wpm, acc=acc, remaining=remaining)

    def _update_metrics_display(self, wpm: int = 0, acc: float = 100.0, remaining: float = None):
        if remaining is None:
            remaining = max(self.time_limit_sec - self.elapsed, 0.0)
        self.metrics_var.set(
            f"WPM: {wpm} | Accuracy: {acc:.2f}% | Streak: {self.streak} | Time: {remaining:.2f}s"
        )

    def _check_stop_conditions(self):
        typed = self.input.get("1.0", "end-1c")
        remaining = max(self.time_limit_sec - self.elapsed, 0.0)
        if remaining <= 0:
            self._finish_run(reason="time")
        elif typed == self.target_text:
            self._finish_run(reason="complete")

    def _finish_run(self, reason: str):
        self.started = False
        self.pause_btn.configure(state="disabled", text="Pause")
        typed = self.input.get("1.0", "end-1c")
        wpm = _compute_wpm(len(typed), max(self.elapsed, 1e-9))
        acc = _compute_accuracy(self.correct, len(typed))
        # Save run
        try:
            insert_run(self.db_path, self.text_id, wpm, acc, self.elapsed)
        except Exception as e:
            messagebox.showwarning("Run not saved", f"Could not save run:\n{e}")
        # Update high score
        try:
            hs = int(get_high_score(self.db_path))
            self.high_var.set(f"High Score: {hs} WPM")
        except Exception:
            pass

        msg = f"Finished by {'time' if reason=='time' else 'completion'}.\nTime: {self.elapsed:.1f}s\nWPM: {wpm}\nAccuracy: {acc:.2f}%"
        messagebox.showinfo("Run complete", msg)

    # ---------------- Timer ----------------

    def _tick(self):
        if self.started and not self.paused:
            # Keep the time display feeling responsive even without keypresses
            self._update_runtime_metrics()
        self.after(50, self._tick)