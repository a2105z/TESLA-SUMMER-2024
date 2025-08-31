# services/articles.py
"""
Text ingestion & preprocessing utilities for SummarEase Typing Studio.

Goals:
- Minimal dependencies (stdlib only)
- Safe, defensive helpers for reading local files and fetching web pages
- Reasonable HTML-to-text cleanup (strip tags, remove scripts/styles, normalize whitespace)
- Tokenization helpers and readability estimate you can surface in the UI

Exports (most useful):
    read_text_file(path) -> str
    fetch_url_text(url, timeout=12) -> (title: str, text: str)
    sanitize_text(text, max_len=None) -> str
    split_sentences(text) -> List[str]
    tokenize_words(text) -> List[str]
    word_count(text) -> int
    char_count(text, spaces=True) -> int
    flesch_kincaid_grade(text) -> float

Notes:
- `fetch_url_text` uses urllib + basic regex-based stripping; it won't be perfect,
  but it's robust and has no external deps. You can later switch to BeautifulSoup
  with the same return shape if you want higher fidelity.
"""

from __future__ import annotations

import io
import os
import re
import html
import math
import urllib.request
import urllib.error
from typing import List, Tuple, Optional


# --------- Core sanitization ---------

# Remove script/style blocks first, then strip tags
_RE_SCRIPT = re.compile(r"<script\b[^>]*>.*?</script>", re.IGNORECASE | re.DOTALL)
_RE_STYLE = re.compile(r"<style\b[^>]*>.*?</style>", re.IGNORECASE | re.DOTALL)
_RE_TAGS = re.compile(r"<[^>]+>")
_RE_WHITESPACE = re.compile(r"\s+")
_RE_SENT_SPLIT = re.compile(r'(?<=[.!?])\s+')
_RE_WORD = re.compile(r"\b[a-zA-Z']+\b")

def _strip_html(html_text: str) -> str:
    if not html_text:
        return ""
    no_scripts = _RE_SCRIPT.sub(" ", html_text)
    no_styles = _RE_STYLE.sub(" ", no_scripts)
    no_tags = _RE_TAGS.sub(" ", no_styles)
    unescaped = html.unescape(no_tags)
    normalized = _RE_WHITESPACE.sub(" ", unescaped)
    return normalized.strip()


def sanitize_text(text: str, max_len: Optional[int] = None) -> str:
    """
    Normalize whitespace, collapse control chars, optionally clamp to max_len.
    """
    if not text:
        return ""
    # Replace common control chars with spaces
    t = text.replace("\r", " ").replace("\t", " ")
    t = _RE_WHITESPACE.sub(" ", t)
    t = t.strip()
    if max_len is not None and max_len > 0 and len(t) > max_len:
        t = t[:max_len].rstrip()
    return t


# --------- IO helpers ---------

def read_text_file(path: str, encoding: str = "utf-8") -> str:
    with io.open(path, "r", encoding=encoding, errors="ignore") as f:
        return f.read()


def fetch_url_text(url: str, timeout: int = 12) -> Tuple[str, str]:
    """
    Fetch a URL and return (title, text). Best-effort, stdlib-only.
    - Strips scripts/styles/tags
    - Extracts <title> where possible
    """
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "SummarEaseTypingStudio/1.0 (+https://example.local)"
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            # Try to guess encoding from headers; fallback to utf-8
            charset = resp.headers.get_content_charset() or "utf-8"
            html_text = raw.decode(charset, errors="ignore")
    except (urllib.error.URLError, urllib.error.HTTPError, UnicodeDecodeError) as e:
        raise RuntimeError(f"Failed to fetch URL: {e}")

    # Extract title (very simple)
    title = ""
    m = re.search(r"<title[^>]*>(.*?)</title>", html_text, flags=re.IGNORECASE | re.DOTALL)
    if m:
        title = html.unescape(m.group(1)).strip()
        title = _RE_WHITESPACE.sub(" ", title)

    text = _strip_html(html_text)
    return (title or "Untitled Page", text)


# --------- Tokenization & stats ---------

def split_sentences(text: str) -> List[str]:
    t = sanitize_text(text)
    if not t:
        return []
    return [s.strip() for s in _RE_SENT_SPLIT.split(t) if s.strip()]


def tokenize_words(text: str) -> List[str]:
    return _RE_WORD.findall((text or "").lower())


def word_count(text: str) -> int:
    return len(tokenize_words(text))


def char_count(text: str, spaces: bool = True) -> int:
    if not text:
        return 0
    return len(text) if spaces else len(text.replace(" ", ""))


# --------- Readability ---------

def _estimate_syllables(word: str) -> int:
    """
    Very rough syllable estimator:
    - count vowel groups as syllables
    - subtract one if word ends with 'e' and there is more than 1 syllable
    """
    w = word.lower()
    if not w:
        return 0
    groups = re.findall(r"[aeiouy]+", w)
    syl = max(1, len(groups))
    if w.endswith("e") and syl > 1:
        syl -= 1
    return syl


def flesch_kincaid_grade(text: str) -> float:
    """
    Flesch–Kincaid Grade Level (approximate).
    Grade = 0.39*(words/sentences) + 11.8*(syllables/words) - 15.59
    Returns 0.0 if inputs are too small to be meaningful.
    """
    sents = split_sentences(text)
    words = tokenize_words(text)
    if not sents or not words:
        return 0.0

    syllables = sum(_estimate_syllables(w) for w in words)
    words_n = max(len(words), 1)
    sents_n = max(len(sents), 1)

    grade = 0.39 * (words_n / sents_n) + 11.8 * (syllables / words_n) - 15.59
    # Clamp a bit to avoid extreme floats from messy inputs
    return round(max(0.0, min(grade, 20.0)), 2)


# --------- Convenience for future UI hooks ---------

def summarize_ready_text_from_file(path: str, max_len: Optional[int] = None) -> str:
    """ Read a file and return sanitized text ready for summarization/typing. """
    return sanitize_text(read_text_file(path), max_len=max_len)


def summarize_ready_text_from_url(url: str, max_len: Optional[int] = None) -> Tuple[str, str]:
    """ Fetch a URL and return (title, sanitized_text). """
    title, raw = fetch_url_text(url)
    return title, sanitize_text(raw, max_len=max_len)
