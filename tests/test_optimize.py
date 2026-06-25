"""Optimize actuator — learned source weights from the scoreboard (pure logic)."""
from __future__ import annotations

import pandas as pd

from ycp import optimize, scoring


def _clips(creator: str, views: int, n: int = 4) -> list[dict]:
    # min_sample defaults to 4, so each creator needs >=4 clips to count in a rollup.
    return [{
        "clip_id": f"{creator}-{i}", "source_creator": creator,
        "fmt": "auto-clip", "hook_type": "Curiosity Gap", "platform": "youtube",
        "views": views, "length_sec": 30, "ad_revenue": 0.0, "retention_pct": 0.0,
    } for i in range(n)]


def _analysis(rows: list[dict]) -> dict:
    return scoring.analyze(pd.DataFrame(rows))


def test_creator_weights_boost_winner_starve_loser():
    rows = _clips("Winner", 500_000) + _clips("Middle", 50_000) + _clips("Loser", 1_000)
    weights = optimize.creator_weights(_analysis(rows))
    assert weights.get("Winner", 1.0) > 1.0       # top quantile → boosted
    assert weights.get("Loser", 1.0) < 1.0        # bottom quantile → starved
    assert weights["Loser"] >= optimize._factors()["floor"]  # never fully zeroed


def test_creator_weights_empty_when_no_data():
    assert optimize.creator_weights({"by_creator": pd.DataFrame()}) == {}


def test_weights_roundtrip_and_log(tmp_path, monkeypatch):
    monkeypatch.setattr(optimize, "WEIGHTS_PATH", tmp_path / "w.json")
    monkeypatch.setattr(optimize, "LOG_PATH", tmp_path / "LOG.md")
    optimize.save_weights({"Winner": 1.5, "Loser": 0.4})
    assert optimize.load_weights() == {"Winner": 1.5, "Loser": 0.4}

    rows = _clips("Winner", 500_000) + _clips("Loser", 1_000)
    entry = optimize.format_entry(_analysis(rows), {"Winner": 1.5, "Loser": 0.4}, today="2026-06-24")
    optimize.append_log(entry)
    text = (tmp_path / "LOG.md").read_text()
    assert "2026-06-24" in text and "Doubling down on:" in text and "Winner" in text


def test_load_weights_missing_file_is_empty(tmp_path, monkeypatch):
    monkeypatch.setattr(optimize, "WEIGHTS_PATH", tmp_path / "nope.json")
    assert optimize.load_weights() == {}


def test_creative_prefs_picks_winning_hook_excludes_tbd():
    rows = (_clips_h("Curiosity Gap", 400_000, 30) + _clips_h("tbd", 500, 50))
    prefs = optimize.creative_prefs(_analysis(rows))
    assert "Curiosity Gap" in prefs["prefer_hooks"]
    assert "tbd" not in prefs["prefer_hooks"]   # non-creative label filtered out
    assert prefs["prefer_length"] == "25-35s"   # the winning (high-view) clips are 30s


def test_creative_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr(optimize, "CREATIVE_PATH", tmp_path / "c.json")
    optimize.save_creative({"prefer_hooks": ["Curiosity Gap"], "prefer_length": "25-35s"})
    assert optimize.preferred_hooks() == ["Curiosity Gap"]
    assert optimize.preferred_length() == "25-35s"


def _clips_h(hook: str, views: int, length: int, n: int = 4) -> list[dict]:
    return [{"clip_id": f"{hook}-{length}-{i}", "source_creator": "C", "fmt": "auto-clip",
             "hook_type": hook, "platform": "youtube", "views": views,
             "length_sec": length, "ad_revenue": 0.0, "retention_pct": 0.0} for i in range(n)]
