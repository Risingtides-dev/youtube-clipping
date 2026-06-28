# Launch Checklist — YouTube Clipping Operation

Companion to `YOUTUBE-CLIPPING-WORKFLOW.md`. This is the do-it order for the first 30 days. Check boxes as you go.

---

## Week 0 — Decisions (Eric, 30 min)
- [ ] **Pick 2–3 starting niches.** Higher-RPM niches (business, finance, self-improvement, tech) earn more on YPP; entertainment/podcast clips get more raw volume. Recommend: 1 high-RPM niche + 1 high-volume podcast/streamer niche.
- [ ] **Confirm Ssemble credit model** — log in → check whether 1 credit = 1 source video or 1 export. This decides hybrid pipeline (yes/no). [ssemble.com/pricing](https://www.ssemble.com/pricing)
- [ ] **Set starting channel count:** 8–12 (not 30). Quality of account health > quantity.
- [ ] **Confirm who does the transformation edits** (Jay solo, or add an editor).

## Week 1 — Infrastructure (Jay)
- [ ] **Cloudflare Email Routing:** set catch-all on your domain → generate one clean alias per channel (`niche1-ch1@yourdomain.com`).
- [ ] **Residential IP setup** (NOT datacenter VPN). Create Google accounts **gradually** — 1–2/day, not all at once.
- [ ] **Warm each account 7–14 days** before posting volume: watch, like, subscribe, search — behave human. Warming runs in parallel with Week 1–2 setup.
- [ ] **Create channels** with real branding: niche-specific name, banner, avatar, about section, channel trailer. No generic "Clips123."
- [ ] **Connect all channels to Ssemble** (Business = unlimited). Connect TikTok + IG Reels accounts too (same edit, 3 platforms).
- [ ] **Set up the Source Creator List** (Sheet): columns = creator, niche, lane (owned), channel URL, notes.

## Week 1 — Owned channel infra (Eric + Jay)
- [ ] **Stand up 8–12 owned channels** (faceless, niche-themed), warmed gradually on residential IPs.
- [ ] **Wire the owned monetization stack** — confirm TikTok Creator Rewards eligibility; track progress toward YPP (1K subs + 10M Shorts views/90d, or 4K watch hours); line up affiliate.
- [ ] **Confirm clip-friendly sources** per niche (public clip programs / creators who encourage clipping) — log into the Source Creator List as priority sources.

## Week 1 — Closed-loop DB (automation — Claude builds)
- [ ] **Stand up the Clip Performance DB** (Google Sheet with the §6.1 schema).
- [ ] **Build the daily capture script** (public views → DB; YouTube Analytics API → DB once channels hit YPP). *(Built: `ycp capture` / `autopilot`.)*
- [ ] **Connect each owned channel's analytics (OAuth) — required to close the loop on retention + revenue.** In Google Cloud Console create an OAuth **desktop** client, download `client_secret*.json`, then run `.venv/bin/python scripts/yt_oauth.py` (it auto-grabs the newest `client_secret*.json` from `~/Downloads`, or pass the path). It writes `YT_CLIENT_ID` / `YT_CLIENT_SECRET` / `YT_REFRESH_TOKEN` / `YT_CHANNEL_ID` to `.env` and prints `✓ Authorized: <channel>`. **Without this, the loop scores on public view counts only — no retention %, no swipe-away, no ad revenue feeding the next cycle.** Re-run once per owned channel.
- [ ] **Build the sourcing rank script** (yt-dlp / YT Data API → ranked daily queue by view-velocity).

## Week 2 — First clips live (full pipeline dry run)
- [ ] **Source:** Jay confirms top 5–10 source videos from the ranked queue.
- [ ] **Repurpose:** run Ssemble AI clipping + 2–3 transformed owned-channel edits.
- [ ] **Approve:** QC board live (Notion or Slack) — run the §4 Stage-3 checklist on every clip.
- [ ] **Distribute:** schedule via Ssemble Calendar at optimal times across all channels + platforms.
- [ ] **Verify capture:** confirm posts are logging into the DB with IDs + timestamps.
- [ ] **Target:** 15–30 posts/day by end of Week 2.

## Week 3–4 — Loop running
- [ ] **First Double-Down Brief** generated (auto-scoring + Ollama roll-up → Slack/Notion Monday).
- [ ] **Eric reads brief, sets next week's targets** (scale winners, kill losers, 1–2 tests).
- [ ] **Ramp to 45–75 posts/day** on validated formats only.
- [ ] **First owned revenue** landing (TikTok Creator Rewards / affiliate) — log realized $/1K by niche to calibrate.

---

## Guardrails (tape these to the wall)
- 🚫 No raw reuploads on owned channels — **always transform**.
- 🚫 No copyrighted music beds — Content ID will find it.
- 🚫 No 20-accounts-in-a-day from one VPN — residential IPs, gradual, warmed.
- ✅ Clip-friendly / permissioned sources first — zero strike risk.
- ✅ One channel-wide demonetization costs months — protect account health above all.

---

## What I (Claude) can build next — pick any:
1. **Sourcing rank script** — yt-dlp/YT Data API → daily ranked source queue.
2. **Closed-loop tracker** — the Performance DB + daily capture + weekly Ollama scoring + Double-Down Brief.
3. **Notion QC board** — the Stage-3 approval workflow, wired to your Notion.
4. **Niche research** — deep scan to pick the 2–3 starting niches + the best owned-channel source creators per niche.
