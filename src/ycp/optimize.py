"""Stage 8 — OPTIMIZE. The actuator that closes the loop.

scoring.py already says which source creators / formats / hooks WIN (scale) and
LOSE (kill). Nothing acted on that — the loop measured and reported but the next
run sourced the same way regardless. This module turns those verdicts into a
per-creator source-ranking multiplier so the NEXT cycle doubles down on winners
and starves losers, then journals every change to IMPROVEMENT-LOG.md (the system's
running record of how it's getting better).

Learning math is deterministic (driven by scoring.scale_and_kill); only the JSON
weights file + the markdown log have side effects. `today` is injectable so the
log entry is testable without a clock.
"""
from __future__ import annotations

import datetime
import json
from pathlib import Path
from typing import Any

import pandas as pd

from . import db, scoring
from .config import ROOT, settings

WEIGHTS_PATH = ROOT / "data" / "learned-weights.json"      # {creator: source multiplier}
CREATIVE_PATH = ROOT / "data" / "learned-creative.json"    # winning hook styles + length (inferred)
AB_WINNERS_PATH = ROOT / "data" / "ab-winners.json"        # hook styles PROVEN by A/B tests
LOG_PATH = ROOT / "IMPROVEMENT-LOG.md"

# Hook labels that aren't a learnable creative style (skip them when picking winners).
_NON_CREATIVE_HOOKS = {"tbd", "heuristic", "manual", "uncategorized", "", "nan"}

_LOG_HEADER = (
    "# Improvement Log — Phoenix Protocol clip factory\n\n"
    "_Auto-appended by the OPTIMIZE stage each cycle. Newest entries at the bottom._\n"
    "_North star: 100M impressions / month. The loop doubles down on what wins._\n"
)


def _factors() -> dict[str, float]:
    o = settings().get("optimize", {})
    return {
        "boost": float(o.get("boost", 1.5)),       # winners sourced harder
        "suppress": float(o.get("suppress", 0.4)),  # losers sourced less
        "floor": float(o.get("floor", 0.1)),        # never fully zero a creator out
    }


def creator_weights(analysis: dict[str, Any]) -> dict[str, float]:
    """Per-creator source multiplier: scaled winners boosted, killed losers suppressed,
    everyone else implicitly 1.0 (omitted). Pure."""
    by = analysis.get("by_creator")
    if by is None or by.empty:
        return {}
    f = _factors()
    scale, kill = scoring.scale_and_kill(by)
    weights: dict[str, float] = {}
    # Apply kill first, then scale, so a creator in both quantiles (tiny samples) ends up boosted.
    for name in kill.get("source_creator", pd.Series(dtype=str)).tolist():
        weights[name] = max(f["floor"], f["suppress"])
    for name in scale.get("source_creator", pd.Series(dtype=str)).tolist():
        weights[name] = f["boost"]
    return weights


def save_weights(weights: dict[str, float]) -> None:
    WEIGHTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    WEIGHTS_PATH.write_text(json.dumps(weights, indent=2, sort_keys=True))


def load_weights() -> dict[str, float]:
    """Read the learned source multipliers (sourcing applies these). Safe default {}."""
    try:
        return json.loads(WEIGHTS_PATH.read_text())
    except (OSError, ValueError):
        return {}


def creative_prefs(analysis: dict[str, Any]) -> dict[str, Any]:
    """The winning CREATIVE levers — top hook styles + best length — so generation can
    bias toward them (not just sourcing). Pure."""
    by_hook = analysis.get("by_hook")
    prefer_hooks: list[str] = []
    if by_hook is not None and not by_hook.empty:
        prefer_hooks = [h for h in by_hook.head(2)["hook_type"].astype(str).tolist()
                        if h.lower() not in _NON_CREATIVE_HOOKS]
    by_len = analysis.get("by_length")
    prefer_length = (str(by_len.iloc[0]["length_bucket"])
                     if by_len is not None and not by_len.empty else None)
    return {"prefer_hooks": prefer_hooks, "prefer_length": prefer_length}


def save_creative(prefs: dict[str, Any]) -> None:
    CREATIVE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CREATIVE_PATH.write_text(json.dumps(prefs, indent=2, sort_keys=True))


def _load_creative() -> dict[str, Any]:
    try:
        return json.loads(CREATIVE_PATH.read_text())
    except (OSError, ValueError):
        return {}


def preferred_hooks() -> list[str]:
    """Hook styles the loop biases toward — A/B-PROVEN winners first, then inferred winners
    from the scoreboard. The hook agent nudges generation toward these."""
    inferred = _load_creative().get("prefer_hooks") or []
    try:
        proven = json.loads(AB_WINNERS_PATH.read_text())
    except (OSError, ValueError):
        proven = []
    return list(dict.fromkeys([*proven, *inferred]))


def preferred_length() -> str | None:
    """The length bucket currently over-indexing (e.g. '35-45s')."""
    return _load_creative().get("prefer_length")


def _top_rows(rolled: pd.DataFrame, key: str, n: int = 3) -> str:
    if rolled is None or rolled.empty:
        return "—"
    return ", ".join(f"{r[key]} ({r['avg_score']:.0f})" for _, r in rolled.head(n).iterrows())


def format_entry(analysis: dict[str, Any], weights: dict[str, float], today: str) -> str:
    """Human-readable changelog entry: what won, what got cut, what changed, progress."""
    scored = analysis.get("scored")
    n_clips = 0 if scored is None else len(scored)
    total_views = 0 if scored is None or scored.empty else int(scored["views"].fillna(0).sum())
    boosted = sorted(k for k, v in weights.items() if v > 1.0)
    cut = sorted(k for k, v in weights.items() if v < 1.0)
    prefs = creative_prefs(analysis)
    return "\n".join([
        f"## {today}",
        f"- **Sampled:** {n_clips} clips · {total_views:,} total views so far.",
        f"- **Top creators:** {_top_rows(analysis.get('by_creator'), 'source_creator')}",
        f"- **Top formats:** {_top_rows(analysis.get('by_format'), 'fmt')} · "
        f"**lengths:** {_top_rows(analysis.get('by_length'), 'length_bucket')}",
        f"- **Winning hook styles:** {', '.join(prefs['prefer_hooks']) or '— (not learned yet)'} · "
        f"**best length:** {prefs['prefer_length'] or '—'} → fed back into hook generation.",
        f"- **Doubling down on:** {', '.join(boosted) or '— (not enough signal yet)'}",
        f"- **Starving:** {', '.join(cut) or '—'}",
        "- **Why:** winners (top-quantile virality) get sourced harder next cycle + their "
        "hook styles bias generation; losers get throttled. → learned-weights/creative.json.",
    ])


def append_log(entry: str) -> None:
    prior = LOG_PATH.read_text() if LOG_PATH.exists() else _LOG_HEADER
    LOG_PATH.write_text(prior.rstrip() + "\n\n" + entry + "\n")


def run(db_path: Path | None = None, today: str | None = None) -> dict[str, Any]:
    """Analyze captured metrics → learn source weights → persist + journal. Returns summary."""
    today = today or datetime.date.today().isoformat()
    analysis = scoring.analyze(db.clips_with_latest_metrics(db_path))
    weights = creator_weights(analysis)
    prefs = creative_prefs(analysis)
    save_weights(weights)
    save_creative(prefs)
    append_log(format_entry(analysis, weights, today))
    return {
        "clips": 0 if analysis["scored"] is None else len(analysis["scored"]),
        "boosted": sorted(k for k, v in weights.items() if v > 1.0),
        "suppressed": sorted(k for k, v in weights.items() if v < 1.0),
        "prefer_hooks": prefs["prefer_hooks"], "prefer_length": prefs["prefer_length"],
    }
