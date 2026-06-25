"""Archive adapter — drive routing + local copy (no network/rclone in tests)."""
from __future__ import annotations

from ycp import archive


def test_is_rclone_routing():
    assert archive._is_rclone("phoenix:Phoenix Protocol/clips")
    assert not archive._is_rclone("/Users/x/Google Drive")
    assert not archive._is_rclone("~/Drive")
    assert not archive._is_rclone("")          # off → not a remote


def test_archive_to_local_dir_copies_clip_and_sidecar(tmp_path, monkeypatch):
    clip = tmp_path / "c1.mp4"
    clip.write_bytes(b"video-bytes")
    dest = tmp_path / "drive"
    monkeypatch.setattr(archive, "settings",
                        lambda: {"archive": {"dest": str(dest), "subfolder_by_channel": True}})
    out = archive.archive_clip(clip, {"clip_id": "c1", "channel": "phoenix-protocol", "hook": "h"})
    assert out is not None
    assert (dest / "phoenix-protocol" / "c1.mp4").read_bytes() == b"video-bytes"
    assert (dest / "phoenix-protocol" / "c1.json").exists()   # metadata sidecar archived too


def test_archive_off_returns_none(tmp_path, monkeypatch):
    clip = tmp_path / "c.mp4"
    clip.write_bytes(b"v")
    monkeypatch.setattr(archive, "settings", lambda: {"archive": {"dest": ""}})
    assert archive.archive_clip(clip, {"clip_id": "c"}) is None
