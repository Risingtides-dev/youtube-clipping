"""Channel-agnostic QC — resolution, routing, local dispatch (no network)."""
from __future__ import annotations

import pytest

from ycp import qc


def test_resolve_explicit_channel(monkeypatch):
    monkeypatch.setattr(qc, "_qc_cfg", lambda: {"channel": "telegram"})
    assert qc.resolve_channel() == "telegram"


def test_resolve_auto_prefers_slack_then_telegram_then_local(monkeypatch):
    monkeypatch.setattr(qc, "_qc_cfg", lambda: {"channel": "auto"})
    monkeypatch.setattr(qc, "env", lambda: {"slack_bot_token": "x", "slack_qc_channel": "c"})
    assert qc.resolve_channel() == "slack"
    monkeypatch.setattr(qc, "env", lambda: {"telegram_bot_token": "t", "telegram_qc_chat": "c"})
    assert qc.resolve_channel() == "telegram"
    monkeypatch.setattr(qc, "env", lambda: {})
    assert qc.resolve_channel() == "local"


def test_local_dispatch_writes_manifest(tmp_path, monkeypatch):
    monkeypatch.setattr(qc, "ROOT", tmp_path)
    clips = [{"clip_id": "x1", "source_creator": "A", "length_sec": 30, "post_url": "/p.mp4"}]
    assert qc._LocalChannel().dispatch(clips, None) == 1
    man = tmp_path / "data" / "qc-review.md"
    assert man.exists()
    body = man.read_text()
    assert "x1" in body and "qc-approve x1" in body


def test_decide_rejects_bad_decision():
    with pytest.raises(ValueError):
        qc.decide("x", "maybe")


def test_unknown_channel_raises():
    with pytest.raises(RuntimeError):
        qc._backend("carrier-pigeon")
