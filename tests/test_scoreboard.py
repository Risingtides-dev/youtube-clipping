"""Scoreboard engine — deterministic game-state math + rendering."""
from __future__ import annotations

import pandas as pd

from ycp import scoreboard as sb


def _df(rows: list[dict]) -> pd.DataFrame:
    return pd.DataFrame(rows)


def test_empty_is_boot_up():
    s = sb.compute(pd.DataFrame())
    assert s["run_rate"] == 0 and s["clips"] == 0 and s["level_n"] == 1
    md = sb.build(pd.DataFrame())
    assert "Boot Up" in md and "Race to $15K" in md


def test_level_mapping():
    assert sb._level(0)[1][1] == "Boot Up"
    assert sb._level(1)[1][1] == "First Blood"
    assert sb._level(600)[1][1] == "Signal"
    assert sb._level(2_500)[1][1] == "Traction"
    assert sb._level(15_000)[1][1] == "GOAL"
    assert sb._level(99_999)[2] is None  # nothing past GOAL


def test_bar_bounds():
    assert sb._bar(0) == "▱" * 24
    assert sb._bar(1) == "▰" * 24
    assert len(sb._bar(0.5)) == 24
    assert len(sb._bar(2.0)) == 24  # clamps over 1.0


def test_compute_revenue_hits_and_quests():
    df = _df([
        {"clip_id": "a", "channel": "ch1", "status": "posted", "source_creator": "Jubilee",
         "views": 200_000, "whop_payout": 0.0, "ad_revenue": 50.0},
        {"clip_id": "b", "channel": "ch1", "status": "posted", "source_creator": "Flagrant",
         "views": 5_000, "whop_payout": 10.0, "ad_revenue": 0.0},
    ])
    s = sb.compute(df)
    assert s["run_rate"] == 60.0
    assert s["hits"] == 1 and s["channels"] == 1 and s["clips"] == 2
    q1 = next(q for q in s["quests"] if q[0].startswith("1 ·"))
    assert "LIVE" in q1[1]  # Jubilee feeds quest 1


def test_build_renders_leaderboard_and_level_up():
    df = _df([{"clip_id": "a", "channel": "ch1", "status": "posted", "source_creator": "X",
               "views": 1000, "whop_payout": 7_000.0, "ad_revenue": 0.0}])
    md = sb.build(df)
    assert "Race to $15K" in md and "ch1" in md
    assert "Engine" in md  # $7K run-rate -> Level 5 Engine
