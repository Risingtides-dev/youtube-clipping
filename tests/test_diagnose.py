"""Diagnose (the WHY layer) — fallback paths only; never hits the network in tests."""
from __future__ import annotations

import pandas as pd

from ycp import diagnose, hooks


def test_diagnose_none_without_key(monkeypatch):
    monkeypatch.setattr(hooks, "_api_key", lambda: None)
    # 10 clips but no DeepSeek key → None (no analysis to write, no crash).
    assert diagnose.diagnose({"scored": pd.DataFrame([{"v": 1}] * 10)}) is None


def test_diagnose_none_when_too_few_clips(monkeypatch):
    # Key present but below the minimum sample → None BEFORE any API call.
    monkeypatch.setattr(hooks, "_api_key", lambda: "fake-key")
    assert diagnose.diagnose({"scored": pd.DataFrame([{"v": 1}] * 3)}) is None
