# Ralph loop — fix the Rust binary's 3 render/parity bugs

You are a fresh agent. The repo is your memory. **Python `src/ycp/*.py` is the correct
reference** — the Rust port in `rust/src/*.rs` must match its behavior. Python is live in
production; **do NOT touch `src/ycp/`**. Work only in `rust/`.

The Rust binary runs end-to-end but its OUTPUT is unusable (that's why we haven't cut over).
Three bugs, fix them so the Rust render matches Python:

1. **Clips aren't clamped to 38s** (the morning test produced 60s clips). Python clamps each
   moment: `min(end, start + MAX_CLIP_SEC)` with `MAX_CLIP_SEC = 38.0` (see `src/ycp/clip.py`).
   Find where `rust/src/clip.rs` / `vision.rs` builds the clip window and apply the same clamp.

2. **Moment scores are on a 3–5 scale, not 0–1** → the A/B "hero" gate (`ab.hero_score = 0.9`)
   fires on EVERY moment, exploding variant count. Python's scores are normalized 0–1 (Gemini
   path) — see `src/ycp/vision.py` / scoring. Make the Rust score 0–1 (normalize, or ensure the
   Gemini path runs and the heuristic fallback is scaled the same).

3. **The hook-TITLE render is broken** — the big title smears across the frame (mis-wrapped
   mid-word, over-sized, wrong position). The word-by-word captions render CORRECTLY, so the
   bug is in the TITLE path of `rust/src/captions.rs`. Match Python `src/ycp/captions.py`: the
   title wraps to whole words within the frame width, fits with `_fit_font`-style stepping, and
   sits in the top region — not overlapping the subject's face.

## Each iteration (pick the FIRST bug not yet verified-fixed)
1. Read the Python reference for that bug, then fix the Rust to match.
2. `cd rust && cargo build --release` — must be green.
3. **VERIFY (no posting — `clip` subcommand only, never `autopilot`/distribute):**
   - Render one real clip: `rust/target/release/ycp clip "<a short youtube url>" --max 1`
     (bound it short for speed). Or, for fast iteration on bug 3, add a tiny
     `cargo run --example render_smoke` that renders ONE frame with a known long title +
     captions to a PNG — no download/whisper needed.
   - Bug 1: `ffprobe` the output → duration ≤ 38s.
   - Bug 2: check the printed/stored score is within 0–1.
   - Bug 3: extract a frame (`ffmpeg -ss 2 -i <clip> -frames:v 1 /tmp/rust-frame.png`) and
     **Read /tmp/rust-frame.png** — confirm the title is wrapped within the frame, near the top,
     legible, NOT smeared over the center/face. (Optionally render the SAME source via
     `.venv/bin/ycp clip` and Read both frames to compare.)
4. Commit that fix alone: `git add rust/src/<file> …` (explicit paths, NEVER `git add -A`;
   `src/ycp/` stays untouched) → `git commit` → `git push origin main`.
5. Update `rust/README.md` status if relevant.

## DONE — only when ALL THREE are verified with evidence
Write a file `rust/RENDER-FIX-DONE` containing a one-line summary (e.g. the verified duration,
score range, and "title frame matches Python"). The loop stops when that file exists. Do NOT
write it prematurely — a fresh agent must be able to see the evidence (a frame you Read, an
ffprobe duration) before you write it. If unsure, leave it and let the next iteration continue.
