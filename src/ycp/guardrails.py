"""Guardrails enforced IN CODE, not just docs (HANDOFF §10).

Two gates protect the whole operation — a single strike pattern can demonetize a
faceless network channel-wide:

1. **Avoid-list gate (sourcing).** Runs BEFORE the score — it's a gate, not a
   deduction. Disqualified creators (Content-ID minefields, paywalled, hate-flagged,
   and the mega-creators that are turbo-only/AVOID per HANDOFF §3) never enter the
   queue. Per-video title screening drops music/casino/licensed-IP red flags.

2. **Publish gate (distribution).** Because QC is AUTO (HANDOFF §9), this is the
   last line before a clip goes public: it must be TRANSFORMED (our hook/caption,
   not a raw reupload) and carry no copyrighted-music signal.

Everything here is pure and unit-tested — these are the load-bearing checks for
auto-posting, so they must be deterministic and verifiable.
"""
from __future__ import annotations

import re

# ── Avoid-list (SOURCE-INTELLIGENCE.md §Avoid + HANDOFF §3 mega-creator ruling) ──
# Normalized substrings matched against creator name AND handle.
_AVOID_CREATORS = {
    "joe rogan", "jre", "andrew tate", "tate", "fresh & fit", "freshandfit",
    "myrongainesx", "mssp", "matt and shane", "matt & shane", "jordan peterson",
    "andrew huberman", "huberman", "peter attia", "plaqueboymax", "lacy", "caedrel",
    # Mega-creators: turbo-only or AVOID as owned lanes (HANDOFF §3).
    "mrbeast", "mr beast", "ishowspeed", "speed", "kai cenat", "taylor swift",
}

# Title red flags → music / gambling / licensed-IP = Content-ID / DMCA risk.
_AVOID_TITLE_TERMS = {
    "official music video", "official video", "lyric", "lyrics", "ft.",
    "feat.", "concert", "live performance", "music video", "casino", "slots",
    "gambling", "betting", "stake.com", "full album", "official audio",
}


def _norm(s: str) -> str:
    """Lowercase, strip @ and non-alphanumerics-to-spaces for fuzzy matching."""
    return re.sub(r"[^a-z0-9 ]+", "", (s or "").lower().replace("@", " ")).strip()


def creator_allowed(name: str = "", handle: str = "") -> bool:
    """False if the creator is on the avoid-list (gate runs BEFORE scoring)."""
    blob = f"{_norm(name)} {_norm(handle)}"
    return not any(bad in blob for bad in (_norm(b) for b in _AVOID_CREATORS))


def source_allowed(title: str) -> tuple[bool, str]:
    """Screen a single source video's title for music/casino/licensed-IP flags."""
    low = (title or "").lower()
    for term in _AVOID_TITLE_TERMS:
        if term in low:
            return False, f"title flag: '{term}'"
    return True, ""


def filter_creators(creators: list[dict]) -> tuple[list[dict], list[str]]:
    """Split creators into (allowed, dropped-names) by the avoid-list. Pure."""
    allowed, dropped = [], []
    for c in creators:
        if creator_allowed(c.get("name", ""), c.get("url", "") or c.get("handle", "")):
            allowed.append(c)
        else:
            dropped.append(c.get("name", "?"))
    return allowed, dropped


def publish_allowed(clip: dict) -> tuple[bool, str]:
    """Last gate before auto-posting (QC is auto). Require transformation + no music.

    `clip` is expected to carry:
      - transformed: bool   (our hook/caption/cut applied — not a raw reupload)
      - has_music:   bool    (copyrighted-music signal detected)
      - title:       str     (also title-screened)
    Conservative by default: missing `transformed` is treated as NOT transformed.
    """
    if not clip.get("transformed", False):
        return False, "not transformed (raw reupload risks channel-wide demonetization)"
    if clip.get("has_music", False):
        return False, "copyrighted-music signal — Content-ID would claim it"
    ok, reason = source_allowed(clip.get("title", ""))
    if not ok:
        return False, reason
    return True, ""
