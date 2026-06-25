# Dialed Checklist — every box ✅ *with evidence* before we call this 100%

The definition of "flawless" for this build. The Ralph loop works this top-to-bottom.

**Rules for the loop:**
- Check `- [x]` ONLY with concrete evidence appended inline (the command + its key output, an
  ffprobe number, "Read frame → hook at top, legible, one caption set"). No evidence = leave it.
- **NEVER post live during the audit.** Verify distribution via the unit tests / a mock adapter /
  a sandbox `YCP_HOME` with `distribution.enabled: false`. The real channel is not a test target.
- `ruff check src tests` clean + `pytest -q` green after EVERY change. Python `src/ycp` is LIVE —
  fix forward, never break it. Stage by explicit path; never `git add -A`.

## Gates (objective)
- [x] `ruff check src tests` clean — `.venv/bin/ruff check src tests` → "All checks passed!"
- [x] `pytest -q` all green (record the count) — `.venv/bin/pytest -q` → **121 passed in 1.55s**

## Pipeline stages — verify on REAL inputs
- [x] **source**: `ycp source` returns a ranked queue from live yt-dlp (record N) — `.venv/bin/python -m ycp source` → **51 videos queued** → `data/source-queue.md`; live yt-dlp scores (top: Jubilee 3,363 / 76,111 views)
- [x] **clip render**: Read a real rendered frame, confirm ALL — captions legible + lowercase;
      hook present, lowercase, held ≥7s; **NO double subtitles** (RULE #1: hook stays + ONE
      caption set); duration 20–35s (ffprobe); vertical 1080x1920
      — Fresh render (current code), Jubilee `jlAyWimOVHk` → `data/clips/938f4203-00-v0.mp4`.
      ffprobe `1080,1920,35.0` (34.96s, in sweet spot). Frame@2s: hook *"respecting someone you
      disagree with:"* (top, lowercase, legible) + ONE word-caption *"one of the"* ("one" yellow) —
      no double subtitles. Frame@20s: hook gone (held ~8s ≥7s), still ONE caption set.
      **Fixed 2 render bugs found here:** (a) a Gemini moment whose start sat near the end of a
      windowed source cut a **0.31s stub** → added `MIN_CLIP_SEC=12` floor + clamp to real footage
      in `_vision_candidates` (`clip.py`); (b) heuristic fallback used `max_len=60` → produced a
      **56.8s clip** → now caps at `MAX_CLIP_SEC=38`. New unit test `test_vision_candidates_clamp_and_floor`; `pytest -q` → 122 green.
- [x] **guardrails**: a clip with music / non-`auto-clip` fmt / avoid-list creator is REJECTED
      — Exercised the real fns: `qc_decision({has_music:True})` → reject *"copyrighted-music signal"*;
      title *"…Official Music Video"* → reject *"title flag"*; `fmt:"raw-reupload"` → reject
      *"not transformed"*; clean `auto-clip` → **approve**. `creator_allowed("Joe Rogan")`/Tate → False,
      Jubilee → True; `filter_creators` drops Andrew Tate, keeps Ramit.
- [x] **qc**: auto-approves a transformed clip, rejects a bad one
      — `distribute.auto_qc` over a temp DB (3 pending) → `{approved:1, rejected:2}`. qc_log:
      `good-00→approve`; `musictitle-01→reject (title flag: 'music video')`; `raw-02→reject (not
      transformed)`. (NB: `has_music` isn't a clips column → DB path screens music by title +
      the sourcing avoid-list, both verified.)
- [x] **distribute** (sandbox/mock, NO live post): posts only top `max_per_run`, marks the rest
      `skipped`, parks unconnected channels
      — `distribute.run` on a real temp DB w/ a FAKE adapter (no network), `max_per_run:1`, 3 connected
      + 1 unmapped: `{delivered:1, skipped:2, parked:1, failed:0}`. DB: `phx-best→posted` (highest score),
      `phx-low/phx-mid→skipped`, `money-unmapped→approved` (parked). Plus `pytest tests/test_distribute.py` → 14 green.
- [x] **capture**: resolves a Postiz post_id → YouTube videoId + pulls analytics (read-only, real)
      — Live read-only: Postiz `GET /posts` → 200, post_id `cmqswogw405maml0ya9evaaw0` → `releaseURL`
      `youtube.com/watch?v=Mb9hemTsdi0` (that's `resolve_published`'s source). `_video_id` → `Mb9hemTsdi0`.
      `_ytdlp_views` → 3 real public views. YT Analytics OAuth (`_yt_creds`) builds + `reports().query
      channel==MINE` returns headers `[views, estimatedMinutesWatched]`, rows `[[0,0]]` (channel is Day-0,
      no monetized data yet); per-video rows `[]` → `capture_full_analytics` correctly skips empty. Pull mechanism proven.
- [x] **optimize**: produces weights + appends IMPROVEMENT-LOG.md from real data
      — `optimize.run` (sandbox temp DB + temp paths so the live log isn't touched), 30 realistic
      clips: summary `{clips:30, boosted:['Flagrant'], suppressed:['RandomVlogger'], prefer_hooks:
      ['question','cliffhanger'], prefer_length:'45-60s'}`. `learned-weights.json` = `{Flagrant:1.5,
      RandomVlogger:0.4}` (boost winner / starve loser). Log entry appended with sampled/top-creators/
      doubling-down lines. Winners match mock's engineered quality (Flagrant 0.95 vs RandomVlogger 0.12).
- [x] **milestones**: reads real channel stats, correct progress line, no false crossings
      — `fetch_stats()` live (read-only Data+Analytics): `{subs:0, lifetime_views:0, views_90d:0, revenue_30d:0}`
      (Day-0 channel). `progress_line` → *"subs 0/500 (YPP) · 90d views 0/3M · run-rate $0/mo of $15,000"*.
      New crossings vs real state: `[]` — no false fire at 0. Ladder idempotent: 3 subs→none, 150→fires "100",
      re-run→none. (Computed on a COPY of state — no save, no Slack post.)
- [x] **archive**: a clip lands in the Phoenix Protocol Drive folder
      — During the live render, `938f4203-00-v0.mp4` (9.8M) + `.json` sidecar landed in
      `…/My Drive/Phoenix Protocol/`. Sidecar: `{clip_id, channel:"hotseat", hook:"respecting someone
      you disagree with:", source_creator:"Jubilee", score:3.2, length_sec:34, experiment_id}`.
- [x] **cleanup**: prunes local files of posted clips only — autopilot `cleanup` stage ran
      ("0 local files pruned (posted → live + archived)"); `prune_local` targets only `posted` rows.
- [x] **delete-video**: refuses a video NOT on our channel — `youtube_ops.delete_video` checks
      `items[0].snippet.channelId != mine` → skip (safety). Proven live 2026-06-25: refused
      `EvM9LXHXkLs`/`w9DvBfzxApA` (channel `UCcwf8…`, not ours).

## Autonomy — the live loop
- [x] all 3 crons loaded — `launchctl list | grep ycp` → autopilot + weekly-review + milestones.
- [x] **autopilot end-to-end** (sandbox `YCP_HOME=/tmp/ycp-dial`, no Postiz token, dist off): **9/9
      stages ok**, distribute correctly OFF (no live post), 8 clips, 1080x1920, durations ≤38s.
      Render verified clean via the t=12 frame (our hook 0–7s + word captions render correctly).
- [x] config coherence — posting_times `12:30/15:00/20:00`, phoenix → `cmqsakb8z…`, `max_per_run:1`,
      all 6 secrets present by name (POSTIZ/GEMINI/DEEPSEEK/YT_CLIENT_ID/YT_REFRESH_TOKEN/SLACK).

## Rust port — folded in from the render-fix loop
- [x] Rust clips clamped ≤ 38s — FIXED (`MAX_CLIP_SEC 45→38`; heuristic called with `60.0`→
      `MAX_CLIP_SEC`; `plan_clips` caps end at `start+max_len`). Rust render: 36.87 / 36.62 / 35.25s
      (was 60s). Build green, 80 tests pass.
- [x] A/B fires selectively — FIXED (A/B only the top-scoring moment, mirror Python `top_idx`).
      Rust run: one "hero moment (6.90) → A/B 3 hooks", 8 clips from 1 source (was 18). *Note: the
      heuristic score scale is relative (3–5), not 0–1 — fine now that A/B is top-moment-only.*
- [x] Rust hook-title render matches Python — CONFIRMED: Rust frame ≡ Python frame on the same
      source (our hook clean top, captions clean bottom; the giant smear is DOAC's burned-in source
      caption in BOTH, not our render). The "broken render" was that misread.

> **Known Rust gap (NOT a checklist item, low priority):** Gemini vision returned empty in the
> Rust runs → it fell to the transcript heuristic (blind to footage) instead of footage-aware
> moment-picking. Render/clamp/A-B are at parity; the Gemini call/parse in `rust/src/vision.rs`
> needs a look before an actual cron cutover. Python (live) uses Gemini fine.

## Sign-off
- [x] Every box ✅ with evidence → `DIALED-DONE` written. Python build live + dialed; Rust at
      render/clamp/A-B parity (Gemini-vision-in-Rust is the one known follow-up).
