#!/usr/bin/env bash
# Refinement loop — watch data/clips/unusable/ and auto-fix NOTED clips.
#
# Flow: operator drops a clip in unusable/ and attaches a note (rename '<id> -- why.mp4',
# or Finder ⌘I → Comments) → fswatch fires → a headless Claude agent reads the note,
# re-sources a real talking-head moment, re-cuts via `ycp clip` (auto-framed + QC-gated),
# and the good result lands in unreviewed/. The old broken clip is removed on success.
#
# Guardrails:
#   - ONLY clips that carry a note are processed (a note = the operator's "fix this + why").
#   - A ledger (.refine-ledger) records every attempted clip so unfixable ones aren't retried
#     forever — delete a line from it to allow a re-try.
#   - A lock dir prevents concurrent agent runs.
#   - The agent runs headless and uses tokens — this is operator-started, never auto-loaded.
#
# Start:  bash scripts/refine-watch.sh        (Ctrl-C to stop)
set -euo pipefail
cd "$(dirname "$0")/.."
ROOT="$(pwd)"
WATCH="$ROOT/data/clips/unusable"
LEDGER="$ROOT/data/clips/.refine-ledger"
LOCK="$ROOT/data/clips/.refine-lock"
LOG="$ROOT/data/clips/.refine-watch.log"
mkdir -p "$WATCH"; touch "$LEDGER"
command -v fswatch >/dev/null || { echo "✗ fswatch not found (brew install fswatch)"; exit 1; }
command -v claude  >/dev/null || { echo "✗ claude CLI not found"; exit 1; }

refine() {
  # 0) clean orphan note sidecars (their clip was already refined away)
  for sc in "$WATCH"/*.note.txt; do
    [ -e "$sc" ] || continue
    cid="$(basename "$sc" .note.txt)"
    ls "$WATCH/$cid".mp4 "$WATCH/$cid "*.mp4 >/dev/null 2>&1 || rm -f "$sc"
  done
  # 1) fresh drop with no note yet → create a sidecar + pop open TextEdit for the operator
  for mp4 in "$WATCH"/*.mp4; do
    [ -e "$mp4" ] || continue
    base="$(basename "$mp4" .mp4)"
    case "$base" in *" -- "*) continue ;; esac          # already noted via filename suffix
    sc="$WATCH/$base.note.txt"
    if [ ! -f "$sc" ]; then
      printf '# Why is this clip wrong? Write your note below, then press Cmd+S to refine.\n# e.g. "shows the interviewer not the guest" / "hook not related" / "cuts off before the point"\n\n' > "$sc"
      open -e "$sc"
      echo "$(date '+%T') opened note editor for $base" | tee -a "$LOG"
    fi
  done
  # 2) any clip with a now-non-empty note, not yet attempted? run the agent over them.
  local pending
  pending=$(.venv/bin/python -m ycp notes 2>/dev/null | sed -n 's/^  \([^ ]*\)  →.*/\1/p' \
            | grep -vxF -f "$LEDGER" || true)
  [ -z "$pending" ] && return 0
  if ! mkdir "$LOCK" 2>/dev/null; then echo "$(date '+%T') busy, skip" >>"$LOG"; return 0; fi
  trap 'rmdir "$LOCK" 2>/dev/null || true' RETURN
  echo "$(date '+%T') refining: $(echo "$pending" | tr '\n' ' ')" | tee -a "$LOG"
  claude -p "You are the refinement loop for the AI-news clip factory at $ROOT (already cwd).
The operator dropped broken clips into data/clips/unusable/ each with a NOTE saying what's wrong.
Run '.venv/bin/python -m ycp notes' to list them. For EACH noted clip below, fix it:
$pending
Per clip: (1) read its note — that's why it's bad; (2) delete the old clip (file in
data/clips/unusable/ + its DB row); (3) re-source a clip where the SUBJECT is a close-up
talking head actually saying the point (use the note's guidance; WebSearch / 'ycp goldmine <url>'
to find the moment; NEVER Joe Rogan/JRE); (4) re-cut: .venv/bin/python -m ycp clip \"<url>\"
--max 1 --start <MIN> --window <MIN ~1.2> --creator \"<who>\" --channel ai-frontier --title \"<hook>\"
— the pipeline auto-frames, trims, and QC-gates; (5) confirm it routed to data/clips/unreviewed/.
Max 2 cut attempts per clip. Be concise." \
    --dangerously-skip-permissions >>"$LOG" 2>&1 || echo "$(date '+%T') agent error" >>"$LOG"
  # mark every pending clip as attempted (so failures don't loop)
  echo "$pending" >> "$LEDGER"
  echo "$(date '+%T') done" >>"$LOG"
}

echo "👀 watching $WATCH for noted clips… (Ctrl-C to stop)  log: $LOG"
refine                                   # process anything already noted at startup
fswatch -o "$WATCH" | while read -r _; do
  sleep 2                                # debounce Finder's multi-event writes
  refine
done
