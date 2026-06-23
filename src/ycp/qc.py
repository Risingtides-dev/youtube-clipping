"""Stage 3 — APPROVE, channel-agnostic.

The review channel is NOT hardcoded. Two knobs in settings (`qc:`):
  • `auto: true`  → no human; the in-code guardrails decide (fully autonomous).
  • `auto: false` → a human ✅/❌ via `channel`:
        auto      → pick by configured creds (slack > telegram > local)
        slack     → post to the Slack QC channel, react to approve/reject
        telegram  → send to a Telegram chat with ✅/❌ inline buttons
        local     → write a review manifest; approve with `ycp qc-approve <id>`

Every backend just (1) dispatches the pending clips for review and (2) routes the
decision back to the DB via `decide()`. Adding a channel = one small class.
"""
from __future__ import annotations

import json
from pathlib import Path

from . import db
from .config import ROOT, env, settings


def _qc_cfg() -> dict:
    return settings().get("qc", {})


def resolve_channel() -> str:
    """Which human channel to use. `auto` picks by whatever creds are configured."""
    name = (_qc_cfg().get("channel") or "auto").lower()
    if name != "auto":
        return name
    e = env()
    if e.get("slack_bot_token") and e.get("slack_qc_channel"):
        return "slack"
    if e.get("telegram_bot_token") and e.get("telegram_qc_chat"):
        return "telegram"
    return "local"


def dispatch_pending(db_path: Path | None = None) -> dict:
    """Send pending clips for review (or auto-approve via guardrails when qc.auto)."""
    if _qc_cfg().get("auto", False):
        from . import distribute
        return {"channel": "auto-guardrails", **distribute.auto_qc(db_path)}
    name = resolve_channel()
    n = _backend(name).dispatch(db.pending_qc_clips(db_path), db_path)
    return {"channel": name, "dispatched": n}


def collect(db_path: Path | None = None) -> None:
    """Block/poll for decisions on the active human channel (no-op for auto/local)."""
    if _qc_cfg().get("auto", False):
        print("qc.auto is on — no human channel to collect from.")
        return
    _backend(resolve_channel()).collect(db_path)


def decide(clip_id: str, decision: str, db_path: Path | None = None,
           reviewer: str = "human") -> None:
    """Record an approve/reject by clip id (used by every channel + `ycp qc-approve|reject`)."""
    if decision not in ("approve", "reject"):
        raise ValueError("decision must be 'approve' or 'reject'")
    db.record_qc(clip_id, decision, reviewer=reviewer, db_path=db_path)
    if decision == "approve":
        db.set_clip_status(clip_id, "scheduled", db_path=db_path)


def _backend(name: str):
    if name == "slack":
        return _SlackChannel()
    if name == "telegram":
        return _TelegramChannel()
    if name == "local":
        return _LocalChannel()
    raise RuntimeError(f"unknown qc channel {name!r} (use auto|slack|telegram|local)")


# ── backends ──────────────────────────────────────────────────────────────────

class _SlackChannel:
    """Delegates to the existing Slack implementation (uploads mp4 + ✅/❌ reactions)."""

    def dispatch(self, clips, db_path):
        from . import slack_qc
        return slack_qc.post_pending(db_path=db_path)

    def collect(self, db_path):
        from . import slack_qc
        slack_qc.run_listener(db_path=db_path)


class _LocalChannel:
    """No external service — write a review manifest; approve with `ycp qc-approve <id>`."""

    def dispatch(self, clips, db_path):
        lines = ["# QC review — pending clips", ""]
        for c in clips:
            lines.append(
                f"- **{c['clip_id']}** · {c.get('source_creator', '?')} · "
                f"{c.get('length_sec', '?')}s\n"
                f"  - file: `{c.get('post_url', '')}`\n"
                f"  - approve: `ycp qc-approve {c['clip_id']}`  ·  "
                f"reject: `ycp qc-reject {c['clip_id']}`")
        path = ROOT / "data" / "qc-review.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(lines) + "\n")
        print(f"→ {len(clips)} clips for review in {path}")
        for c in clips:
            print(f"   {c['clip_id']}  {c.get('post_url', '')}")
        return len(clips)

    def collect(self, db_path):
        print("local channel: decisions come from `ycp qc-approve|reject <id>` (no daemon).")


class _TelegramChannel:
    """Sends each clip to a Telegram chat with ✅/❌ inline buttons; polls for the taps."""

    API = "https://api.telegram.org/bot{token}/{method}"

    def _creds(self):
        e = env()
        tok, chat = e.get("telegram_bot_token"), e.get("telegram_qc_chat")
        if not (tok and chat):
            raise RuntimeError("TELEGRAM_BOT_TOKEN and TELEGRAM_QC_CHAT required in .env")
        return tok, chat

    def dispatch(self, clips, db_path):
        import requests
        tok, chat = self._creds()
        sent = 0
        for c in clips:
            path = c.get("post_url") or ""
            caption = (f"🎬 QC · {c['clip_id']} · {c.get('source_creator', '?')} · "
                       f"{c.get('length_sec', '?')}s")
            kb = {"inline_keyboard": [[
                {"text": "✅ Approve", "callback_data": f"qc:approve:{c['clip_id']}"},
                {"text": "❌ Reject", "callback_data": f"qc:reject:{c['clip_id']}"}]]}
            try:
                with open(path, "rb") as fh:
                    requests.post(self.API.format(token=tok, method="sendVideo"),
                                  data={"chat_id": chat, "caption": caption,
                                        "reply_markup": json.dumps(kb),
                                        "supports_streaming": True},
                                  files={"video": fh}, timeout=180).raise_for_status()
                sent += 1
            except (OSError, requests.RequestException) as exc:
                print(f"  ! telegram send failed for {c['clip_id']}: {exc}")
        return sent

    def collect(self, db_path):
        import requests
        tok, _ = self._creds()
        print("Telegram QC listener live. Ctrl-C to stop.")
        offset = None
        while True:
            try:
                r = requests.get(self.API.format(token=tok, method="getUpdates"),
                                 params={"timeout": 30, "offset": offset}, timeout=40).json()
            except requests.RequestException:
                continue
            for u in r.get("result", []):
                offset = u["update_id"] + 1
                cq = u.get("callback_query")
                if not cq or not cq.get("data", "").startswith("qc:"):
                    continue
                _, decision, clip_id = cq["data"].split(":", 2)
                try:
                    decide(clip_id, decision, db_path=db_path,
                           reviewer=str(cq.get("from", {}).get("id", "tg")))
                    requests.post(self.API.format(token=tok, method="answerCallbackQuery"),
                                  data={"callback_query_id": cq["id"],
                                        "text": f"{decision}d {clip_id}"}, timeout=20)
                except Exception as exc:  # noqa: BLE001
                    print(f"  ! telegram decide failed: {exc}")
