"""A/B hook testing — pure winner-picking (no DB/network)."""
from __future__ import annotations

import pandas as pd

from ycp import experiment


def _df(rows: list[dict]) -> pd.DataFrame:
    return pd.DataFrame(rows)


def _ab(monkeypatch, min_views: int = 1000) -> None:
    monkeypatch.setattr(experiment, "settings", lambda: {"ab": {"min_views": min_views}})


def test_winners_picks_highest_views(monkeypatch):
    _ab(monkeypatch)
    rows = [
        {"clip_id": "a-v0", "experiment_id": "E", "status": "posted", "views": 5000,
         "hook_type": "Curiosity Gap"},
        {"clip_id": "a-v1", "experiment_id": "E", "status": "posted", "views": 1200,
         "hook_type": "Contrarian"},
    ]
    w = experiment.winners(_df(rows))
    assert len(w) == 1
    assert w[0]["winning_hook"] == "Curiosity Gap" and w[0]["variants"] == 2
    assert w[0]["margin"] == round(5000 / 1200, 1)


def test_winners_wait_for_min_views(monkeypatch):
    _ab(monkeypatch)
    rows = [{"clip_id": "a-v0", "experiment_id": "E", "status": "posted", "views": 50,
             "hook_type": "X"},
            {"clip_id": "a-v1", "experiment_id": "E", "status": "posted", "views": 40,
             "hook_type": "Y"}]
    assert experiment.winners(_df(rows)) == []   # not enough signal to crown a winner


def test_winners_need_two_posted_variants(monkeypatch):
    _ab(monkeypatch)
    rows = [{"clip_id": "a-v0", "experiment_id": "E", "status": "posted", "views": 9000,
             "hook_type": "X"},
            {"clip_id": "a-v1", "experiment_id": "E", "status": "pending_qc", "views": 0,
             "hook_type": "Y"}]
    assert experiment.winners(_df(rows)) == []   # only one is live — nothing to compare


def test_winners_ignores_non_experiment_clips():
    assert experiment.winners(pd.DataFrame([{"clip_id": "x", "status": "posted", "views": 9}])) == []
