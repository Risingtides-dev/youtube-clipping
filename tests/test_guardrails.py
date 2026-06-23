"""Guardrails — avoid-list gate + publish gate (pure, load-bearing for auto-QC)."""
from __future__ import annotations

from ycp import guardrails


def test_avoid_list_blocks_disqualified_creators():
    assert not guardrails.creator_allowed("Joe Rogan", "@joerogan")
    assert not guardrails.creator_allowed("Andrew Tate", "")
    assert not guardrails.creator_allowed("Fresh & Fit", "@MyronGainesX")
    assert not guardrails.creator_allowed("MrBeast", "@MrBeast")        # mega-creator (HANDOFF §3)
    assert not guardrails.creator_allowed("Andrew Huberman", "@hubermanlab")


def test_avoid_list_allows_clean_creators():
    assert guardrails.creator_allowed("Jubilee", "@jubilee")
    assert guardrails.creator_allowed("Ramit Sethi", "@ramitsethi")
    assert guardrails.creator_allowed("Graham Stephan", "@grahamstephan")


def test_filter_creators_splits_and_reports():
    creators = [
        {"name": "Jubilee", "url": "https://youtube.com/@jubilee/videos"},
        {"name": "Joe Rogan", "url": "https://youtube.com/@joerogan/videos"},
        {"name": "Ramit Sethi", "url": "https://youtube.com/@ramitsethi/videos"},
    ]
    allowed, dropped = guardrails.filter_creators(creators)
    assert [c["name"] for c in allowed] == ["Jubilee", "Ramit Sethi"]
    assert dropped == ["Joe Rogan"]


def test_source_title_screen_flags_music_and_casino():
    assert guardrails.source_allowed("Great debate moment about taxes")[0]
    assert not guardrails.source_allowed("Drake - Official Music Video")[0]
    assert not guardrails.source_allowed("Biggest CASINO win ever (slots)")[0]


def test_publish_gate_requires_transformation_and_no_music():
    ok, _ = guardrails.publish_allowed(
        {"transformed": True, "has_music": False, "title": "Why this policy fails"})
    assert ok
    # raw reupload blocked
    assert not guardrails.publish_allowed({"transformed": False, "title": "x"})[0]
    # music blocked
    assert not guardrails.publish_allowed(
        {"transformed": True, "has_music": True, "title": "x"})[0]
    # missing transformed -> conservative block
    assert not guardrails.publish_allowed({"title": "x"})[0]
