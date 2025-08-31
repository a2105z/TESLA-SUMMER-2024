# tests/test_summarizer.py
import os
import importlib

def test_get_summarizer_defaults_to_extractive(monkeypatch):
    # Ensure no provider key is set so we default to extractive
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    summ_mod = importlib.import_module("services.summarizer")
    s = summ_mod.get_summarizer()
    assert s.__class__.__name__ == "ExtractiveSummarizer"

def test_extractive_basic_summary_respects_sentence_limit():
    from services.summarizer import ExtractiveSummarizer

    text = (
        "Python is a popular programming language. "
        "It is widely used in web development, data science, and automation. "
        "The language emphasizes readability. "
        "Many beginners start with Python due to its simple syntax. "
        "Large companies use it in production systems."
    )

    s = ExtractiveSummarizer()
    out = s.summarize(text, max_sentences=2)

    # should contain at most 2 sentence terminators (quick heuristic)
    # and not be empty
    assert out.strip()
    sent_count = sum(ch in ".!?" for ch in out)
    assert sent_count <= 2

def test_extractive_returns_empty_on_empty_input():
    from services.summarizer import ExtractiveSummarizer
    s = ExtractiveSummarizer()
    assert s.summarize("", max_sentences=5) == ""

def test_extractive_when_limit_exceeds_sentences_returns_original_order():
    from services.summarizer import ExtractiveSummarizer
    s = ExtractiveSummarizer()
    text = "A. B. C."
    out = s.summarize(text, max_sentences=10)
    # original order should be preserved when all sentences are returned
    assert out.replace(" ", "") == "A.B.C."