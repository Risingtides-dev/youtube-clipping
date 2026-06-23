# Research Log — discovery toward "the portfolio that clears $15K/month"

Append-only. Newest cycle on top. Each entry: what was discovered/scored/validated ·
evidence · what got promoted · the new top discovery gap. The loop reads this first every
cycle (see `RESEARCH-GOAL-AND-LOOP.md`).

---

## 🧭 Discovery scorecard (target: validated portfolio → $15K/month)

| | Value | Notes |
|---|---|---|
| Source pages scored | **33** | Exit target ≥30 ✓ (Cycle 2). 24 promoted to niches.yaml. |
| Channel concepts defined | **5** (incl. 1 agitation) | Exit target 3–5 ✓. Each has feeders + go/no-go test. |
| Promoted to `niches.yaml` | **21 creators / 5 niches** | `load_creators()` parses clean; all URLs resolve. |
| Live re-rank off Double-Down Brief | **not yet** | No channels live → no `data/latest-brief.md` yet. Opens once Concept 3 ships. |
| Top discovery gap now | **`ycp source` queue is empty on real channels** | yt-dlp *flat* mode returns no view_count → rank() drops everything at min_views. Ops-side fix needed (see below). |

---

## Cycle 2 — Close the source gap: 33 scored, Whatever surface resolved (2026-06-22)

**Orient:** gap was "29 < 30 target + stale Whatever handle + no Cuban velocity."
**Discover/score (real yt-dlp):** resolved + scored 4 new sources —
- **@whatever2ND** (ROS 65.3) — the LIVE Whatever clip surface (fresh 0d), replacing the stale main handle for debate sourcing.
- **@AlexHormozi** (ROS 67.6) — 9,713 views/hr, business/MMO, clip-tolerated. Top-tier velocity source.
- **@garyvee** (ROS 55.4) — *explicitly encourages clipping* (top compliance), business RPM.
- **@ColinandSamir** (ROS 54.2) — creator-economy interviews; kept on the bench.
**Promote:** +3 to niches.yaml (@whatever2ND, @AlexHormozi, @garyvee) → 24 creators. `load_creators()` parses clean.
**Couldn't verify:** Mark Cuban/Trailblazers YT handle (@Trailblazers = NBA; @TrailblazersPodcast = wrong show) — stays agent-sourced on the board. @WhateverPodcastClips + @biolayne still 404 on yt-dlp.
**Exit criterion #1 (≥30 scored) now MET: 33.**
**New bottleneck:** unchanged sourcing flat-fix (ops loop / task chip) — AND the system has no AUTOPILOT yet (orchestration + gamified scoreboard). That's the next build (Eric's directive 2026-06-22).

## Cycle 1 — Bootstrap: 29 sources scored, 5 concepts, niches.yaml seeded (2026-06-22)

**Orient:** all three working files were empty — the binding gap was "zero real scored
sources, zero defined angles." Cycle 1 = create them with a real first batch.

**Discover (real data pulled):**
- **Velocity:** live yt-dlp non-flat scan of 29 candidate channels (top-4 recent uploads
  each) → real peak views/hour. Parallelized via Python threadpool (the repo's flat-mode
  `sourcing._ytdlp_json` returns no view_count for these channels — see gap below).
- **Live campaigns (historical — Whop cut 2026-06):** swept the paid-clipping economy — verified funded pools
  (Coinbase $3/1k ~95% left, Boring Money $1.50/1k, Shesbirdie $1.75/1k, Roobet $250k pool,
  Mark Cuban $1/1k ~60%), plus paid YouTube sources (Diary of a CEO/Clipster, Iman Gadzhi,
  Jay Shetty, Iced Coffee Hour).
- **Angles:** mapped the debate/agitation economy (Jubilee, Whatever, No Jumper, Modern Day
  Debate, Pop Culture Crisis) + the exact policy line (position-attack = safe; protected-group
  attack = struck; Fresh & Fit as the cautionary boundary; Jan 2026 monetization expansion).

**Score:** ran the ROS rubric (.30/.25/.15/.15/.10/.05) on all 29 with real velocity +
evidence-based 0–1 dimension ratings → `SOURCE-INTELLIGENCE.md`. Top 5: Diary of a CEO 86.5 ·
Jubilee 81.8 · Ramit Sethi 72.6 · Bad Friends 71.6 · Iced Coffee Hour 71.1.

**Angle:** 5 concepts in `CHANNEL-CONCEPTS.md`, each with thesis + feeders + format/hook +
lane + a hard go/no-go gate. Concept 1 ("Hot Seat" debate flashpoints) is the agitation bet,
with the position-vs-protected-group guardrail baked in.

**Validate (real evidence, not asserted):**
- *Debate angle:* Jubilee's 51,725 views/hr (live) + structured-debate policy carve-out +
  documented comparable wins (Mehdi Hasan Surrounded, "who pays" 1.8M clip). **Greenlit.**
- *Finance-conflict angle:* Ramit "Money for Couples" — real format, US-top-RPM, verified
  under-clipped (thin existing field). **Greenlit as highest-EV open lane.**
- *Business/finance authority:* Mark Cuban/Trailblazers — low saturation, high-RPM owned source.
  **Greenlit as an owned-channel source.** _(Originally scoped as paid cash engine; Whop cut 2026-06.)_

**Promote:** 21 validated creators → `config/niches.yaml`, grouped by the concept each feeds.
**Verified:** `sourcing.load_creators()` → 21 creators / 5 niches, 0 bad URLs.

**Evidence it works:** velocity numbers are live (not estimated); `load_creators()` parses
clean; ROS is reproducible (deterministic script, weights sum to 1.0); every greenlit concept
cites real velocity / a live funded pool / a named comparable win.

**New bottleneck (handed to the OPS loop):** `ycp source` won't produce a live queue yet —
`sourcing._ytdlp_json` uses `--flat-playlist`, which returns `view_count: None` for these
channels (confirmed: @ChrisWillx flat dump → all None), so `rank()` drops everything at
`min_views: 50000`. **The proven fix:** the non-flat `--print` extraction used in this cycle's
scan (real views + timestamp). Tradeoff to design: non-flat is slower per video, so likely
"flat for IDs → non-flat on top-N per creator," or accept a small per-creator window. This is
an ops/throughput fix, not a research task — flagged for `GOAL-AND-LOOP.md`.

**Next cycle target:** (1) close the source gap to ≥30 — resolve the live Whatever-clips
handles (`@WhateverPodcastClips` 404'd) and add the Mark Cuban handle with a live velocity
pull; (2) once Concept 3 ships and `data/latest-brief.md` exists, run the first re-rank: scale
the feeders behind whatever's winning, cut the dead weight.
