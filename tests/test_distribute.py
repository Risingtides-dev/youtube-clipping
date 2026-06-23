"""Distribution — auto-QC verdict + outbox adapter (pure / filesystem, no network)."""
from __future__ import annotations

from pathlib import Path

from ycp import distribute


def test_auto_qc_approves_transformed_clean_clip():
    decision, _ = distribute.qc_decision(
        {"fmt": "auto-clip", "source_creator": "Ramit Sethi"})
    assert decision == "approve"


def test_auto_qc_rejects_untransformed_clip():
    # fmt != auto-clip → treated as raw reupload → rejected
    decision, reason = distribute.qc_decision({"fmt": "raw", "source_creator": "x"})
    assert decision == "reject" and "transform" in reason.lower()


def test_caption_falls_back_to_creator():
    assert distribute.caption_for({"source_creator": "Codie Sanchez"}) == "Codie Sanchez — clip"


def test_outbox_adapter_writes_clip_and_sidecar(tmp_path):
    src = tmp_path / "clip.mp4"
    src.write_bytes(b"fake mp4")
    adapter = distribute.OutboxAdapter(tmp_path / "outbox")
    dest = adapter.deliver(src, {"clip_id": "abc", "caption": "Hook here"})
    assert Path(dest).exists()
    sidecar = (tmp_path / "outbox" / "clip.json")
    assert sidecar.exists() and "Hook here" in sidecar.read_text()


def test_run_disabled_by_default_reports_gate(monkeypatch):
    # No settings override → distribution.enabled defaults to false in config.
    result = distribute.run(db_path=None)
    assert result["enabled"] is False and "Repurpose" in result["note"]
