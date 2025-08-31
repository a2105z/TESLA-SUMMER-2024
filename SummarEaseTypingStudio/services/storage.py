# services/storage.py
"""
SQLite storage layer for SummarEase Typing Studio.

Responsibilities:
- Initialize database schema & pragmas
- CRUD for texts (articles/summaries) and typing runs
- Simple meta key-value store (for future preferences)
- Convenience queries: high score, recent runs, recent texts

All functions accept a db_path so the app can inject the path centrally.
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Iterable, List, Optional, Tuple, Any, Dict


# -----------------------------
# Models
# -----------------------------

@dataclass(frozen=True)
class TextRow:
    id: int
    title: str
    content: str
    created_at: str  # ISO timestamp


@dataclass(frozen=True)
class RunRow:
    id: int
    text_id: Optional[int]
    wpm: float
    accuracy: float
    duration_sec: float
    timestamp: str  # ISO timestamp


# -----------------------------
# Connection helpers
# -----------------------------

def _connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    # Row factory for dict-like access if needed
    conn.row_factory = sqlite3.Row
    # Enforce FK integrity
    conn.execute("PRAGMA foreign_keys = ON;")
    # WAL for better concurrent read/write behavior
    conn.execute("PRAGMA journal_mode = WAL;")
    # A bit more robustness
    conn.execute("PRAGMA synchronous = NORMAL;")
    return conn


@contextmanager
def _cxn(db_path: str):
    conn = _connect(db_path)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


# -----------------------------
# Initialization
# -----------------------------

SCHEMA = """
CREATE TABLE IF NOT EXISTS texts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text_id INTEGER,
    wpm REAL NOT NULL,
    accuracy REAL NOT NULL,
    duration_sec REAL NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(text_id) REFERENCES texts(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS meta (
    key TEXT PRIMARY KEY,
    value TEXT
);

-- Helpful indexes
CREATE INDEX IF NOT EXISTS idx_runs_text_id ON runs(text_id);
CREATE INDEX IF NOT EXISTS idx_runs_timestamp ON runs(timestamp);
CREATE INDEX IF NOT EXISTS idx_texts_created ON texts(created_at);
"""


def init_db(db_path: str) -> None:
    """Create schema and pragmas. Safe to call multiple times."""
    with _cxn(db_path) as conn:
        conn.executescript(SCHEMA)


# -----------------------------
# Texts
# -----------------------------

def insert_text(db_path: str, title: str, content: str) -> int:
    """Insert a new text (article, summary, clipboard). Returns new text id."""
    with _cxn(db_path) as conn:
        cur = conn.execute(
            "INSERT INTO texts (title, content) VALUES (?, ?)",
            (title, content),
        )
        return int(cur.lastrowid)


def get_text(db_path: str, text_id: int) -> Optional[TextRow]:
    with _cxn(db_path) as conn:
        cur = conn.execute(
            "SELECT id, title, content, created_at FROM texts WHERE id = ?",
            (text_id,),
        )
        row = cur.fetchone()
        if not row:
            return None
        return TextRow(
            id=row["id"],
            title=row["title"] or "",
            content=row["content"],
            created_at=row["created_at"],
        )


def list_recent_texts(db_path: str, limit: int = 20) -> List[TextRow]:
    with _cxn(db_path) as conn:
        cur = conn.execute(
            "SELECT id, title, content, created_at FROM texts "
            "ORDER BY created_at DESC, id DESC LIMIT ?",
            (limit,),
        )
        return [
            TextRow(
                id=r["id"],
                title=r["title"] or "",
                content=r["content"],
                created_at=r["created_at"],
            )
            for r in cur.fetchall()
        ]


def delete_text(db_path: str, text_id: int) -> None:
    with _cxn(db_path) as conn:
        conn.execute("DELETE FROM texts WHERE id = ?", (text_id,))


# -----------------------------
# Runs
# -----------------------------

def insert_run(
    db_path: str,
    text_id: Optional[int],
    wpm: float,
    accuracy: float,
    duration_sec: float,
) -> int:
    """Insert a typing run and return its id."""
    with _cxn(db_path) as conn:
        cur = conn.execute(
            "INSERT INTO runs (text_id, wpm, accuracy, duration_sec) VALUES (?, ?, ?, ?)",
            (text_id, float(wpm), float(accuracy), float(duration_sec)),
        )
        return int(cur.lastrowid)


def get_high_score(db_path: str) -> float:
    """Return max WPM across all runs (0 if none)."""
    with _cxn(db_path) as conn:
        cur = conn.execute("SELECT MAX(wpm) AS max_wpm FROM runs")
        row = cur.fetchone()
        return float(row["max_wpm"]) if row and row["max_wpm"] is not None else 0.0


def list_recent_runs(db_path: str, limit: int = 50) -> List[RunRow]:
    with _cxn(db_path) as conn:
        cur = conn.execute(
            "SELECT id, text_id, wpm, accuracy, duration_sec, timestamp "
            "FROM runs ORDER BY timestamp DESC, id DESC LIMIT ?",
            (limit,),
        )
        return [
            RunRow(
                id=r["id"],
                text_id=r["text_id"],
                wpm=float(r["wpm"]),
                accuracy=float(r["accuracy"]),
                duration_sec=float(r["duration_sec"]),
                timestamp=r["timestamp"],
            )
            for r in cur.fetchall()
        ]


def list_runs_for_text(db_path: str, text_id: int, limit: int = 100) -> List[RunRow]:
    with _cxn(db_path) as conn:
        cur = conn.execute(
            "SELECT id, text_id, wpm, accuracy, duration_sec, timestamp "
            "FROM runs WHERE text_id = ? "
            "ORDER BY timestamp DESC, id DESC LIMIT ?",
            (text_id, limit),
        )
        return [
            RunRow(
                id=r["id"],
                text_id=r["text_id"],
                wpm=float(r["wpm"]),
                accuracy=float(r["accuracy"]),
                duration_sec=float(r["duration_sec"]),
                timestamp=r["timestamp"],
            )
            for r in cur.fetchall()
        ]


# -----------------------------
# Meta (key-value)
# -----------------------------

def set_meta(db_path: str, key: str, value: str) -> None:
    with _cxn(db_path) as conn:
        conn.execute(
            "INSERT INTO meta(key, value) VALUES(?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, value),
        )


def get_meta(db_path: str, key: str, default: Optional[str] = None) -> Optional[str]:
    with _cxn(db_path) as conn:
        cur = conn.execute("SELECT value FROM meta WHERE key = ?", (key,))
        row = cur.fetchone()
        return row["value"] if row else default


# -----------------------------
# Utility
# -----------------------------

def vacuum(db_path: str) -> None:
    """Optional maintenance."""
    with _cxn(db_path) as conn:
        conn.execute("VACUUM")


def _as_dict(rows: Iterable[sqlite3.Row]) -> List[Dict[str, Any]]:
    """Handy if you want raw dicts in a pinch."""
    out: List[Dict[str, Any]] = []
    for r in rows:
        out.append({k: r[k] for k in r.keys()})
    return out