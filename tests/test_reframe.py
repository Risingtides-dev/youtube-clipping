"""Face-pan reframe — pure crop-x expression logic (no OpenCV / ffmpeg)."""
from __future__ import annotations

from ycp import reframe


def test_empty_track_returns_none():
    assert reframe.crop_x_expr([], 3413) is None


def test_static_track_centers_and_clamps():
    track = [(i * 0.3, 0.5) for i in range(40)]
    assert reframe.crop_x_expr(track, 3413, crop_w=1080) == str(int(0.5 * 3413 - 540))


def test_track_clamps_to_frame_edges():
    left = [(i * 0.3, 0.0) for i in range(40)]
    right = [(i * 0.3, 1.0) for i in range(40)]
    assert reframe.crop_x_expr(left, 3413) == "0"
    assert reframe.crop_x_expr(right, 3413) == str(3413 - 1080)


def test_sustained_pan_builds_conditional_expression():
    track = [(i * 0.3, 0.2) for i in range(20)] + [(6 + i * 0.3, 0.85) for i in range(20)]
    expr = reframe.crop_x_expr(track, 3413)
    assert expr.startswith("if(lt(t")  # hard-cut pan between two positions
