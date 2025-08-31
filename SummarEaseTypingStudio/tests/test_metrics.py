# tests/test_metrics.py
# We import the helper functions from ui.typing_tab since that's where the
# WPM/accuracy formulas live in the current codebase.

def test_wpm_basic():
    from ui.typing_tab import _compute_wpm
    # 250 chars in 60 seconds => 50 words (assuming 5 chars/word) => 50 WPM
    assert _compute_wpm(250, 60.0) == 50

def test_wpm_guard_against_zero_time():
    from ui.typing_tab import _compute_wpm
    # Should not crash; extremely small elapsed should still produce a large number
    wpm = _compute_wpm(50, 0.0)
    assert isinstance(wpm, int)

def test_accuracy_full_correct():
    from ui.typing_tab import _compute_accuracy
    assert _compute_accuracy(correct=100, total=100) == 100.0

def test_accuracy_half_correct():
    from ui.typing_tab import _compute_accuracy
    assert _compute_accuracy(correct=5, total=10) == 50.0

def test_accuracy_zero_total_is_100():
    from ui.typing_tab import _compute_accuracy
    # By convention we report 100% when nothing is typed yet
    assert _compute_accuracy(correct=0, total=0) == 100.0
