"""Stage 5 (capture half) — pull performance into the DB.

Two sources, in order of how much they need:
  • public views   – yt-dlp on each posted clip URL. No creds. Works today.
  • full analytics  – retention %, RPM, ad revenue. Needs YouTube Analytics OAuth
                      per owned channel (see capture_full_analytics docstring).

Public views close the loop on the number that matters most early: how many
views each clip is pulling. Ad revenue follows once owned channels hit YPP.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

from . import db
from .db import connect


def _ytdlp_views(url: str) -> int | None:
    """Current public view count for one video URL (YouTube/TikTok/IG)."""
    cmd = ["yt-dlp", "--dump-json", "--skip-download", url]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
    if proc.returncode != 0:
        return None
    try:
        return int(json.loads(proc.stdout).get("view_count") or 0)
    except (json.JSONDecodeError, ValueError):
        return None


def capture_public(db_path: Path | None = None) -> int:
    """Snapshot public views for every posted clip that has a URL. Returns count."""
    db.init_db(db_path)
    with connect(db_path) as conn:
        rows = conn.execute(
            "SELECT clip_id, post_url FROM clips "
            "WHERE status = 'posted' AND post_url IS NOT NULL"
        ).fetchall()
    n = 0
    for r in rows:
        views = _ytdlp_views(r["post_url"])
        if views is None:
            print(f"  ! no views for {r['clip_id']} ({r['post_url']})")
            continue
        db.insert_metric({"clip_id": r["clip_id"], "views": views}, db_path)
        n += 1
    return n


def capture_full_analytics(db_path: Path | None = None) -> int:
    """Retention %, RPM, ad revenue per owned channel via YouTube Analytics API.

    Requires OAuth per channel (YT_OAUTH_CLIENT_SECRET_JSON in .env). This is a
    deliberate stub — wiring real OAuth is a setup task, not something to fake.
    To enable: install google-api-python-client + google-auth-oauthlib, run the
    one-time consent flow per channel, then query the 'reports' endpoint for
    estimatedRevenue, averageViewPercentage, and views grouped by video.
    """
    raise NotImplementedError(
        "Full analytics needs YouTube Analytics OAuth per channel. "
        "Public views (capture_public) cover the early loop; "
        "wire OAuth when owned channels approach YPP. See docstring."
    )
