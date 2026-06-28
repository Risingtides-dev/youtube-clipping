#!/usr/bin/env python3
"""Refinement-request builder for ONE clip — the form that opens when you drop a clip.

Stack atomic ops (started early/late · ended early/late · crop · captions · hook), hit send.
Writes a job to data/clips/.refine-queue/ that refine_loop.py runs through the DETERMINISTIC
refine engine (refine.apply) — same source, same moment, your adjustments. No guessing agent.

Usage:  refine_builder.py <clip.mp4>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from ycp import notes, refine          # noqa: E402

QUEUE = ROOT / "data" / "clips" / ".refine-queue"


def _time_to_sec(s: str) -> float:
    """'2:14' / '1:50:00' / '134' -> seconds."""
    s = s.strip()
    if ":" in s:
        sec = 0.0
        for part in s.split(":"):
            sec = sec * 60 + float(part or 0)
        return sec
    return float(s or 0)


def _meta(clip: Path, cid: str) -> dict:
    """The clip's meta sidecar (creator/hook/length), if present."""
    p = clip.parent / "meta" / f"{cid}.json"
    try:
        return json.loads(p.read_text())
    except (OSError, ValueError):
        return {}
MAGENTA, YELLOW, DIM, RESET = "\033[95m", "\033[93m", "\033[90m", "\033[0m"

# type -> prompt. start/end take a signed nudge ('2 earlier'/'1 later'); rest take guidance text.
COMPONENTS = [
    ("start",    "started too early / late", "how much? e.g. '2 earlier' or '1 later'"),
    ("end",      "ended too early / late",   "how much? e.g. '1 later' or '3 earlier'"),
    ("crop",     "cropping issue",           "describe the fix (e.g. 'he drifts left, keep him centred')"),
    ("captions", "captions issue",           "describe the fix"),
    ("hook",     "hook refinement",          "type the NEW hook text"),
]


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: refine_builder.py <clip.mp4>")
        return 2
    clip = Path(sys.argv[1])
    cid = notes.clip_id_for(clip)
    prov = refine.provenance(cid)

    print(f"\n{MAGENTA}⚡ REFINE{RESET}  {YELLOW}{clip.name}{RESET}")
    if prov and prov["post_title"]:
        print(f"{DIM}  hook: {prov['post_title']}{RESET}")

    # No stored source? Offer the paste-the-link salvage (backlog clips cut before provenance).
    pin = None
    if not prov or prov["source_url"] is None:
        meta = _meta(clip, cid)
        print(f"{DIM}  ⚠ no stored source for this clip (predates provenance). Paste the source "
              f"link to make it re-cuttable, or Enter to skip.{RESET}")
        url = input("  source URL → ").strip()
        if url:
            start = _time_to_sec(input("  start time in the video (m:ss or seconds) → "))
            length = float(meta.get("length_sec") or 30)
            pin = {"url": url, "start": start, "end": start + length,
                   "creator": meta.get("source_creator"), "title": meta.get("hook"),
                   "channel": meta.get("channel")}
            print(f"  {MAGENTA}✓{RESET} pinned {url.split('=')[-1]} @ {start:.0f}-{start + length:.0f}s\n")
        else:
            print(f"{DIM}  skipped — send will fail without a source.{RESET}\n")
    print()

    ops: list[dict] = []
    while True:
        for i, (_, label, _) in enumerate(COMPONENTS, 1):
            print(f"  [{i}] {label}")
        print(f"  {YELLOW}[s]{RESET} send   {DIM}[q] cancel{RESET}"
              + (f"   {DIM}({len(ops)} queued){RESET}" if ops else ""))
        try:
            choice = input("> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\ncancelled.")
            return 1
        if choice == "q":
            print("cancelled.")
            return 1
        if choice == "s":
            if not ops:
                print(f"{DIM}  nothing added yet.{RESET}")
                continue
            break
        if choice in {"1", "2", "3", "4", "5"}:
            key, label, hint = COMPONENTS[int(choice) - 1]
            val = input(f"  {label} — {hint}\n  → ").strip()
            if val:
                ops.append({"type": key, "value": val})
                print(f"  {MAGENTA}✓{RESET} {key}: {val}\n")
            else:
                print(f"{DIM}  skipped (empty).{RESET}\n")
        else:
            print(f"{DIM}  ? pick 1-5, s, or q.{RESET}")

    QUEUE.mkdir(parents=True, exist_ok=True)
    job = {"clip_id": cid, "file": str(clip), "ops": ops}
    if pin:
        job["pin"] = pin
    (QUEUE / f"{cid}.json").write_text(json.dumps(job))
    print(f"\n{MAGENTA}▶ SENT{RESET} — {len(ops)} op(s) queued: "
          f"{', '.join(o['type'] for o in ops)}.  Watch the dashboard.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
