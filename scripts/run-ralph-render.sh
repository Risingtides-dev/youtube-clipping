#!/usr/bin/env bash
# Ralph loop — fix the Rust binary's 3 render/parity bugs (rust/RENDER-FIX-PROMPT.md).
# Fresh Claude each iteration; repo = memory; done-gate = the agent writes rust/RENDER-FIX-DONE
# once all three are verified (build green + a rendered frame inspected + duration/score checks).
#
#   bash scripts/run-ralph-render.sh
set -uo pipefail
cd "$(dirname "$0")/.."
mkdir -p data/logs
LOG="data/logs/ralph-render.log"
rm -f rust/RENDER-FIX-DONE   # fresh run

# `claude` is an interactive alias (clears proxy vars); call the real binary the same way.
CLAUDE_BIN="${CLAUDE_BIN:-/opt/homebrew/bin/claude}"
run_claude() {
  ALL_PROXY= HTTPS_PROXY= HTTP_PROXY= all_proxy= https_proxy= http_proxy= \
    "$CLAUDE_BIN" "$@"
}

ALLOW=(--permission-mode acceptEdits --allowedTools
  Edit Write Read Glob Grep
  "Bash(cd:*)" "Bash(ls:*)" "Bash(cat:*)" "Bash(grep:*)" "Bash(rg:*)" "Bash(find:*)" "Bash(sed:*)" "Bash(echo:*)" "Bash(mkdir:*)" "Bash(cp:*)"
  "Bash(cargo:*)" "Bash(rustc:*)" "Bash(ffmpeg:*)" "Bash(ffprobe:*)"
  "Bash(git add:*)" "Bash(git commit:*)" "Bash(git push:*)" "Bash(git status:*)" "Bash(git diff:*)" "Bash(git log:*)"
  "Bash(rust/target/debug/ycp:*)" "Bash(rust/target/release/ycp:*)"
  "Bash(.venv/bin/python:*)" "Bash(.venv/bin/python3:*)" "Bash(.venv/bin/ycp:*)")

echo "=== Ralph (render fix) started $(date) ===" | tee -a "$LOG"
for i in $(seq 1 30); do
  if [ -f rust/RENDER-FIX-DONE ]; then
    echo "✓ Ralph: render fixes COMPLETE after $((i-1)) iterations $(date) — $(cat rust/RENDER-FIX-DONE)" | tee -a "$LOG"
    break
  fi
  echo "── iteration $i  $(date +%H:%M:%S) ──" | tee -a "$LOG"
  run_claude -p "$(cat rust/RENDER-FIX-PROMPT.md)" "${ALLOW[@]}" >>"$LOG" 2>&1 \
    || echo "(iteration $i exited non-zero)" | tee -a "$LOG"
  sleep 3
done
[ -f rust/RENDER-FIX-DONE ] || echo "⚠ Ralph stopped without DONE — check $LOG" | tee -a "$LOG"
echo "=== Ralph (render fix) stopped $(date) ===" | tee -a "$LOG"
