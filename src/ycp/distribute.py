"""Stage 7 — DISTRIBUTE. Approved clips → Repurpose.io → connected channels.

Repurpose.io watches a cloud source (a Drive/Dropbox folder, etc.) and auto-posts
to every connected account. So our handoff is deliberately **thin and swappable**:
drop each approved, publish-gated clip + a metadata sidecar into an OUTBOX folder
that Eric points Repurpose at. ONE-TIME human step (HANDOFF §9): connect accounts
+ point Repurpose at the outbox. After that, posting is automatic.

Loosely coupled behind an `Adapter` protocol (Eric is trialing Repurpose) — moving
to platform APIs later is a new adapter, not a rewrite.

Two safety properties hold here because QC is AUTO (HANDOFF §9):
- Every clip clears `guardrails.publish_allowed` again right before delivery
  (transformed, no music, clean title) — defense in depth.
- DISABLED by default (`distribution.enabled: false`) until accounts are connected,
  so building/testing this never risks an accidental public post.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any, Protocol

from . import db, guardrails
from .config import ROOT, settings


# ── auto-QC (Eric's call §9) ──────────────────────────────────────────────────

def qc_decision(clip: dict[str, Any]) -> tuple[str, str]:
    """Auto-QC verdict for one clip. Pure.

    'approve' only if it clears the publish gate. fmt=='auto-clip' means the clip
    went through our cut + caption (+ hook) pipeline → transformed (not a raw
    reupload). The in-code filters are the only gate now, so this stays strict.
    """
    meta = {
        "transformed": clip.get("fmt") == "auto-clip",
        "has_music": bool(clip.get("has_music", False)),
        "title": clip.get("post_title") or clip.get("source_creator") or "",
    }
    ok, reason = guardrails.publish_allowed(meta)
    return ("approve", "") if ok else ("reject", reason)


def auto_qc(db_path: Any = None) -> dict[str, int]:
    """Apply the auto-QC verdict to every pending_qc clip. Returns counts."""
    counts = {"approved": 0, "rejected": 0}
    for clip in db.pending_qc_clips(db_path):
        decision, reason = qc_decision(clip)
        db.record_qc(clip["clip_id"], decision, reviewer="auto-qc", note=reason, db_path=db_path)
        counts["approved" if decision == "approve" else "rejected"] += 1
    return counts


# ── distribution adapter ──────────────────────────────────────────────────────

def caption_for(clip: dict[str, Any]) -> str:
    """Post caption/title for a clip (the burned hook is the on-screen title)."""
    return clip.get("post_title") or f"{clip.get('source_creator', '')} — clip".strip(" —")


class Adapter(Protocol):
    def deliver(self, clip_path: Path, meta: dict) -> str: ...


class OutboxAdapter:
    """Drops clip + a JSON metadata sidecar into the folder Repurpose.io watches."""

    def __init__(self, outbox: Path):
        self.outbox = outbox

    def deliver(self, clip_path: Path, meta: dict) -> str:
        self.outbox.mkdir(parents=True, exist_ok=True)
        dest = self.outbox / clip_path.name
        if clip_path.exists():
            shutil.copy2(clip_path, dest)
        (self.outbox / f"{clip_path.stem}.json").write_text(json.dumps(meta, indent=2))
        return str(dest)


def _resolve_outbox(cfg: dict) -> Path:
    path = Path(cfg.get("outbox", "data/outbox"))
    return path if path.is_absolute() else ROOT / path


def build_adapter(cfg: dict) -> Adapter:
    # Only one adapter today; `cfg['adapter']` reserved for a future API adapter.
    return OutboxAdapter(_resolve_outbox(cfg))


def run(db_path: Any = None) -> dict[str, Any]:
    """Hand approved clips to the distribution adapter, marking them posted.

    Gated by `distribution.enabled` (default off) until Repurpose accounts are
    connected. Re-checks the publish gate per clip — defense in depth under auto-QC.
    """
    cfg = settings().get("distribution", {})
    if not cfg.get("enabled", False):
        n = len(db.approved_clips(db_path))
        return {"enabled": False, "delivered": 0, "waiting": n,
                "note": "distribution OFF — connect Repurpose accounts, point it at the "
                        "outbox, then set distribution.enabled: true"}
    adapter = build_adapter(cfg)
    delivered = blocked = 0
    for clip in db.approved_clips(db_path):
        meta = {
            "transformed": clip.get("fmt") == "auto-clip",
            "has_music": bool(clip.get("has_music", False)),
            "title": caption_for(clip),
        }
        ok, reason = guardrails.publish_allowed(meta)
        if not ok:
            db.set_clip_status(clip["clip_id"], "rejected", db_path=db_path)
            blocked += 1
            continue
        dest = adapter.deliver(Path(clip.get("post_url") or ""), {
            "clip_id": clip["clip_id"], "caption": caption_for(clip),
            "channel": clip.get("channel"), "platform": clip.get("platform"),
        })
        db.set_clip_status(clip["clip_id"], "posted", db_path=db_path,
                           post_url=dest, posted_at=db.now())
        delivered += 1
    return {"enabled": True, "delivered": delivered, "blocked": blocked}
