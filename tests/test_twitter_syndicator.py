#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for Twitter / X syndicator and carousel deck integration.
"""

from core.adapters.syndication.targets import TARGET_REGISTRY
from adapters.egress.syndication.twitter import TwitterSyndicator


def test_registry_contains_twitter():
    assert "twitter" in TARGET_REGISTRY
    assert TARGET_REGISTRY["twitter"] == TwitterSyndicator


def test_twitter_syndicator_metadata_and_payload():
    syn = TwitterSyndicator(config={"bearer_token": "mock_bearer_token"}, site_url="https://example.com")
    assert syn.PLUGIN_ID == "twitter"
    assert syn.DISPLAY_NAME == "Twitter / X"
    assert syn.ICON == "𝕏"
    assert syn.is_enabled() is True

    payload = syn.format_payload(
        title="Building Autonomous AI Agents with AGY",
        slug="ai-agents-agy",
        content="## Introduction\nIn this article, we explore how to build autonomous agentic workflows.\n\n![Hero](https://example.com/banner.png)",
        metadata={"tags": ["AI", "Tech", "Python"]}
    )

    assert "Building Autonomous AI Agents with AGY" in payload["title"]
    assert "https://example.com/ai-agents-agy" in payload["canonical_url"]
    assert "#AI" in payload["text"]
    assert "https://example.com/banner.png" in payload["images"]
    assert payload["total_images"] <= 4


def test_twitter_deck_resolution_prioritizes_16x9(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    # 模拟生成 16:9 画幅卡片
    deck_dir = tmp_path / ".plenipes" / "cache" / "cards" / "pitch-deck_16x9"
    deck_dir.mkdir(parents=True)
    for i in range(1, 6):
        (deck_dir / f"card_0{i}.jpg").write_bytes(f"card{i}".encode("utf-8"))

    syn = TwitterSyndicator(config={}, site_url="https://acme.org")
    payload = syn.format_payload(
        title="Q3 Technical Report",
        slug="pitch-deck",
        content="Summary without inline images.",
        metadata={}
    )

    # Twitter 最多装配 4 张卡片
    assert len(payload["images"]) == 4
    assert "card_01.jpg" in payload["images"][0]
    assert "card_04.jpg" in payload["images"][3]

