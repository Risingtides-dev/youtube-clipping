"""Hook optimizer — pure scoring, safety, and fallback (no API/network)."""
from __future__ import annotations

from ycp import autopilot, hooks


def test_score_rewards_curiosity_and_stakes_over_bland():
    punchy = hooks.score_hook("Why nobody tells you this money mistake")
    bland = hooks.score_hook("A video about some financial topics today")
    assert punchy > bland


def test_score_rewards_punchy_length():
    short = hooks.score_hook("This always happens before a crash")
    rambling = hooks.score_hook(
        "Here is a very long winded title that simply will not stop going on and on")
    assert short > rambling


def test_finance_angle_bonus():
    base = hooks.score_hook("Watch this before you act")
    moneyed = hooks.score_hook("Watch this before you go broke", angle="finance")
    assert moneyed > base


def test_looks_safe_blocks_slurs_allows_opinion():
    assert hooks.looks_safe("This economic policy is a complete scam")
    assert not hooks.looks_safe("these people are groomers")  # protected-group attack


def test_best_hook_falls_back_when_no_candidates(monkeypatch):
    # Force the LLM path to return nothing -> heuristic fallback still yields a title.
    monkeypatch.setattr(hooks, "generate_candidates", lambda *a, **k: [])
    out = hooks.best_hook("Why does nobody talk about this? It changes everything.")
    assert out and "?" in out  # heuristic prefers the question


def test_best_hook_picks_highest_scoring_safe_candidate(monkeypatch):
    monkeypatch.setattr(hooks, "generate_candidates", lambda *a, **k: [
        {"text": "a bland line here", "type": "Reframe", "fit": 0.3},
        {"text": "Why this money mistake ruins you", "type": "Curiosity Gap", "fit": 0.9},
    ])
    out = hooks.best_hook("transcript", angle="finance")
    assert out == "Why this money mistake ruins you"


def test_context_fit_drives_selection(monkeypatch):
    # A high agent-fit hook should win even if a rival scores slightly better on the
    # deterministic heuristic — the agent has the video context.
    monkeypatch.setattr(hooks, "generate_candidates", lambda *a, **k: [
        {"text": "Why nobody tells you this", "type": "Curiosity Gap", "fit": 0.2},
        {"text": "Buy a business not a job", "type": "Contrarian", "fit": 0.95},
    ])
    assert hooks.best_hook("transcript", angle="finance") == "Buy a business not a job"


def test_best_returns_text_and_type(monkeypatch):
    monkeypatch.setattr(hooks, "generate_candidates", lambda *a, **k: [
        {"text": "the cardio pace that adds years:", "type": "Curiosity Gap", "fit": 0.9}])
    r = hooks.best("transcript")
    assert r["text"] == "the cardio pace that adds years:" and r["type"] == "Curiosity Gap"


def test_best_heuristic_fallback_marks_type(monkeypatch):
    monkeypatch.setattr(hooks, "generate_candidates", lambda *a, **k: [])
    r = hooks.best("Why does nobody talk about this? It matters.")
    assert r["text"] and r["type"] == "heuristic"


def test_prefer_types_nudge_breaks_the_tie(monkeypatch):
    # Same text (same heuristic); Reframe has higher fit, but Pattern Interrupt is a learned
    # winner → the +0.1 nudge flips selection to it.
    monkeypatch.setattr(hooks, "generate_candidates", lambda *a, **k: [
        {"text": "identical style line", "type": "Reframe", "fit": 0.72},
        {"text": "identical style line", "type": "Pattern Interrupt", "fit": 0.70}])
    assert hooks.best("t", prefer_types=["Pattern Interrupt"])["type"] == "Pattern Interrupt"


def test_variants_returns_distinct_styles(monkeypatch):
    monkeypatch.setattr(hooks, "generate_candidates", lambda *a, **k: [
        {"text": "contrarian take here", "type": "Contrarian", "fit": 0.9},
        {"text": "another contrarian one", "type": "Contrarian", "fit": 0.8},
        {"text": "curiosity gap hook", "type": "Curiosity Gap", "fit": 0.85},
        {"text": "pattern interrupt line", "type": "Pattern Interrupt", "fit": 0.7}])
    v = hooks.variants("moment", k=3)
    types = [x["type"] for x in v]
    assert len(v) == 3 and len(set(types)) == 3   # 3 DIFFERENT angles for the A/B test


def test_coerce_accepts_string_and_dict():
    assert hooks._coerce_candidate("Hook text")["text"] == "Hook text"
    assert hooks._coerce_candidate({"text": "X", "type": "Reframe", "fit": "0.8"})["fit"] == 0.8
    assert hooks._coerce_candidate({"text": ""}) is None
    assert hooks._coerce_candidate({"text": "Y", "fit": "bad"})["fit"] == 0.5  # bad fit → default


def test_playbook_loads_the_real_skill():
    hooks._playbook.cache_clear()
    pb = hooks._playbook()
    # Grounded in the Undertow framework, not a generic prompt.
    assert "hook" in pb.lower()
    assert "Contrarian" in pb and "Pattern Interrupt" in pb
    assert "Undertow" in pb


def test_angle_mapping():
    assert autopilot.angle_for("debate-agitation") == "agitation"
    assert autopilot.angle_for("finance-money-fights") == "finance"
    assert autopilot.angle_for("comedy-reaction") == ""
    assert autopilot.angle_for(None) == ""
