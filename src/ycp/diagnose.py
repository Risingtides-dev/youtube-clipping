"""WHY analysis — the causal layer on top of the quantitative scoreboard.

scoring/brief RANK what's winning ("make 3× more of creator X · hook Z"). This asks the
harder question — WHY — and returns it as prose: the causal patterns behind winners vs
losers (hook style, topic, length, moment type) plus concrete creative changes for next
cycle. Uses DeepSeek (the same strong model as the hook agent).

Deliberately OPTIONAL and non-blocking: returns None without a key or without enough data,
so the deterministic brief + the cron never depend on it. It augments the brief; it doesn't
gate it. Reuses hooks.py's DeepSeek plumbing.
"""
from __future__ import annotations

import pandas as pd
import requests

from . import hooks

_SYSTEM = (
    "You are the performance analyst for a faceless YouTube Shorts factory. You are given "
    "aggregated clip performance (virality score 0-100, views, by creator / hook style / "
    "length / format) AND hook drop-off by style (% of viewers gone by the end of the hook — "
    "the single sharpest signal of whether a hook is working). Do NOT restate the numbers. "
    "Explain WHY the winners win and the losers lose — the causal pattern in hook style, "
    "topic, emotional trigger, length, and opening moment, leaning on the drop-off data to "
    "pinpoint whether clips fail at the hook or mid-clip. Be specific and falsifiable. Then "
    "give exactly 3 concrete, testable creative changes for next cycle (e.g. 'open more hooks "
    "with a number', 'cut 30-45s clips to 20-30s', 'lead with loss not curiosity for finance'). "
    "Format as short markdown: a '**Why:**' paragraph then a '**Do next:**' list of 3. <180 words."
)

# Need at least this many scored clips before a causal read is worth anything.
_MIN_CLIPS = 6


def _rollup_lines(name: str, df: pd.DataFrame, key: str) -> str:
    if df is None or df.empty:
        return f"{name}: (no data)"
    rows = [f"{r[key]} score={r['avg_score']:.0f} views={int(r['avg_views'])} n={int(r['n'])}"
            for _, r in df.head(5).iterrows()]
    return f"{name}: " + " | ".join(rows)


def _retention_line(scored: pd.DataFrame | None) -> str:
    """Mean hook drop-off (% gone by the hook's end) by hook style — the causal 'why' signal."""
    if scored is None or scored.empty or "swipe_away_pct" not in scored:
        return "Hook drop-off: (no retention data yet)"
    s = scored.dropna(subset=["swipe_away_pct"])
    if s.empty:
        return "Hook drop-off: (no retention data yet)"
    g = s.groupby("hook_type")["swipe_away_pct"].mean().sort_values()
    return ("Hook drop-off by style (lower=better, % gone by hook's end): "
            + " | ".join(f"{k} {v:.0f}%" for k, v in g.items()))


def _facts(analysis: dict) -> str:
    return "\n".join([
        _rollup_lines("By creator", analysis.get("by_creator"), "source_creator"),
        _rollup_lines("By hook style", analysis.get("by_hook"), "hook_type"),
        _rollup_lines("By length", analysis.get("by_length"), "length_bucket"),
        _rollup_lines("By format", analysis.get("by_format"), "fmt"),
        _rollup_lines("By posting hour (channel-local)", analysis.get("by_hour"), "post_hour"),
        _retention_line(analysis.get("scored")),
    ])


def diagnose(analysis: dict, model: str | None = None, timeout: int = 40) -> str | None:
    """Return a markdown WHY analysis, or None if no key / not enough data / API failure."""
    key = hooks._api_key()
    if not key:
        return None
    scored = analysis.get("scored")
    if scored is None or len(scored) < _MIN_CLIPS:
        return None
    model = model or hooks.settings().get("hooks", {}).get("model", hooks.DEFAULT_MODEL)
    try:
        resp = requests.post(
            hooks.DEEPSEEK_URL,
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={"model": model, "temperature": 0.7, "max_tokens": 500,
                  "messages": [{"role": "system", "content": _SYSTEM},
                               {"role": "user", "content": _facts(analysis)}]},
            timeout=timeout)
        resp.raise_for_status()
        text = resp.json()["choices"][0]["message"]["content"].strip()
    except (requests.RequestException, ValueError, KeyError, IndexError):
        return None
    return text or None
