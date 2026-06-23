# YouTube Clipping Operation — Master Workflow & Strategy

**Owner:** Eric Cromartie / Rising Tides
**Operator:** Jay (infrastructure + sourcing + QC)
**Distribution engine:** Postiz (public API, preferred — we hold the token) · Repurpose.io (alternative). See DISTRIBUTION.md.
**Goal:** $15,000+/month, durable, on a closed-loop **automated** system
**Strategy:** **Owned-first** — your faceless channels are the asset; the owned monetization stack (TikTok Creator Rewards + YPP + affiliate + brand deals) is the revenue. _(Whop cut 2026-06; pure owned-first — supersedes the original Whop-first framing.)_
**Last updated:** 2026-06-22 (owned-first reconciliation)

---

## 0. Bottom line up front (read this first)

**OWNED-FIRST (Whop cut 2026-06).** The facts below are unchanged; the *conclusion* is. We build owned channels as the asset and monetize the owned stack. Here's why:

1. **Shorts ad revenue *alone* can't get you there — that's why we stack.** YouTube Shorts ad rev pays only **$0.03–$0.07 per 1,000 views**; to hit $15K on that alone you'd need **~300–500 million views/month** (top-1%). The fix isn't one magic source — it's the owned *stack* (TikTok Creator Rewards + YPP + affiliate + brand deals, §9), and you **own** every channel feeding it. ([Shorts RPM](https://mediacube.io/en-US/blog/youtube-shorts-rpm))

2. **The July 2025 "inauthentic content" crackdown did NOT ban clips.** YouTube explicitly confirmed clips, compilations, commentary, and reactions are *still monetizable* — what got killed is **mass-produced, templated, zero-effort content that's "easily replicable at scale."** Pure auto-reuploads of someone else's clip with a caption slapped on = the exact thing that now gets a channel demonetized *channel-wide*. Transformation is the line between a monetized asset and a dead channel. ([YouTube policy](https://support.google.com/youtube/answer/1311392?hl=en), [Social Media Today](https://www.socialmediatoday.com/news/youtube-clarifies-monetization-update-inauthentic-repeated-content/752892/))

3. **Owned channels are the asset; the owned *stack* is the cash.** YPP eligibility takes months (1,000 subs + 10M Shorts views/90d, or 4,000 watch hours), but you don't wait on it: **TikTok Creator Rewards** pays on 1-min+ videos far sooner (~$0.40–$1.00/1K, ~10–20× Shorts ad rev), **affiliate** earns on even a small engaged channel, and **brand deals** (Rising Tides' agency edge) stack on top.

**So the play is owned-first.** Your faceless channels are the appreciating, automatable, sellable asset — that's the build. The owned monetization stack (TikTok Creator Rewards + YPP + affiliate + brand deals) is the path to $15K. **Honest tradeoff:** owned-first is slower to the *first* dollar than renting distribution would be — that's the price of owning the asset instead of renting it. Full reasoning in §1–2.

---

## 1. The money math (honest version)

### What $15,000/month actually requires

| Income path | Realized rate | Views/month needed | Views/day | Reality check |
|---|---|---|---|---|
| **Shorts ad rev only** (conservative $0.03/1K) | $30 / million | **333M** | 11.1M | Top-1% operation. 6–12 mo build. |
| **Shorts ad rev only** (good $0.05/1K) | $50 / million | **200M** | 6.7M | Still enormous. |
| **The Owned Stack** (TikTok Rewards + YPP + affiliate + brand deals) | mixed | ~15–25M total | ~500–800K | **The realistic $15K plan** — you own every channel. |

**Takeaway:** pure Shorts-ad-rev to $15K is a top-1% grind (hundreds of millions of views/mo). The owned *stack* — TikTok Creator Rewards (the fast owned cash) + YPP + affiliate + brand deals — gets there at a fraction of that, and you **own** every channel.

### Assumptions to verify Day 1 (don't take my numbers as gospel — confirm)
- **Ssemble credit model:** Business = **2,600 video credits/year (~7/day)**. Confirm whether 1 credit = *one source video processed* (→ many clips per credit, great) or *one clip export* (→ a real volume ceiling). This single fact decides whether Ssemble alone can carry the volume or whether we run the hybrid pipeline in §5. ([Ssemble pricing](https://www.ssemble.com/pricing))
- **Realized TikTok Creator Rewards rate:** advertised rates move; plan around a conservative **$0.40–$1.00/1K realized** and re-verify current program terms before relying on a number.
- **Your niche RPM:** Finance/business clips earn ~10x comedy/lifestyle on YouTube. Niche selection (§4, Stage 1) directly moves the YPP number.

---

## 2. The operating model — owned channels (single lane)

_(Whop cut 2026-06; the original two-lane model collapsed to one — pure owned-first.)_ Everything downstream feeds **owned faceless channels** — there is no rented/permissioned lane anymore.

### The core asset — owned faceless channels (your $15K engine)
- **What:** Niche/theme channels you own (e.g., "best podcast moments," "[niche] breakdowns," reframed challenge/comedy clips with a hook + commentary angle).
- **Why it's the long game:** You own the audience, the channel appreciates, and it monetizes via the owned stack (TikTok Creator Rewards + YPP + affiliate + brand deals) *and* becomes a sellable asset.
- **Optimize for:** Transformation + retention. These MUST clear the "inauthentic content" bar — original packaging, commentary, editorial point of view, not template slop.
- **Pays:** TikTok Creator Rewards + affiliate land early; YPP turns on Month 3+ (after threshold), then it compounds.

---

## 3. Compliance guardrails (these protect the entire operation)

> One channel-wide demonetization or a 3-strike termination wipes out months of work. These are non-negotiable.

### 3.1 The transformation standard (beats the inauthentic-content policy)
Every clip on an *owned* channel must add at least one layer of original human value:
- **Reframe / re-edit** — your own cut, pacing, hook, B-roll, zooms, not the raw clip.
- **Commentary or context** — text overlay analysis, a take, a "why this matters," a question to the audience.
- **Curation with a thesis** — the channel has a clear editorial identity, not "random viral clips."
- **Original packaging** — your thumbnail, your title voice, your captions style.

Avoid the kill-zone: identical template across every video, zero-variation auto-captions on someone else's raw footage, channels that are obviously "easily replicable at scale."

### 3.2 Copyright / Content ID
- Prefer sources who **explicitly allow clipping** (creators with public clip programs, Creative Commons). Permissioned = no strike risk.
- For owned transformation channels, the transformation + commentary is your fair-use posture — but understand it's a *posture*, not a guarantee. Keep clips short, add value, never reupload full segments.
- **Music is the silent killer.** Background music in clips triggers Content ID instantly. Strip/replace audio beds where possible.

### 3.3 Account infrastructure — the Jay tasks, done safely
Your plan (Cloudflare emails + VPN + multiple accounts) is half-right. Here's the safe version:

- ✅ **Cloudflare Email Routing for unique emails** — smart and legitimate. A catch-all domain gives you unlimited clean, professional aliases (`channel1@yourdomain.com`). Keep this.
- ⚠️ **Don't spin up 20 accounts from one datacenter VPN in a day.** YouTube flags account *networks* created on shared/datacenter IPs — that's how whole networks get banned together. Use **clean residential IPs**, create accounts gradually, and **warm each one** (watch videos, like, subscribe, behave human for 1–2 weeks) before posting at volume.
- ✅ **Structure under a Brand Account model** where sensible, and keep **separate, properly-managed AdSense** — don't let a strike on one channel cascade through shared monetization.
- ✅ **Start with fewer, healthier channels (8–12), not 30 burners.** Quality of account health > quantity. Scale channel count only after the first cohort is warm and clean.

---

## 4. The A-to-Z pipeline (the workflow)

Five stages. Each shows **what happens → who/what does it → automation level.**

```
[1 SOURCE] → [2 REPURPOSE] → [3 APPROVE] → [4 DISTRIBUTE] → [5 MEASURE → feeds back to 1]
   Jay          Ssemble/AI       Jay/Eric       Ssemble          Automation (closed loop)
```

### Stage 1 — SOURCE (find the videos worth clipping)
- **What:** Build a ranked daily queue of source videos with the highest clip potential.
- **How:**
  - Maintain a **Source Creator List** per niche — prioritize *clip-friendly creators* (public clip programs / clipping encouraged) and *big evergreen creators*.
  - Daily, pull each creator's newest + top-performing long-form (sorted by views/velocity) via the **YouTube Data API** or `yt-dlp`. Rank by view-velocity (views ÷ hours since upload).
- **Automation:** *Semi-auto.* A daily sourcing script ranks candidates and drops the top N into the queue. Jay confirms the final picks (5 min). → **This is the first thing worth building (§Next steps).**
- **Output:** `Daily Source Queue` (creator, video URL, view-velocity, lane, target channels).

### Stage 2 — REPURPOSE (clip + transform)
- **What:** Turn each source video into 3–10 vertical Shorts.
- **How:**
  - **Raw volume:** Ssemble AI clipping finds viral moments → auto-captions + face-tracking + hook titles. Fast. Or the hybrid local pipeline (§5) for raw volume.
  - **Transformation:** Start from the AI clip, then add the value layer — your hook, your text-overlay take, trimmed pacing, your caption style. This is where a human (Jay or an editor) earns the monetization.
  - One edit is exported **9:16 once, reused across YouTube Shorts + TikTok + IG Reels** (3 posts per edit).
- **Automation:** *AI-assisted, human-finished.* Ssemble does 80%, the transformation layer is the 20% that keeps you monetized.
- **Output:** Clips in a review queue, tagged: source creator, format, hook type, length, target channel, lane.

### Stage 3 — APPROVE (QC gate)
- **What:** A human approves before anything posts — catches off-brand, Content-ID-risky, weak-hook, or policy-risky clips.
- **How:** Clips land in a **review board** (Notion or a simple Slack approval flow — you have both connected). Reviewer thumbs up/down + optional tweak note. Approved → scheduled. Rejected → killed or sent back.
- **Approve criteria checklist:**
  - [ ] Hook lands in first 1–2 seconds
  - [ ] Transformation present
  - [ ] No copyrighted music bed / Content-ID risk
  - [ ] Caption accuracy + readability
  - [ ] Correct target channel + niche fit
- **Automation:** *Human gate, frictionless.* This is the "approving the viral clips" step you asked for — kept to seconds-per-clip with a board.
- **Output:** Approved, scheduled clips.

### Stage 4 — DISTRIBUTE (multi-channel auto-post)
- **What:** Post approved clips across all channels at optimal times, hands-off.
- **How:** **Ssemble Calendar** schedules + auto-posts to TikTok / YouTube Shorts / IG Reels on connected accounts (Business = *unlimited accounts*) at best-performing times. Set it and forget it. ([Ssemble](https://www.ssemble.com/tools/ai-clipping))
- **Automation:** *Fully automated* once approved.
- **Output:** Live posts, logged with post ID + timestamp + channel into the performance DB.

### Stage 5 — MEASURE → FEED BACK (the closed loop — §6)
- **What:** Pull performance daily, score weekly, decide what to double down on, feed that back into Stage 1's sourcing spec.
- **Automation:** *Fully automated capture + scoring; human reads the weekly brief and sets next week's targets.*

---

## 5. Posts-per-day plan (volume + the credit bottleneck)

### Volume targets (ramp)
| Phase | Channels live | Edits/day (unique) | Posts/day (×3 platforms) | Notes |
|---|---|---|---|---|
| **Weeks 1–2** (warm-up) | 4–6 warming | 5–10 | 15–30 | Accounts warming; low volume, build habit + DB. |
| **Weeks 3–6** (ramp) | 8–12 | 15–25 | 45–75 | Owned channels live, closed loop running. |
| **Weeks 7–12** (scale winners) | 12–15 | 25–35 | 75–100+ | Double down on validated formats only. |

**Rule of thumb:** ~4–6 Shorts/channel/day on YouTube. Volume + iteration is the whole game early — most clips do 1–5K views, the winners spike to 100K–1M+. You're buying lottery tickets and then printing more of whatever wins.

### ⚠️ The Ssemble credit bottleneck — and the fix
Business = **~2,600 credits/year (~7/day)**. If 1 credit = 1 export, that **cannot** sustain 25–35 edits/day. Two options:

1. **Confirm the credit model first.** If 1 credit = 1 *source video* (yielding many clips), the ceiling may be fine. Verify Day 1.
2. **Run the hybrid pipeline (recommended for volume):** Use the tools you already have installed —
   - `yt-dlp` → download source videos (free, unlimited)
   - `ffmpeg` + scene/silence detection → batch-cut raw clips (free, unlimited)
   - `whisper` → auto-captions locally (free, you already run this)
   - **Ssemble reserved for:** AI viral-moment *detection* on hero candidates, the polished owned-channel transformation clips, and — critically — the **auto-post scheduler** (its real superpower for you is unlimited-account distribution, not just clipping).

   This keeps raw-volume clipping free and uncapped, and spends Ssemble credits only where they add the most value. It also fits your existing local-automation stack.

---

## 6. The closed-loop feedback system (your "double down" engine)

This is the part that compounds. The whole point: **stop guessing, let data tell you which creator × format × hook to scale.**

### 6.1 What we track (the schema)
One row per posted clip, in a **Clip Performance DB** (Google Sheet to start, SQLite when it grows):

| Field | Example |
|---|---|
| clip_id, post_date, channel, platform, lane | `c0612-03`, `2026-06-12`, `PodMoments`, `YouTube`, `Lane2` |
| source_creator, source_video | `FlagrantPod`, `url` |
| format | `talking-head-moment`, `reaction`, `list`, `debate-clip` |
| hook_type | `question`, `bold-claim`, `cliffhanger`, `pattern-interrupt` |
| length_sec | `34` |
| views_24h, views_7d, retention_%, swipe_away_% | from YouTube Analytics API |
| rpm, ad_revenue | YPP channels |
| virality_score | computed (below) |

### 6.2 How we score
Weekly, compute a **Virality Score** per clip (e.g., a weighted blend of 7-day views, retention %, and revenue-per-view), then **roll it up by dimension**: which *source creator*, *format*, *hook type*, *length bucket*, and *posting time* are over-indexing.

### 6.3 The weekly Double-Down Brief (the output that closes the loop)
Every Monday, an automated one-pager:
- 🟢 **Scale:** top-decile combos (e.g., "Flagrant debate-clips, question hook, 25–35s → 4.2x avg views — make 3x more").
- 🔴 **Kill:** bottom-decile (stop wasting edits here).
- 🆕 **Test:** 1–2 new format/creator bets.
- 💰 **Money focus:** which niches/channels earned best per view this week → where to point volume.

This brief **becomes next week's Stage 1 sourcing spec.** That's the closed loop: post → measure → score → decide → source to the decision → post. Who/what/format/where to double down, answered with data every week.

### 6.4 Tooling
- **Capture:** Daily script snapshots public views (and YouTube Analytics once channels hit YPP) → appends to the DB. (Build target — see Next steps.)
- **Score + Brief:** Weekly aggregation. Per your ops rules, the heavy roll-up/scoring is **offloaded to local Ollama** (it's repetitive batch work) — Claude builds the script, Ollama grinds the numbers, you read the brief.
- **Surface:** Brief drops into Slack/Notion every Monday.

---

## 7. Roles & ownership

| Who/What | Owns |
|---|---|
| **Jay** | Account infrastructure (safe setup, warming), Stage 1 sourcing confirmation, Stage 3 QC approval. The human operator. |
| **Ssemble** | Stage 2 AI clipping + Stage 4 auto-post distribution (unlimited accounts). The engine. |
| **Editor (Jay or a hire)** | The owned-channel transformation layer — the 20% that keeps channels monetized. Add when scaling. |
| **Automation (Claude-built)** | Sourcing rank script, closed-loop capture, weekly scoring + Double-Down Brief. The nervous system. |
| **Eric** | Strategy, niche/creator selection, the weekly double-down decision, partnerships + cross-promo. |

---

## 8. 90-day roadmap to $15K/month (owned-first)

| | Focus | Milestones | Target revenue |
|---|---|---|---|
| **Month 1** | Infrastructure + first owned channels | 8–12 warmed channels; autopilot wired; Concepts 1–2 live; closed-loop DB running | **$0–1K** (TikTok Rewards begins) |
| **Month 2** | Volume + the loop compounding | 45–75 posts/day; first TikTok Creator Rewards + affiliate revenue; Double-Down Brief steering decisions; channels approaching YPP threshold | **$2–5K** (TikTok Rewards + affiliate core) |
| **Month 3** | Scale winners + YPP turns on | Scale only validated concepts; first channels cross YPP (1K subs / 10M Shorts views per 90d); first brand deal into an owned channel | **$8–15K** (TikTok + YPP + affiliate + brand deals) |
| **Steady state** | Owned network = compounding asset | Portfolio of monetized owned channels + affiliate + brand deals | **$15K+ and climbing** |

---

## 9. The full monetization stack (owned-first; every income line)

1. **TikTok Creator Rewards** — the fastest *owned* cash: ~$0.40–$1.00/1K on 1-min+ videos (~10–20× YouTube Shorts ad rev). Verify current rates.
2. **YouTube Partner Program** — Shorts ad-rev share (45% of pool) + high-RPM long-form (finance/business RPM $5–30) on owned channels. The compounding asset.
3. **Affiliate / product links** — niche-relevant offers in pinned comments / bios; often out-earns ad rev on a small engaged channel.
4. **Direct brand deals** — Rising Tides is a marketing agency: sell sponsorships straight into your own channels as they grow. Highest-margin owned line.
5. **Channel sales** — aged, monetized faceless channels are sellable assets ($X-thousands each).
6. **Cross-promotion into Rising Tides wins** — point distribution at what you're already winning with; clip channels become an owned media network.

---

## 10. Risk register

| Risk | Severity | Mitigation |
|---|---|---|
| Channel-wide demonetization (inauthentic content) | 🔴 High | Transformation standard on every owned-channel clip (§3.1). |
| Copyright strikes / Content ID | 🔴 High | Prefer permissioned sources; strip music; short transformed clips, never full reuploads. |
| Account network ban (VPN/burner pattern) | 🟠 Med-High | Residential IPs, gradual creation, warm accounts, fewer healthier channels (§3.3). |
| Ssemble credit ceiling throttles volume | 🟠 Med | Verify credit model Day 1; run hybrid local pipeline (§5). |
| Pure-YPP timeline disappoints | 🟡 Med | TikTok Creator Rewards + affiliate give owned cash flow well before YPP turns on. |

---

### Sources
- [YouTube channel monetization policies (official)](https://support.google.com/youtube/answer/1311392?hl=en)
- [YouTube clarifies inauthentic/reused content update — Social Media Today](https://www.socialmediatoday.com/news/youtube-clarifies-monetization-update-inauthentic-repeated-content/752892/)
- [YouTube Shorts RPM 2026 — Mediacube](https://mediacube.io/en-US/blog/youtube-shorts-rpm)
- [Ssemble pricing](https://www.ssemble.com/pricing) · [Ssemble AI clipping + auto-post](https://www.ssemble.com/tools/ai-clipping)
