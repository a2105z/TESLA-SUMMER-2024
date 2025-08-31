# app.py
"""
SummarEase Typing Studio — Tkinter entrypoint.

Responsibilities:
- Initialize Tk root, styles, and global exception handler
- Ensure app directories exist and initialize SQLite (services.storage.init_db)
- Create the tabbed UI (Notebook) and wire inter-tab callbacks
- Provide dependency injection hooks for summarizer/storage services
- Offer small UX niceties: status bar, keyboard shortcuts, window sizing

This file deliberately keeps business logic out; the heavy lifting lives under
`services/` and the view logic in `ui/`.
"""

from __future__ import annotations

import os
import sys
import logging
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

# --- App paths / constants ----------------------------------------------------

APP_NAME = "SummarEase Typing Studio"
APP_ROOT = Path(__file__).resolve().parent
DATA_DIR = APP_ROOT / "data"
TEXTS_DIR = DATA_DIR / "texts"
DB_PATH = DATA_DIR / "app.db"

# --- Logging ------------------------------------------------------------------

def configure_logging() -> None:
    log_dir = APP_ROOT / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "app.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        handlers=[
            logging.FileHandler(log_path, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )
    logging.getLogger("PIL").setLevel(logging.WARNING)
    logging.info("Logging initialized at %s", log_path)


# --- Deferred imports (so this file can be run before others are implemented) --

def safe_imports():
    """
    Import UI + services lazily and fail gracefully with a helpful message
    if a module is missing while we're developing iteratively.
    """
    try:
        from services.storage import init_db  # noqa: F401
    except Exception as e:  # broad for dev-time clarity
        raise RuntimeError(
            "Missing or broken module: services.storage\n"
            "Create 'services/storage.py' with an 'init_db(db_path: str) -> None' function."
        ) from e

    try:
        from services.summarizer import get_summarizer  # noqa: F401
    except Exception as e:
        raise RuntimeError(
            "Missing or broken module: services.summarizer\n"
            "Create 'services/summarizer.py' exposing 'get_summarizer() -> SummarizerLike'.\n"
            "It should return an object with method: summarize(text: str, max_sentences: int) -> str."
        ) from e

    try:
        from ui.typing_tab import TypingTrainerFrame  # noqa: F401
        from ui.summarize_tab import SummarEaseFrame  # noqa: F401
    except Exception as e:
        raise RuntimeError(
            "Missing UI modules. Create:\n"
            "  - 'ui/typing_tab.py' with class TypingTrainerFrame(ttk.Frame)\n"
            "  - 'ui/summarize_tab.py' with class SummarEaseFrame(ttk.Frame)\n"
            "Both should accept the injected dependencies noted below."
        ) from e


# --- Tk styling / theme -------------------------------------------------------

def init_style() -> ttk.Style:
    style = ttk.Style()
    # Use platform default theme, prefer "clam" fallback for consistency
    try:
        style.theme_use("vista" if sys.platform == "win32" else "clam")
    except tk.TclError:
        style.theme_use(style.theme_names()[0])

    # Fonts & paddings
    style.configure("TLabel", padding=(2, 2))
    style.configure("TButton", padding=(8, 4))
    style.configure("TNotebook", tabmargins=(8, 4, 8, 0))
    style.configure("TNotebook.Tab", padding=(14, 6))
    style.configure("Status.TLabel", anchor="w")

    return style


# --- Global exception hook for Tk ---------------------------------------------

def tk_exception_handler(exc, val, tb):
    logging.exception("Unhandled Tkinter exception", exc_info=(exc, val, tb))
    messagebox.showerror(
        "Unexpected Error",
        f"{exc.__name__}: {val}\n\nSee logs/app.log for details.",
    )


# --- Main Application ---------------------------------------------------------

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        # Reasonable default size; users can resize and it will persist if you add config later
        self.geometry("1000x720")
        self.minsize(820, 600)

        # Hook Tk's exception reporting
        self.report_callback_exception = tk_exception_handler  # type: ignore[attr-defined]

        # Style
        self.style = init_style()

        # Ensure data directories exist & DB is initialized
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        TEXTS_DIR.mkdir(parents=True, exist_ok=True)
        self._init_storage()

        # Obtain summarizer provider (DI)
        self.summarizer = self._get_summarizer()

        # Build UI
        self._build_menu()
        self._build_ui()

        # Keybindings quality-of-life
        self.bind_all("<Control-q>", lambda e: self.on_quit())
        self.bind_all("<Command-q>", lambda e: self.on_quit())  # macOS

        logging.info("%s ready.", APP_NAME)

    # --- Dependency setup -----------------------------------------------------

    def _init_storage(self) -> None:
        # Lazy import now that we can surface nice errors
        from services.storage import init_db
        init_db(str(DB_PATH))
        logging.info("Database initialized at %s", DB_PATH)

    def _get_summarizer(self):
        from services.summarizer import get_summarizer
        # get_summarizer may choose an LLM or an extractive fallback based on env vars
        summarizer = get_summarizer()
        logging.info("Summarizer provider: %s", summarizer.__class__.__name__)
        return summarizer

    # --- UI -------------------------------------------------------------------

    def _build_menu(self):
        menubar = tk.Menu(self)
        # File menu
        file_menu = tk.Menu(menubar, tearoff=False)
        file_menu.add_command(label="Quit", command=self.on_quit, accelerator="Ctrl+Q")
        menubar.add_cascade(label="File", menu=file_menu)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=False)
        help_menu.add_command(label="About", command=self.on_about)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.config(menu=menubar)

    def _build_ui(self):
        # Top-level layout: Notebook + status bar
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)

        self.notebook = ttk.Notebook(container)
        self.notebook.pack(fill="both", expand=True)

        # Import tab classes
        from ui.typing_tab import TypingTrainerFrame
        from ui.summarize_tab import SummarEaseFrame

        # Create tabs with DI hooks:
        # - summarizer is passed to SummarEase
        # - a callback from SummarEase -> Typing to hand off generated text
        self.typing_tab = TypingTrainerFrame(
            self.notebook,
            db_path=str(DB_PATH),
            texts_dir=str(TEXTS_DIR),
        )
        self.summar_tab = SummarEaseFrame(
            self.notebook,
            summarizer=self.summarizer,
            on_text_ready=self._send_text_to_typing,
            db_path=str(DB_PATH),
        )

        self.notebook.add(self.summar_tab, text="SummarEase")
        self.notebook.add(self.typing_tab, text="Typing Trainer")

        # Status bar
        status_bar = ttk.Frame(container)
        status_bar.pack(fill="x", side="bottom")
        self.status_var = tk.StringVar(value="Ready.")
        ttk.Label(status_bar, textvariable=self.status_var, style="Status.TLabel").pack(
            anchor="w", padx=8, pady=2
        )

    # --- Inter-tab communication ---------------------------------------------

    def _send_text_to_typing(self, title: str, content: str) -> None:
        """
        Called by the SummarEase tab when a summary (or original) should become
        the typing target. The Typing tab should expose a method to accept it.
        """
        if not content.strip():
            messagebox.showwarning("No text", "Cannot send empty text to Typing Trainer.")
            return
        # Switch to the Typing tab and inject the text
        try:
            self.typing_tab.set_target_text(title=title, content=content)
            self.notebook.select(self.typing_tab)
            self.set_status(f"Sent '{title}' to Typing Trainer.")
        except Exception as e:
            logging.exception("Failed to hand off text to Typing tab")
            messagebox.showerror("Typing Trainer", f"Failed to load text:\n{e}")

    # --- UX helpers -----------------------------------------------------------

    def set_status(self, msg: str) -> None:
        self.status_var.set(msg)
        # Optionally, we could auto-clear after a short delay:
        self.after(4000, lambda: self.status_var.set("Ready."))

    def on_about(self):
        messagebox.showinfo(
            "About",
            f"{APP_NAME}\n\n"
            "Study smarter and type faster: summarize content, then practice typing it.\n"
            "Built with Tkinter and SQLite.",
        )

    def on_quit(self):
        self.destroy()


# --- Entrypoint ---------------------------------------------------------------

def main():
    configure_logging()

    # Before importing other modules, verify they exist so early errors are clearer.
    try:
        safe_imports()
    except RuntimeError as e:
        configure_logging()  # ensure logging in environments that re-run main
        logging.error(str(e))
        # Show a friendly dialog to help during iterative dev
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Module setup", str(e))
        root.destroy()
        sys.exit(1)

    # Create and run the app
    app = App()
    # Center window on first launch (simple approach)
    app.update_idletasks()
    width = app.winfo_width()
    height = app.winfo_height()
    x = (app.winfo_screenwidth() // 2) - (width // 2)
    y = (app.winfo_screenheight() // 2) - (height // 2)
    app.geometry(f"{width}x{height}+{x}+{y}")

    app.mainloop()


if __name__ == "__main__":
    main()