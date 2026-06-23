#!/usr/bin/env bash
# Autopilot daily tick — the whole closed loop in one command.
#   source → clip → qc → capture → brief → scoreboard
#
# This is the cron/launchd entrypoint. It supersedes daily.sh (which only did
# source + capture). Logs each run to data/autopilot-runs.log.
#
# Enable on a schedule ONE of two ways (do this only once the pipeline is ready
# to run end-to-end — i.e. after distribution is wired + channels are live):
#
#   launchd (recommended on macOS — survives logout, no crontab):
#     cp scripts/com.risingtides.ycp-autopilot.plist ~/Library/LaunchAgents/
#     launchctl load ~/Library/LaunchAgents/com.risingtides.ycp-autopilot.plist
#
#   cron (7am daily):
#     0 7 * * *  "/Users/ecfromthedc/Desktop/Development/Youtube Clipping Workflow/scripts/autopilot.sh"
set -euo pipefail
cd "$(dirname "$0")/.."                       # repo root (ycp resolves config/ + data/ from here)

# DeepSeek key for the hook agent — pulled from 1Password at runtime, never on disk.
# Set DEEPSEEK_OP_REF to the item's secret reference, e.g.:
#   export DEEPSEEK_OP_REF="op://Private/DeepSeek/credential"
# (needs the 1Password CLI integration enabled). If DEEPSEEK_API_KEY is already
# set, or no ref/op is available, we skip and the hook agent falls back to the heuristic.
if [ -z "${DEEPSEEK_API_KEY:-}" ] && [ -n "${DEEPSEEK_OP_REF:-}" ] && command -v op >/dev/null 2>&1; then
  DEEPSEEK_API_KEY="$(op read "$DEEPSEEK_OP_REF" 2>/dev/null || true)"
  export DEEPSEEK_API_KEY
fi

LOG="data/autopilot-runs.log"
mkdir -p data
echo "[$(date '+%Y-%m-%d %H:%M:%S')] autopilot tick starting" | tee -a "$LOG"

# --max-videos caps clip volume per run; tune as channels prove out.
.venv/bin/python -m ycp autopilot --max-videos "${YCP_MAX_VIDEOS:-5}" 2>&1 | tee -a "$LOG"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] autopilot tick done" | tee -a "$LOG"
