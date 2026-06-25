"""Capture tests — public-view snapshotting into the DB (owned-first; Whop cut)."""
from __future__ import annotations

from ycp import capture, db


def test_capture_public_snapshots_posted_clips(tmp_path, monkeypatch):
    dbp = tmp_path / "t.db"
    db.init_db(dbp)
    # one posted clip with a URL (captured), one without a URL (ignored)
    db.insert_clip({"clip_id": "c1", "channel": "ch", "platform": "youtube", "lane": "owned",
                    "fmt": "x", "hook_type": "q", "length_sec": 30,
                    "status": "posted", "post_url": "https://www.youtube.com/watch?v=abc123"}, dbp)
    db.insert_clip({"clip_id": "c2", "channel": "ch", "platform": "youtube", "lane": "owned",
                    "fmt": "x", "hook_type": "q", "length_sec": 30,
                    "status": "posted"}, dbp)

    monkeypatch.setattr(capture, "_ytdlp_views", lambda url: 4321)
    n = capture.capture_public(dbp)
    assert n == 1  # only the clip with a post_url is snapshotted

    df = db.clips_with_latest_metrics(dbp)
    by_id = {r["clip_id"]: r for _, r in df.iterrows()}
    assert by_id["c1"]["views"] == 4321
    assert by_id["c2"]["views"] == 0  # no URL -> never captured


def test_analyze_retention_reads_hook_dropoff():
    # 40% gone by the hook's end (20% of the clip); the cliff is at the 10% mark.
    curve = [(0.0, 1.0), (0.1, 0.6), (0.2, 0.6), (0.5, 0.5), (1.0, 0.4)]
    r = capture.analyze_retention(curve)
    assert r["swipe_away_pct"] == 40.0
    assert r["biggest_drop_at"] == 0.1 and r["biggest_drop_pct"] == 40.0


def test_analyze_retention_none_for_short_curve():
    assert capture.analyze_retention([(0.0, 1.0)]) is None


def test_capture_public_skips_when_no_views(tmp_path, monkeypatch):
    dbp = tmp_path / "t.db"
    db.init_db(dbp)
    db.insert_clip({"clip_id": "c1", "channel": "ch", "platform": "youtube", "lane": "owned",
                    "fmt": "x", "hook_type": "q", "length_sec": 30,
                    "status": "posted", "post_url": "https://www.youtube.com/watch?v=abc123"}, dbp)

    monkeypatch.setattr(capture, "_ytdlp_views", lambda url: None)  # fetch failed
    n = capture.capture_public(dbp)
    assert n == 0  # no metric written when views can't be fetched
