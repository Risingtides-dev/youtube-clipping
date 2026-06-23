# 🤖 AUTOPILOT-LOG — the autopilot loop's memory

Append-only build log for `AUTOPILOT-GOAL-AND-LOOP.md`. Each entry: what shipped, the
evidence it works, the remaining human-touch count, and the new #1 autonomy bottleneck.

**Day-0 baseline (2026-06-22):** 🟢 Boot Up · $0/mo · 0 channels live · scoreboard at Level 1.

---

## 2026-06-22 — Cycles 1–5 + hook agent (session build)

Built the autonomy backbone end-to-end. Verified: `ruff` clean · **58 tests pass**
(`pytest -k "not cut_vertical"`) · live commands run where the network/machine allows.

### ✅ Shipped
1. **Cycle 1 — `ycp source` fixed + hardened.** Bug was `yt-dlp --flat-playlist` →
   `view_count=None` → `rank()` dropped everything at `min_views`. Fix: flat enumerate for
   IDs → non-flat `--print` metadata on the top-N recent per creator (`meta_fetch`), parsed
   by a pure `_parse_meta_lines`. Added **creator-level concurrency** (ThreadPoolExecutor).
   *Evidence:* empty → **52 real ranked videos** with live view counts; **2m14s** (was
   heading >20min). Jubilee top velocity 51,595/hr matches SOURCE-INTELLIGENCE's recorded 51,725/hr.
2. **Cycle 2 — orchestrator `ycp autopilot`** (`src/ycp/autopilot.py` + `scripts/autopilot.sh`
   + launchd plist). Chains source→clip→qc→capture→brief→scoreboard; fault-isolated per stage;
   idempotent (skips already-clipped sources via `source_video_id`). *Evidence:* **7/7 stages
   clean** on `--skip-source --no-clip`. Schedule artifacts created but NOT enabled (premature
   until distribution + channels live).
3. **Cycle 3 — hook agent** (`src/ycp/hooks.py`, Eric's ask). Generates N viral hook candidates →
   pure heuristic scorer → best; safety-screened; wired into `clip.run` with a niche→angle map.
   **Model: DeepSeek** (`deepseek-chat`) — NOT a local model (see Decisions). Heuristic fallback
   when no key. **Hook copywriting skill:** the agent's system prompt is `config/hook-playbook.md`
   — distilled from the Undertow framework (5 hook types + structural principles + levers + angle
   tuning), editable without code change. *Evidence:* scoring/safety/fallback/playbook unit-tested
   + verified live (fallback path); live DeepSeek path pending the 1Password key.
4. **Cycle 4 — guardrails in code** (`src/ycp/guardrails.py`). Avoid-list gate inside sourcing
   (drops JRE/Tate/Fresh&Fit/Huberman/mega-creators + music/casino titles BEFORE ranking) +
   `publish_allowed` (transformed + no-music check). *Evidence:* wired into `sourcing.run`; tested.
5. **Cycle 5 — distribution adapter** (`src/ycp/distribute.py`). Repurpose.io outbox adapter
   (drop approved clip + JSON sidecar into a watched folder) + `auto_qc` (used only if `qc.auto`).
   DISABLED by default until accounts connected. *Evidence:* gated run reports the gate; adapter
   + caption logic tested.

### 🧭 Decisions baked in (HANDOFF §9, this session)
- Posting → **Repurpose.io** (Eric trialing it). · Launch → **Hot Seat + Money Fights**.
- Whop → **CUT** (owned-first only; `capture.py` Whop-payout path stripped 2026-06).
- **QC → MANUAL Slack review** (revised from "auto"): clips post to Slack, nothing advances
  until Eric ✅'s it. He oversees content until it earns autonomy ("once I see you're doing the
  right thing then I'll let it run autonomously"). `qc.auto: false` in settings.
- **Hooks → DeepSeek** (started on Ollama — too weak for viral hooks, removed; briefly Claude;
  now DeepSeek per Eric). Key in 1Password → `DEEPSEEK_API_KEY` via `op read` (never on disk).

### 👤 Human-touch count (current)
Recurring: **Slack ✅/❌ review per batch** (the QC gate). One-time setup still pending (below).

### 🚧 #1 autonomy bottleneck → next
**Live-running the full chain is blocked on one-time human setup**, not code. In priority order:
1. **ffmpeg lacks libass/libfreetype** → no caption/`drawtext` rendering (clips produce, but
   text/hook overlays are skipped via graceful degradation). Needs an ffmpeg build with libass.
2. **DeepSeek key** — enable 1Password CLI integration (or give the `op://` ref) so the hook
   agent uses DeepSeek instead of the heuristic fallback.
3. **Slack QC creds** — `SLACK_BOT_TOKEN` + `SLACK_QC_CHANNEL` in `.env` so clips post for review.
4. **Repurpose.io** — connect accounts, point at the outbox, set `distribution.enabled: true`.
5. **Channels** — create/auth Hot Seat + Money Fights (account creation stays human).

Once #1–#3 are in, the daily loop runs source→clip(+hook+captions)→Slack review; #4–#5 light up posting.

**Scoreboard after this session:** still 🟢 Boot Up · $0/mo (no channels live yet — gated on the above).
