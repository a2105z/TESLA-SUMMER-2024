# ui/summarize_tab.py
"""
SummarEase tab (Tkinter).

Features:
- Paste or load a .txt file into "Original"
- Choose max sentences and run the injected summarizer
- Copy summary to clipboard
- Send Original or Summary to the Typing tab via on_text_ready(title, content)
- Persist sent texts in SQLite using services.storage.insert_text

Constructor signature matches app.py:
    SummarEaseFrame(parent, summarizer, on_text_ready, db_path)

The `summarizer` must implement: summarize(text: str, max_sentences: int) -> str
"""

from __future__ import annotations

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from typing import Callable

# Local services
try:
    from services.storage import insert_text
except Exception:
    # During early dev, app.py's safe_imports will catch missing modules.
    # This fallback avoids import-time hard crashes if imported out-of-order.
    def insert_text(db_path: str, title: str, content: str) -> int:  # type: ignore
        raise RuntimeError("services.storage.insert_text is not available yet.")


class SummarEaseFrame(ttk.Frame):
    def __init__(
        self,
        master,
        summarizer,
        on_text_ready: Callable[[str, str], None],
        db_path: str,
    ):
        super().__init__(master)
        self.summarizer = summarizer
        self.on_text_ready = on_text_ready
        self.db_path = db_path

        # Layout weights
        self.columnconfigure(0, weight=1)
        # rows: title, toolbar, original label, original text, summary label, summary text
        self.rowconfigure(3, weight=1)
        self.rowconfigure(5, weight=1)

        # Title
        ttk.Label(self, text="SummarEase", font=("Segoe UI", 16, "bold")).grid(
            row=0, column=0, sticky="w", padx=8, pady=(8, 0)
        )

        # Toolbar
        self._build_toolbar(row=1)

        # Original Text
        ttk.Label(self, text="Original text").grid(
            row=2, column=0, sticky="w", padx=8, pady=(8, 0)
        )
        self.original_text = self._make_scrolled_text(row=3, height=12)
        self.original_text.insert(
            "1.0",
            "Paste an article here, or click 'Load .txt' to open a file.",
        )
        self.original_text.bind("<<Modified>>", self._on_modified)

        # Summary Text
        ttk.Label(self, text="Summary").grid(
            row=4, column=0, sticky="w", padx=8, pady=(8, 0)
        )
        self.summary_text = self._make_scrolled_text(row=5, height=10)
        self.summary_text.bind("<<Modified>>", self._on_modified)

        # Counters / info
        info_bar = ttk.Frame(self)
        info_bar.grid(row=6, column=0, sticky="ew", padx=8, pady=(6, 8))
        info_bar.columnconfigure(0, weight=1)
        info_bar.columnconfigure(1, weight=1)

        self.orig_stats = tk.StringVar(value="Original: 0 chars, 0 words")
        self.summ_stats = tk.StringVar(value="Summary: 0 chars, 0 words")
        ttk.Label(info_bar, textvariable=self.orig_stats, anchor="w").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(info_bar, textvariable=self.summ_stats, anchor="e").grid(
            row=0, column=1, sticky="e"
        )

        # Keybindings
        self.bind_all("<Control-Return>", lambda e: self.do_summarize())
        self.bind_all("<Control-KP_Enter>", lambda e: self.do_summarize())
        self.bind_all("<Control-Shift-S>", lambda e: self.send_summary_to_typing())
        self.bind_all("<Control-Shift-O>", lambda e: self.send_original_to_typing())

        self._update_counters()

    # ---------------- UI builders ----------------

    def _build_toolbar(self, row: int):
        bar = ttk.Frame(self)
        bar.grid(row=row, column=0, sticky="ew", padx=8, pady=8)

        # Left controls
        left = ttk.Frame(bar)
        left.pack(side="left")
        ttk.Button(left, text="Load .txt", command=self.load_file).pack(side="left")
        ttk.Button(left, text="Clear", command=self.clear_texts).pack(side="left", padx=(6, 0))

        # Middle controls
        mid = ttk.Frame(bar)
        mid.pack(side="left", padx=(16, 0))
        ttk.Label(mid, text="Max sentences:").pack(side="left")
        self.max_sentences_var = tk.IntVar(value=5)
        ttk.Spinbox(mid, from_=2, to=20, width=5, textvariable=self.max_sentences_var).pack(
            side="left", padx=(6, 0)
        )
        ttk.Button(mid, text="Summarize", command=self.do_summarize).pack(side="left", padx=(10, 0))
        ttk.Button(mid, text="Copy Summary", command=self.copy_summary).pack(side="left", padx=(6, 0))

        # Right controls
        right = ttk.Frame(bar)
        right.pack(side="right")
        ttk.Button(right, text="Send Summary → Typing", command=self.send_summary_to_typing).pack(
            side="left"
        )
        ttk.Button(right, text="Send Original → Typing", command=self.send_original_to_typing).pack(
            side="left", padx=(6, 0)
        )

        # Provider badge
        prov = getattr(self.summarizer, "__class__", type("X", (), {})).__name__
        self.provider_label = ttk.Label(bar, text=f"Provider: {prov}")
        self.provider_label.pack(side="right", padx=(0, 8))

    def _make_scrolled_text(self, row: int, height: int) -> tk.Text:
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

        # Tweak text widget fonts/padding if desired
        txt.configure(font=("Segoe UI", 11), padx=6, pady=6)

        return txt

    # ---------------- Commands ----------------

    def clear_texts(self):
        self.original_text.delete("1.0", "end")
        self.summary_text.delete("1.0", "end")
        self._update_counters()

    def load_file(self):
        path = filedialog.askopenfilename(
            title="Open text file",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            self.original_text.delete("1.0", "end")
            self.original_text.insert("1.0", content)
            self._update_counters()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file:\n{e}")

    def do_summarize(self):
        src = self.original_text.get("1.0", "end").strip()
        if not src:
            messagebox.showwarning("No text", "Please provide original text first.")
            return
        max_s = int(self.max_sentences_var.get())
        try:
            summary = self.summarizer.summarize(src, max_sentences=max_s)
        except Exception as e:
            messagebox.showerror("Summarize failed", f"Provider error:\n{e}")
            return

        self.summary_text.delete("1.0", "end")
        self.summary_text.insert("1.0", summary)
        self._update_counters()

    def copy_summary(self):
        txt = self.summary_text.get("1.0", "end").strip()
        if not txt:
            messagebox.showwarning("No summary", "Nothing to copy yet.")
            return
        try:
            self.clipboard_clear()
            self.clipboard_append(txt)
            self.update()  # ensures it stays on clipboard after app exits
            messagebox.showinfo("Copied", "Summary copied to clipboard.")
        except Exception as e:
            messagebox.showerror("Clipboard", f"Failed to copy:\n{e}")

    def send_summary_to_typing(self):
        self._send_text_to_typing(title="Summary", content_widget=self.summary_text)

    def send_original_to_typing(self):
        self._send_text_to_typing(title="Original", content_widget=self.original_text)

    def _send_text_to_typing(self, title: str, content_widget: tk.Text):
        content = content_widget.get("1.0", "end").strip()
        if not content:
            messagebox.showwarning("No text", f"{title} text is empty.")
            return
        # Persist then hand off
        try:
            text_id = insert_text(self.db_path, title, content)
            # We don't need text_id here, but it’s saved for analytics/history
        except Exception as e:
            # Still allow sending to typing even if persistence fails
            messagebox.showwarning(
                "Saved with warning",
                f"Could not save to database ({e}). Sending to Typing anyway.",
            )
        self.on_text_ready(title, content)

    # ---------------- Helpers ----------------

    def _on_modified(self, event):
        # Reset the modified flag and update counters
        widget = event.widget
        widget.edit_modified(False)
        self._update_counters()

    def _update_counters(self):
        o = self.original_text.get("1.0", "end").strip()
        s = self.summary_text.get("1.0", "end").strip()
        self.orig_stats.set(f"Original: {len(o)} chars, {self._word_count(o)} words")
        self.summ_stats.set(f"Summary: {len(s)} chars, {self._word_count(s)} words")

    @staticmethod
    def _word_count(text: str) -> int:
        # Simple whitespace tokenization
        return len([w for w in text.split() if w.strip()])