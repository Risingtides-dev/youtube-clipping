# DISTRIBUTION.md — how approved clips get posted

**Canonical distribution plan.** This supersedes the older "Repurpose.io" references scattered in
the loop docs. Distribution is **Stage 7** of the pipeline (`src/ycp/distribute.py`) and only ever
runs on clips that cleared the manual Slack QC gate.

> **Preferred: Postiz (public API).** We hold the `POSTIZ_API_TOKEN` and connect the YouTube
> channels directly in Postiz, so posting is API-native and fully under our control.
> **Alternative: Repurpose.io** (watch-folder) — kept as a swappable fallback.

Pick the path with one knob in `config/settings.yaml`:

```yaml
distribution:
  enabled: false          # master switch — OFF until a provider is fully configured
  provider: postiz        # postiz (preferred) | repurpose (alternative)
```

Both sit behind the same `Adapter` protocol in `distribute.py`, so switching is a config change,
not a rewrite. Every clip re-clears `guardrails.publish_allowed` (transformed, no music, clean
title) right before delivery — defense in depth behind manual QC.

---

## Why Postiz is preferred

| | **Postiz (preferred)** | Repurpose.io (alternative) |
|---|---|---|
| Integration | Direct **public API** — we already hold the token | Watch-folder (Drive/Dropbox sync) |
| Control | Per-post, per-channel, scheduled or now | Fire-and-forget into the folder |
| Ownership | Open-source, self-hostable if we want | Third-party SaaS |
| Per-channel reconnect | Connect once in Postiz | Connect once in Repurpose |
| Cost | Token we have | Separate subscription |

Repurpose stays in the repo as a fallback in case a platform integration is easier there, or as a
zero-code path while Postiz channels are still being connected.

---

## Preferred plan — Postiz

### One-time human setup
1. **Connect each YouTube channel** in Postiz (Postiz UI → add channel → YouTube → auth). Account
   *creation* stays human by design; this is the one-time connect.
2. **Generate the API token:** Postiz → **Settings → Developers → Public API**. Put it in `.env` as
   `POSTIZ_API_TOKEN` (and 1Password — never commit it). Self-hosted? also set `POSTIZ_API_URL` to
   `https://<your-instance>/public/v1`.
3. **Get the integration ids:** `GET /public/v1/integrations` (a "channel" is an `integration` in
   the API). Map each owned channel → its integration id in `distribution.postiz.channels`
   (keys = the channel ids from `CHANNEL-PLAYBOOK.md`).
4. **Flip it on:** set `distribution.enabled: true`. Keep `provider: postiz`.

### The adapter contract (`PostizAdapter`, already implemented)
Per approved clip, gated by `distribution.enabled`:
1. **Upload the mp4** — `POST {api_url}/upload` (multipart `file=@clip.mp4`) → `{ "id", "path" }`.
2. **Create the post** — `POST {api_url}/posts` targeting the channel's integration id:
   ```json
   {
     "type": "now",
     "date": "<ISO-8601>",
     "posts": [{
       "integration": { "id": "<integration-id>" },
       "value": [{ "content": "<caption>", "image": [{ "id": "<media-id>", "path": "<url>" }] }],
       "settings": { "__type": "youtube", "title": "<caption>" }
     }]
   }
   ```
- **Auth:** header `Authorization: <POSTIZ_API_TOKEN>` (raw token, *not* `Bearer`). OAuth tokens
  start with `pos_`.
- **Base URL:** `https://api.postiz.com/public/v1` (cloud) or self-hosted `<instance>/public/v1`.
- **Rate limit:** ~30–100 requests/hour depending on plan (self-hosted set via `API_LIMIT`). It
  caps *requests*, not posts — batch the daily run and respect it.
- **`schedule`:** `now` posts immediately; set `distribution.postiz.schedule: schedule` + pass a
  `date` to queue at a chosen time.

> ⚠ **Go-live gate (production test):** before scheduling the autopilot, post **one real clip to
> one connected channel** with the live token and eyeball it on YouTube. The unit tests mock the
> HTTP; only a real post proves the integration. Confirm the YouTube-specific `settings` fields
> (title/description, Short vs. video) against the live API on that first post.

### Config (`config/settings.yaml`)
```yaml
distribution:
  enabled: false
  provider: postiz
  postiz:
    api_url: https://api.postiz.com/public/v1   # self-hosted: <instance>/public/v1
    token_env: POSTIZ_API_TOKEN                  # resolved from .env / 1Password
    schedule: now                                # now | schedule
    channels:                                    # channel id -> Postiz integration id
      hot-seat: ""
      money-fights: ""
      crash-out: ""
      myth-busting: ""
      boardroom: ""
  outbox: data/outbox                            # used only by the Repurpose alternative
```

---

## Alternative plan — Repurpose.io

Unchanged from the original design. Set `provider: repurpose`. The `OutboxAdapter` drops each
approved clip + a JSON metadata sidecar into `distribution.outbox` (a folder Repurpose watches via
Drive/Dropbox sync); Repurpose auto-posts to the connected accounts. One-time human step: connect
accounts in the Repurpose dashboard and point it at the outbox. Use this if a given platform is
easier to wire there, or as a no-code bridge before Postiz channels are connected.

---

## Status
- **Code:** both adapters implemented + unit-tested (`tests/test_distribute.py`); selection by
  `distribution.provider`. Postiz HTTP is mock-tested (no live token needed to run the suite).
- **Live:** OFF (`enabled: false`). Blocked on the one-time human setup above (token + connect +
  map channels) and the go-live production test. Account creation stays human by design.
