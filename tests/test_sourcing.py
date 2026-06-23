"""Sourcing parser/ranker tests — pure logic, no network."""
from __future__ import annotations

from ycp import sourcing

NOW = 1_700_000_000.0  # fixed clock for deterministic velocity

RAW = [
    {"id": "v1", "title": "Hot debate moment", "view_count": 500_000,
     "timestamp": NOW - 3600 * 10, "channel_id": "UC1"},          # 10h old -> 50k/h
    {"id": "v2", "title": "Slow burn", "view_count": 120_000,
     "timestamp": NOW - 3600 * 240, "channel_id": "UC1"},         # 240h old -> 500/h
    {"id": "v3", "title": "No timestamp", "view_count": 80_000, "channel_id": "UC1"},
    {"id": None, "title": "garbage"},                              # dropped
]


def test_parse_computes_velocity():
    rows = sourcing.parse_entries(RAW, "Flagrant", "whop", now_epoch=NOW)
    assert len(rows) == 3  # the id=None entry is dropped
    by_id = {r["video_id"]: r for r in rows}
    assert by_id["v1"]["view_velocity"] == 50_000.0
    assert by_id["v2"]["view_velocity"] == 500.0
    # no timestamp -> velocity falls back to raw views
    assert by_id["v3"]["view_velocity"] == 80_000.0


def test_rank_filters_and_sorts():
    rows = sourcing.parse_entries(RAW, "Flagrant", "whop", now_epoch=NOW)
    ranked = sourcing.rank(rows, {"min_views": 100_000})
    ids = [r["video_id"] for r in ranked]
    assert "v3" not in ids                      # 80k < 100k filtered out
    assert ids[0] == "v1"                        # highest velocity first
    assert ranked == sorted(ranked, key=lambda r: r["view_velocity"], reverse=True)


def test_render_queue_md_handles_empty():
    assert "empty" in sourcing.render_queue_md([])


def test_parse_meta_lines_reads_real_metadata():
    # Simulates `yt-dlp --print _META_FORMAT`: the empty-queue bug was flat mode
    # returning NA view_count; non-flat output below carries real numbers.
    stdout = (
        "v1\t500000\t1699999999\tUC1\tHot debate moment\n"
        "v2\tNA\tNA\tUC2\tPrivate or members-only\n"   # missing fields -> None
        "v3\t80000\t1699990000\tUC3\tTitle with\ta tab inside\n"  # tab in title kept
        "\n"                                                       # blank line ignored
    )
    rows = sourcing._parse_meta_lines(stdout)
    assert len(rows) == 3
    by_id = {r["id"]: r for r in rows}
    assert by_id["v1"]["view_count"] == 500_000
    assert by_id["v1"]["timestamp"] == 1699999999.0
    assert by_id["v2"]["view_count"] is None          # NA normalized to None
    assert by_id["v2"]["timestamp"] is None
    assert by_id["v3"]["title"] == "Title with\ta tab inside"

    # And the existing pure pipeline consumes it unchanged:
    rows_with_views = [r for r in rows if r["view_count"]]
    candidates = sourcing.parse_entries(rows_with_views, "Flagrant", "owned", now_epoch=NOW)
    ranked = sourcing.rank(candidates, {"min_views": 50_000})
    assert [r["video_id"] for r in ranked][0] == "v1"  # real views -> non-empty queue
