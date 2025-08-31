# services/summarizer.py
"""
Summarizer providers for SummarEase Typing Studio.

Exports:
- get_summarizer() -> Summarizer
- ExtractiveSummarizer: no-deps, frequency-based extractive summary
- OpenAISummarizer: optional provider guarded by OPENAI_API_KEY

Design:
- Keep a simple interface: summarize(text, max_sentences=5) -> str
- Fail safe: always fall back to ExtractiveSummarizer on any error
"""

from __future__ import annotations

import os
import re
import math
from abc import ABC, abstractmethod
from typing import List, Tuple, Iterable, Dict, Optional


# -----------------------------
# Interface
# -----------------------------

class Summarizer(ABC):
    @abstractmethod
    def summarize(self, text: str, max_sentences: int = 5) -> str:
        ...


# -----------------------------
# Utilities
# -----------------------------

_SENT_SPLIT = re.compile(r'(?<=[.!?])\s+')
_WORD = re.compile(r"\b[a-zA-Z']+\b")

_STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "if", "then", "to", "of", "in",
    "on", "for", "with", "at", "from", "into", "by", "up", "out", "over",
    "below", "above", "after", "before", "is", "are", "was", "were", "be",
    "been", "being", "do", "does", "did", "doing", "as", "it", "its",
    "that", "this", "these", "those", "so", "than", "too", "very", "can",
    "could", "should", "would", "might", "will"
}


def _split_sentences(text: str) -> List[str]:
    # Normalize whitespace; preserve periods for splitting
    t = re.sub(r'\s+', ' ', text).strip()
    if not t:
        return []
    sents = [s.strip() for s in _SENT_SPLIT.split(t) if s.strip()]
    return sents


def _tokens(text: str) -> List[str]:
    return [w for w in _WORD.findall(text.lower())]


def _word_freq(words: Iterable[str]) -> Dict[str, int]:
    freq: Dict[str, int] = {}
    for w in words:
        if w in _STOPWORDS:
            continue
        freq[w] = freq.get(w, 0) + 1
    return freq


def _score_sentence(sent: str, freq: Dict[str, int]) -> float:
    ws = _tokens(sent)
    if not ws:
        return 0.0
    # Sum of term frequencies, normalized by length to reward concise sentences
    return sum(freq.get(w, 0) for w in ws) / (len(ws) + 1)


# -----------------------------
# Providers
# -----------------------------

class ExtractiveSummarizer(Summarizer):
    """
    Lightweight extractive summarizer:
      - Sentence tokenization via regex
      - Word frequency scoring (stopword-light)
      - Picks top-N sentences, keeps original order
    """

    def summarize(self, text: str, max_sentences: int = 5) -> str:
        sents = _split_sentences(text)
        if not sents:
            return ""
        if max_sentences <= 0:
            return ""
        if len(sents) <= max_sentences:
            return " ".join(sents)

        freq = _word_freq(_tokens(text))
        ranked: List[Tuple[float, int, str]] = [
            (_score_sentence(s), i, s) for i, s in enumerate(sents)
        ]
        ranked.sort(key=lambda x: x[0], reverse=True)
        top = sorted(ranked[:max_sentences], key=lambda x: x[1])
        return " ".join(s for _, _, s in top)


class OpenAISummarizer(Summarizer):
    """
    Optional abstractive provider. Used only if OPENAI_API_KEY is present.
    If anything goes wrong (import/network), we fall back to extractive.

    Implementation note:
    - This is intentionally minimal and dependency-guarded.
    - You can swap to your preferred provider; keep the same interface.
    """

    def __init__(self):
        self._available = False
        self._client = None
        try:
            import openai  # type: ignore
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                openai.api_key = api_key
                self._available = True
                self._openai = openai
        except Exception:
            self._available = False
            self._openai = None

        self._fallback = ExtractiveSummarizer()

    def summarize(self, text: str, max_sentences: int = 5) -> str:
        if not self._available:
            return self._fallback.summarize(text, max_sentences)

        prompt = (
            "Summarize the following text into concise, fluent English, using at most "
            f"{max_sentences} sentences. Preserve key facts and context.\n\n=== TEXT START ===\n"
            f"{text}\n=== TEXT END ==="
        )

        try:
            # Minimal, backward-compatible call; adjust to your installed openai version if needed.
            # Newer SDKs: client = OpenAI(); client.chat.completions.create(...)
            import openai  # type: ignore
            resp = openai.ChatCompletion.create(
                model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
                messages=[
                    {"role": "system", "content": "You are a helpful, precise summarizer."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
                max_tokens=800,
            )
            summary = resp["choices"][0]["message"]["content"].strip()
            # Soft guard: ensure we don't exceed roughly the sentence limit (best effort)
            sents = _split_sentences(summary)
            if len(sents) > max_sentences:
                summary = " ".join(sents[:max_sentences])
            return summary
        except Exception:
            # Any error falls back to extractive
            return self._fallback.summarize(text, max_sentences)


# -----------------------------
# Factory
# -----------------------------

def get_summarizer() -> Summarizer:
    """
    Choose provider:
    - If OPENAI_API_KEY present -> try OpenAISummarizer (falls back internally)
    - Else -> ExtractiveSummarizer
    """
    if os.getenv("OPENAI_API_KEY"):
        return OpenAISummarizer()
    return ExtractiveSummarizer()