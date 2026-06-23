"""The gamified scoreboard — the "Race to $15K" game state, from real loop data.

Turns the closed-loop DB (clips + captured metrics + revenue) into a single
glanceable game: your level, your monthly run-rate, the milestone ladder, the
channel leaderboard, and the concept "quests" and their go/no-go gates. This is
the hands-off operator's dashboard — you read this, not the guts.

Fully deterministic (pure pandas + rules), like brief.py. `ycp scoreboard`
regenerates SCOREBOARD.md every time the loop runs, so the game keeps score for
you automatically. No LLM, reproducible, unit-tested.
"""
from __future__ import annotations

from datetime import date

import pandas as pd

GOAL = 15_000  # $/month — the win condition

# (monthly run-rate threshold, name, badge, one-line meaning)
LEVELS = [
    (0,       "Boot Up",    "🟢", "system built — channels not live yet"),
    (1,       "First Blood", "🩸", "first dollar earned / first channel live"),
    (500,     "Signal",     "📡", "$500/mo — a format is working"),
    (2_500,   "Traction",   "🚀", "$2.5K/mo — the loop is compounding"),
    (6_000,   "Engine",     "⚙️", "$6K/mo — scale the proven winners"),
    (10_000,  "Cruise",     "🛞", "$10K/mo — most of the way home"),
    (GOAL,    "GOAL",       "🏁", "$15K/mo — WIN. Then push Overdrive."),
]

HIT_VIEWS = 100_000  # a clip at/above this is a "hit"

# concept (quest) -> the source creators that feed it, to detect when it's live.
# Mirrors CHANNEL-CONCEPTS.md / niches.yaml. Demo creators included so `ycp demo`
# data lights up quests too.
QUESTS = [
    ("1 · Hot Seat (debate/agitation)", "owned",
     ["Jubilee", "Whatever (clips)", "No Jumper", "Pop Culture Crisis",
      "Modern Day Debate", "Flagrant"]),
    ("2 · Money Fights (finance conflict)", "owned",
     ["Ramit Sethi", "Graham Stephan", "Codie Sanchez", "My First Million",
      "Alex Hormozi", "Gary Vaynerchuk"]),
    ("3 · Cash Engine (paid campaigns)", "whop",
     ["Diary of a CEO", "Iced Coffee Hour", "Iman Gadzhi", "Jay Shetty"]),
    ("4 · Crash Out (comedy/reaction)", "owned",
     ["Bad Friends", "Kill Tony", "This Is Important", "ModernWisdom"]),
    ("5 · Myth-Busting (health/fitness)", "owned",
     ["Dr Mike Israetel", "Bryan Johnson", "Jeff Nippard", "Dr Gabrielle Lyon"]),
]


def _level(run_rate: float) -> tuple[int, tuple, tuple | None]:
    """Return (level_index_1based, current_level_tuple, next_level_tuple|None)."""
    idx = 0
    for i, lvl in enumerate(LEVELS):
        if run_rate >= lvl[0]:
            idx = i
    nxt = LEVELS[idx + 1] if idx + 1 < len(LEVELS) else None
    return idx + 1, LEVELS[idx], nxt


def _bar(pct: float, width: int = 24) -> str:
    pct = max(0.0, min(1.0, pct))
    fill = round(pct * width)
    return "▰" * fill + "▱" * (width - fill)


def _money(x: float) -> str:
    return f"${x:,.0f}" if x >= 100 else f"${x:,.2f}"


def _views(x: float) -> str:
    return (f"{x/1_000_000:.1f}M" if x >= 1_000_000
            else f"{x/1_000:.0f}K" if x >= 1000 else f"{x:.0f}")


def compute(df: pd.DataFrame) -> dict:
    """Reduce the clips+metrics frame to the game state. Pure."""
    if df.empty:
        lvl_n, lvl, nxt = _level(0)
        return {"run_rate": 0.0, "views": 0, "clips": 0, "posted": 0, "channels": 0,
                "hits": 0, "hit_rate": 0.0, "whop": 0.0, "ads": 0.0, "best": None,
                "level_n": lvl_n, "level": lvl, "next": nxt, "leaderboard": [],
                "quests": [(q[0], "⬜ queued — spin up a channel", 0, 0.0) for q in QUESTS]}

    d = df.copy()
    d["views"] = pd.to_numeric(d["views"], errors="coerce").fillna(0)
    whop = pd.to_numeric(d.get("whop_payout", 0), errors="coerce").fillna(0)
    ads = pd.to_numeric(d.get("ad_revenue", 0), errors="coerce").fillna(0)
    d["_rev"] = whop + ads
    run_rate = float(d["_rev"].sum())  # v1: captured revenue = run-rate proxy
    views = int(d["views"].sum())
    posted = int((d.get("status", "") == "posted").sum())
    n = len(d)
    channels = int(d["channel"].nunique()) if "channel" in d else 0
    hits = int((d["views"] >= HIT_VIEWS).sum())
    best_i = d["views"].idxmax()
    best = {"channel": d.loc[best_i].get("channel", "?"),
            "views": int(d.loc[best_i, "views"]),
            "creator": d.loc[best_i].get("source_creator", "?")}
    lb = (d.groupby("channel")
          .agg(views=("views", "sum"), rev=("_rev", "sum"), n=("clip_id", "count"))
          .sort_values("rev", ascending=False).head(5).reset_index())
    leaderboard = [(r["channel"], int(r["views"]), float(r["rev"]), int(r["n"]))
                   for _, r in lb.iterrows()]

    quests = []
    creators = set(d.get("source_creator", pd.Series(dtype=str)).dropna())
    for name, _lane, feeders in QUESTS:
        live = [c for c in feeders if c in creators]
        if live:
            sub = d[d["source_creator"].isin(live)]
            qv, qr = int(sub["views"].sum()), float(sub["_rev"].sum())
            status = f"🟢 LIVE — {len(sub)} clips · {_views(qv)} views · {_money(qr)}"
            quests.append((name, status, len(sub), qr))
        else:
            quests.append((name, "⬜ queued — spin up a channel", 0, 0.0))

    lvl_n, lvl, nxt = _level(run_rate)
    return {"run_rate": run_rate, "views": views, "clips": n, "posted": posted,
            "channels": channels, "hits": hits, "hit_rate": hits / n if n else 0.0,
            "whop": float(whop.sum()), "ads": float(ads.sum()), "best": best,
            "level_n": lvl_n, "level": lvl, "next": nxt,
            "leaderboard": leaderboard, "quests": quests}


def build(df: pd.DataFrame, as_of: str | None = None) -> str:
    """Render SCOREBOARD.md from the game state. Deterministic."""
    s = compute(df)
    as_of = as_of or date.today().isoformat()
    pct = s["run_rate"] / GOAL
    lvl = s["level"]
    nxt = s["next"]
    if nxt:
        gap = nxt[0] - s["run_rate"]
        next_line = f"**Next:** {nxt[2]} {nxt[1]} at {_money(nxt[0])}/mo — {_money(max(gap,0))} to go."
    else:
        next_line = "**🏁 GOAL CLEARED. You win. Push to Overdrive.**"

    ladder = []
    for thresh, name, badge, meaning in LEVELS:
        lit = "✅" if s["run_rate"] >= thresh else "⬜"
        here = " ◀ **YOU**" if name == lvl[1] else ""
        ladder.append(f"| {lit} | {badge} {name} | {_money(thresh)}/mo | {meaning}{here} |")

    if s["leaderboard"]:
        lb = ["| # | channel | views | revenue | clips |", "|---|---|---|---|---|"]
        for i, (ch, v, r, nclips) in enumerate(s["leaderboard"], 1):
            lb.append(f"| {i} | {ch} | {_views(v)} | {_money(r)} | {nclips} |")
        leaderboard = "\n".join(lb)
    else:
        leaderboard = "_(no posted clips yet — leaderboard fills as channels go live)_"

    quests = "\n".join(f"- **{name}** — {status}" for name, status, _n, _r in s["quests"])

    best = (f"{_views(s['best']['views'])} views — {s['best']['channel']} "
            f"(from {s['best']['creator']})") if s["best"] else "—"

    return f"""# 🏁 Race to $15K — Scoreboard

_Auto-generated by `ycp scoreboard` from the closed-loop DB · as of {as_of}._

## {lvl[2]} Level {s['level_n']} — {lvl[1]}

### {_money(s['run_rate'])}/mo  ·  {_bar(pct)}  {pct*100:.1f}% to $15K

{next_line}

| stat | value |
|---|---|
| 💵 Monthly run-rate | **{_money(s['run_rate'])}** (Whop {_money(s['whop'])} · ads {_money(s['ads'])}) |
| 👀 Views captured | {_views(s['views'])} |
| 🎬 Clips (posted / total) | {s['posted']} / {s['clips']} |
| 📺 Channels live | {s['channels']} |
| 🎯 Hit-rate (clips ≥100K) | {s['hit_rate']*100:.0f}%  ({s['hits']} hits) |
| 🏆 Best clip | {best} |

## 🪜 Milestone ladder
| | level | gate | meaning |
|---|---|---|---|
{chr(10).join(ladder)}

## 🗺️ Quests (the 5 concepts — clear each go/no-go gate to scale it)
{quests}

## 🏅 Channel leaderboard
{leaderboard}

---
> The loop keeps score: every `ycp capture` + `ycp brief` cycle updates these numbers.
> Climb the ladder by making more of what the Double-Down Brief says wins. 🏁
"""
