# 🖥️ Setup — moving the operation to the Mac Mini

Clone-and-run guide for standing this repo up on a fresh Mac. For *what the system is*
and *how it runs*, read `HANDOFF.md` first — this doc is just the machine setup.

> ⚠️ **Make the GitHub repo PRIVATE before relying on it.** It contains the full strategy,
> the ranked creator list (`config/niches.yaml`), channel concepts, and money math —
> business IP, not for the public. `gh repo edit ecfromthedc/youtube-clipping --visibility private`.

---

## 1. Prerequisites (Homebrew)

```bash
# Homebrew first if needed: https://brew.sh
brew install python@3.11 uv yt-dlp ffmpeg whisper-cpp
brew install ollama          # OPTIONAL — only used for bulk caption translation
```

**⚠️ ffmpeg must include libass/libfreetype** (caption + hook-title rendering needs it).
The standard homebrew-core `ffmpeg` does. Verify after install:

```bash
ffmpeg -hide_banner -filters | grep -E "drawtext|subtitles"   # must print BOTH
```

If either is missing you have a stripped build (this happened on the old Mac) — the clip
pipeline still runs but skips captions/hooks (graceful degradation). Fix: `brew reinstall ffmpeg`.

## 2. Clone + install

```bash
git clone git@github.com:ecfromthedc/youtube-clipping.git
cd youtube-clipping
./scripts/setup.sh            # uv venv + dev tools + non-editable install (spaced-path safe)
./scripts/setup-whisper.sh    # downloads the GGML model into models/ (gitignored, ~141MB)
```

> Folder name has no spaces here (`youtube-clipping`), so editable installs would work too —
> but `setup.sh` installs non-editable to match how it was built. **Re-run `setup.sh` after any
> `src/ycp/` edit** or the `ycp` command won't see it (tests reflect edits without reinstall).

## 3. Secrets (`.env` — gitignored, never commits)

```bash
cp .env.example .env
```

Then edit `.env` and fill what you need:
- **`DEEPSEEK_API_KEY`** — the viral hook agent (paste from 1Password). Without it, hooks fall back to a transcript heuristic.
- **`SLACK_BOT_TOKEN` / `SLACK_APP_TOKEN` / `SLACK_QC_CHANNEL`** — required for the manual QC board (clips post here for your ✅/❌). See `.env.example` for the app scopes.
- The rest (YouTube API key) is optional.

## 4. Verify it works

```bash
.venv/bin/ruff check src tests                 # clean
.venv/bin/python -m pytest tests/ -q -k "not cut_vertical"   # ~58 pass (skip the ffmpeg smoke that hangs in sandbox)
.venv/bin/python -m ycp scoreboard             # Day-0 game state
.venv/bin/python -m ycp source                 # writes a NON-EMPTY data/source-queue.md (~2-3 min, live yt-dlp)
.venv/bin/python -m ycp autopilot --skip-source --no-clip   # chains all stages 7/7
```

## 5. Go-live gates (what's still human, in order)

1. **ffmpeg w/ libass** — §1 (captions + burned hooks).
2. **DeepSeek key** — §3 (real hooks vs heuristic).
3. **Slack QC** — §3 creds, so clips post for your review. QC is **manual** (`qc.auto: false`) until you trust the output.
4. **Repurpose.io** — connect accounts, point it at the outbox folder (`data/outbox`), then set `distribution.enabled: true` in `config/settings.yaml`.
5. **Channels** — create/auth Hot Seat + Money Fights (account creation stays human by design).

## 6. Schedule it (only once §1–§5 are in and you've approved real output)

```bash
cp scripts/com.risingtides.ycp-autopilot.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.risingtides.ycp-autopilot.plist   # daily 7am
```
(Update the absolute paths inside the plist to the Mac Mini's clone location first.)

---

## Map of the docs
- **`HANDOFF.md`** — cold-start source of truth (state, decisions §9, build order §8, guardrails §10).
- **`AUTOPILOT-GOAL-AND-LOOP.md`** — the build loop (paste its prompt into `/loop` to keep building autonomy).
- **`AUTOPILOT-LOG.md`** — what's been built + the current #1 bottleneck (the loop's memory).
- **`config/hook-playbook.md`** — the viral-hook copywriting skill the DeepSeek agent runs on (tune freely).
- **`RESEARCH-GOAL-AND-LOOP.md`** / **`GOAL-AND-LOOP.md`** — the discovery loop + the ops fallback loop.
