"""Stage 5 (capture half) — pull performance into the DB.

Two sources, in order of how much they need:
  • public views   – yt-dlp on each posted clip URL. No creds. Works today.
  • full analytics  – retention %, RPM, ad revenue. Needs YouTube Analytics OAuth
                      per owned channel (see capture_full_analytics docstring).

Public views close the loop on the number that matters most early: how many
views each clip is pulling. Ad revenue follows once owned channels hit YPP.
"""
from __future__ import annotations

import datetime
import json
import os
import subprocess
from pathlib import Path

from . import db
from .config import env, settings
from .db import connect

YT_WATCH = "youtube.com/watch?v="
HOOK_WINDOW = 0.2   # first 20% of a Short ≈ the hook window (where the hook must hold)


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


def resolve_published(db_path: Path | None = None) -> int:
    """Resolve posted clips' Postiz post_id → the published YouTube URL (releaseURL).

    Postiz publishes to YouTube async, so the post starts with only a Postiz post_id.
    Once PUBLISHED, GET /posts exposes `releaseURL`/`releaseId` (the YouTube video id).
    We copy that URL into post_url so capture_public + capture_full_analytics can use it.
    Returns how many clips got resolved this pass. Safe no-op without a Postiz token.
    """
    import requests

    token = os.getenv("POSTIZ_API_TOKEN") or ""
    if not token:
        return 0
    db.init_db(db_path)
    with connect(db_path) as conn:
        pending = conn.execute(
            "SELECT clip_id, post_id FROM clips WHERE status='posted' AND post_id IS NOT NULL "
            "AND (post_url IS NULL OR post_url NOT LIKE '%youtube.com/watch%')"
        ).fetchall()
    if not pending:
        return 0
    api = settings()["distribution"]["postiz"]["api_url"].rstrip("/")
    start = (datetime.date.today() - datetime.timedelta(days=10)).isoformat() + "T00:00:00Z"
    end = (datetime.date.today() + datetime.timedelta(days=2)).isoformat() + "T00:00:00Z"
    try:
        resp = requests.get(f"{api}/posts", headers={"Authorization": token},
                            params={"startDate": start, "endDate": end}, timeout=30)
        resp.raise_for_status()
        data = resp.json()
    except (requests.RequestException, ValueError):
        return 0
    posts = data if isinstance(data, list) else (data.get("posts") or data.get("data") or [])
    # Keep the REAL publish time (publishDate), not our schedule slot — so timing analysis
    # ("did a great clip ship at the wrong hour?") is grounded in when it actually went live.
    info_by_id = {p.get("id"): (p.get("releaseURL"), p.get("publishDate")) for p in posts
                  if p.get("state") == "PUBLISHED" and p.get("releaseURL")}
    n = 0
    for r in pending:
        info = info_by_id.get(r["post_id"])
        if info:
            url, published = info
            db.set_clip_status(r["clip_id"], "posted", db_path=db_path,
                               post_url=url, posted_at=published or db.now())
            n += 1
    return n


def _video_id(url: str | None) -> str | None:
    """Extract a YouTube video id from a watch URL (else None)."""
    if url and YT_WATCH in url:
        return url.split("watch?v=", 1)[1].split("&", 1)[0]
    return None


def capture_public(db_path: Path | None = None) -> int:
    """Snapshot public views for every posted clip that has a URL. Returns count."""
    db.init_db(db_path)
    resolve_published(db_path)  # turn Postiz post_ids into YouTube URLs first
    with connect(db_path) as conn:
        rows = conn.execute(
            "SELECT clip_id, post_url FROM clips "
            "WHERE status = 'posted' AND post_url LIKE '%youtube.com/watch%'"
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


def _yt_creds():
    """Build YouTube Analytics OAuth creds from .env (scripts/yt_oauth.py wrote them).
    Returns None if creds or the google libs are absent (so the loop never hard-breaks)."""
    try:
        from google.oauth2.credentials import Credentials
    except ImportError:
        return None
    env()  # ensures .env is loaded
    cid, secret, refresh = (os.getenv("YT_CLIENT_ID"), os.getenv("YT_CLIENT_SECRET"),
                            os.getenv("YT_REFRESH_TOKEN"))
    if not (cid and secret and refresh):
        return None
    return Credentials(token=None, refresh_token=refresh, client_id=cid,
                       client_secret=secret, token_uri="https://oauth2.googleapis.com/token")


def analyze_retention(curve: list[tuple[float, float]]) -> dict | None:
    """Turn an audience-retention curve [(elapsedRatio, watchRatio), ...] into the signals
    that explain WHY a clip wins or loses: how well the HOOK holds (swipe-away in the first
    20%) and where the single biggest drop happens. Pure. None if the curve is unreadably short.

    watchRatio ≈ fraction of viewers still watching at that point (≈1.0 at the very start).
    """
    pts = sorted((float(e), float(w)) for e, w in curve if e is not None and w is not None)
    if len(pts) < 3:
        return None
    hook_pts = [w for e, w in pts if e <= HOOK_WINDOW]
    hook_ret = hook_pts[-1] if hook_pts else pts[0][1]
    drops = [(pts[i][1] - pts[i + 1][1], pts[i + 1][0]) for i in range(len(pts) - 1)]
    biggest_drop, at = max(drops, key=lambda d: d[0]) if drops else (0.0, 0.0)
    return {
        "hook_retention": round(hook_ret, 3),
        "swipe_away_pct": round(max(0.0, 1.0 - hook_ret) * 100, 1),   # % gone by the hook's end
        "biggest_drop_pct": round(max(0.0, biggest_drop) * 100, 1),
        "biggest_drop_at": round(at, 2),                              # where (0-1 of the clip)
    }


def _fetch_retention(ya, video_id: str, start: str, end: str) -> list[tuple[float, float]] | None:
    """Pull the audience-retention curve for one video (None if YT has no data yet)."""
    try:
        rep = ya.reports().query(
            ids="channel==MINE", startDate=start, endDate=end,
            metrics="audienceWatchRatio", dimensions="elapsedVideoTimeRatio",
            filters=f"video=={video_id}").execute()
    except Exception:  # noqa: BLE001
        return None
    rows = rep.get("rows") or []
    return [(r[0], r[1]) for r in rows] if rows else None


def capture_full_analytics(db_path: Path | None = None) -> int:
    """Per-clip retention % + ad revenue from the YouTube Analytics API (owned channel).

    Uses the OAuth creds from scripts/yt_oauth.py. For each posted clip resolved to a
    YouTube video id, query the owner-only metrics and store them so scoring can weight
    retention + revenue, not just public views. Safe no-op without creds. Returns updates.
    """
    creds = _yt_creds()
    if creds is None:
        return 0
    from googleapiclient.discovery import build
    db.init_db(db_path)
    resolve_published(db_path)
    with connect(db_path) as conn:
        rows = conn.execute(
            "SELECT clip_id, post_url, posted_at FROM clips "
            "WHERE status='posted' AND post_url LIKE '%youtube.com/watch%'"
        ).fetchall()
    if not rows:
        return 0
    ya = build("youtubeAnalytics", "v2", credentials=creds)
    today = datetime.date.today().isoformat()
    n = 0
    for r in rows:
        vid = _video_id(r["post_url"])
        if not vid:
            continue
        start = (r["posted_at"] or today)[:10]
        try:
            rep = ya.reports().query(
                ids="channel==MINE", startDate=start, endDate=today,
                metrics="views,averageViewPercentage,estimatedRevenue",
                dimensions="video", filters=f"video=={vid}").execute()
        except Exception:  # noqa: BLE001 — one video's failure must not stop the rest
            continue
        srows = rep.get("rows")
        if not srows:
            continue  # no owned data yet — don't overwrite the public-view snapshot with zeros
        row = srows[0]  # [video, views, avgViewPct, estRevenue]
        ret = analyze_retention(_fetch_retention(ya, vid, start, today) or [])
        db.insert_metric({
            "clip_id": r["clip_id"],
            "views": int(row[1]) if len(row) > 1 else 0,
            "retention_pct": float(row[2]) if len(row) > 2 else 0.0,
            "ad_revenue": float(row[3]) if len(row) > 3 else 0.0,
            "swipe_away_pct": ret["swipe_away_pct"] if ret else None,  # hook drop-off (the 'why')
        }, db_path)
        n += 1
    return n
