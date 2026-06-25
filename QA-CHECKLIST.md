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
- [ ] **capture**: resolves a Postiz post_id → YouTube videoId + pulls analytics (read-only, real)
- [ ] **optimize**: produces weights + appends IMPROVEMENT-LOG.md from real data
- [ ] **milestones**: reads real channel stats, correct progress line, no false crossings
- [ ] **archive**: a clip lands in the Phoenix Protocol Drive folder
- [ ] **cleanup**: prunes local files of posted clips only
- [ ] **delete-video**: refuses a video NOT on our channel (safety); accepts one that is

## Autonomy — the live loop
- [ ] all 3 crons loaded (autopilot / weekly-review / milestones)
- [ ] **autopilot end-to-end** (sandbox `YCP_HOME`, `distribution.enabled: false`): 9/9 stages,
      sane outputs, NO broken clips, ≤ `max_per_run` would post
- [ ] config coherence: posting_times, channel mapping, all secrets present (by name only)

## Rust port — folded in from the render-fix loop
- [ ] Rust clips clamped ≤ 38s (ffprobe a Rust-rendered clip)
- [ ] Rust moment scores in 0–1 (A/B gate fires selectively, not on every moment)
- [ ] Rust hook-title render matches Python (Read a Rust frame: wrapped, top, legible)

## Sign-off
- [ ] Every box above is ✅ with evidence → write `DIALED-DONE` (one-line summary). Loop stops.
