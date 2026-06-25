"""A/B hook testing — crown the winning hook angle on hero clips.

A hero moment (top predicted score) is cut into several variants — the SAME clip with a
DIFFERENT hook style (clip.py + settings.ab) — sharing an experiment_id. Once the variants
have real views, resolve() picks the winner by views, journals it, and feeds the winning
hook style into optimize's PROVEN preferences so generation biases toward what actually won.
This turns "which angle?" from taste into measured, compounding optimization.
"""
from __future__ import annotations

import json
from typing import Any

import pandas as pd

from . import db, optimize
from .config import ROOT, settings

RESOLVED_PATH = ROOT / "data" / "resolved-experiments.json"


def _read_json(path, default):
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return default


def winners(df: pd.DataFrame) -> list[dict[str, Any]]:
    """For each experiment with >=2 posted variants and enough views, the winning variant.
    Pure read of a clips+metrics frame."""
    if df is None or df.empty or "experiment_id" not in df:
        return []
    min_views = settings().get("ab", {}).get("min_views", 1000)
    out: list[dict[str, Any]] = []
    for exp_id, grp in df[df["experiment_id"].notna()].groupby("experiment_id"):
        posted = grp[grp["status"] == "posted"]
        if len(posted) < 2:
            continue
        views = posted["views"].fillna(0)
        if views.max() < min_views:
            continue
        ranked = views.sort_values(ascending=False)
        win = posted.loc[views.idxmax()]
        out.append({
            "experiment": str(exp_id),
            "winning_hook": str(win.get("hook_type")),
            "winning_views": int(ranked.iloc[0]),
            "variants": int(len(posted)),
            "margin": round(ranked.iloc[0] / max(ranked.iloc[1], 1), 1) if len(ranked) > 1 else 0.0,
        })
    return out


def resolve(db_path=None) -> list[dict[str, Any]]:
    """Crown NEW A/B winners (idempotent): journal them + bias generation toward the winning
    hook styles (optimize's PROVEN list). Returns the freshly-resolved results."""
    df = db.clips_with_latest_metrics(db_path)
    done = set(_read_json(RESOLVED_PATH, []))
    fresh = [w for w in winners(df) if w["experiment"] not in done]
    if not fresh:
        return []
    won_hooks = [w["winning_hook"] for w in fresh if w["winning_hook"] not in ("None", "", "nan")]
    proven = list(dict.fromkeys(won_hooks + _read_json(optimize.AB_WINNERS_PATH, [])))
    optimize.AB_WINNERS_PATH.parent.mkdir(parents=True, exist_ok=True)
    optimize.AB_WINNERS_PATH.write_text(json.dumps(proven))
    optimize.append_log("\n".join([
        "", "### A/B winners",
        *[f"- **{w['winning_hook']}** hook won {w['experiment']} — {w['winning_views']:,} views, "
          f"{w['margin']}× runner-up across {w['variants']} angles" for w in fresh],
        "- → added to PROVEN hook styles; generation now biases toward them.",
    ]))
    RESOLVED_PATH.write_text(json.dumps(sorted(done | {w["experiment"] for w in fresh})))
    return fresh
