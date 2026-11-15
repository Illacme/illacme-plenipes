#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for Jike and Weibo multi-image carousel syndicators.
"""

from core.adapters.syndication.targets import TARGET_REGISTRY
from adapters.egress.syndication.jike import JikeSyndicator
from adapters.egress.syndication.weibo import WeiboSyndicator


def test_registry_contains_jike_and_weibo():
    assert "jike" in TARGET_REGISTRY
    assert "weibo" in TARGET_REGISTRY
    assert TARGET_REGISTRY["jike"] == JikeSyndicator
    assert TARGET_REGISTRY["weibo"] == WeiboSyndicator


def test_jike_syndicator_metadata_and_format_payload():
    syn = JikeSyndicator(config={"token": "test_jike_token", "topic_id": "test_topic_123"}, site_url="https://example.com")
    assert syn.PLUGIN_ID == "jike"
    assert syn.DISPLAY_NAME == "即刻"
    assert syn.ICON == "🟡"
    assert syn.is_enabled() is True

    payload = syn.format_payload(
        title="测试即刻多图分发",
        slug="test-jike",
        content="# 核心要点\n即刻技术圈子测试文章。\n\n![插图1](https://example.com/img1.jpg)",
        metadata={"tags": ["科技", "独立开发"]}
    )

    assert "测试即刻多图分发" in payload["title"]
    assert "核心要点" in payload["content"]
    assert "https://example.com/img1.jpg" in payload["images"]
    assert payload["topic_id"] == "test_topic_123"


def test_weibo_syndicator_metadata_and_format_payload():
    syn = WeiboSyndicator(config={"access_token": "test_wb_token"}, site_url="https://example.com")
    assert syn.PLUGIN_ID == "weibo"
    assert syn.DISPLAY_NAME == "微博"
    assert syn.ICON == "🔴"
    assert syn.is_enabled() is True

    payload = syn.format_payload(
        title="测试微博九宫格分发",
        slug="test-weibo",
        content="## 深度解析\n这是一条测试微博九宫格内容。\n\n![封面图](https://example.com/cover.jpg)",
        metadata={"tags": ["AI技术", "架构演进"]}
    )

    assert "测试微博九宫格分发" in payload["title"]
    assert "https://example.com/cover.jpg" in payload["images"]
    assert "#AI技术#" in payload["status"]


def test_carousel_deck_resolution(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    deck_dir = tmp_path / ".plenipes" / "cache" / "cards" / "demo-doc_3x4"
    deck_dir.mkdir(parents=True)
    (deck_dir / "card_01.jpg").write_bytes(b"fake1")
    (deck_dir / "card_02.jpg").write_bytes(b"fake2")

    syn = JikeSyndicator(config={}, site_url="https://myblog.com")
    payload = syn.format_payload(
        title="卡片测试",
        slug="demo-doc",
        content="正文无图",
        metadata={}
    )

    assert len(payload["images"]) == 2
    assert "card_01.jpg" in payload["images"][0]
    assert "card_02.jpg" in payload["images"][1]

