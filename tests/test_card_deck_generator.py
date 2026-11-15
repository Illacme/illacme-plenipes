# -*- coding: utf-8 -*-
"""
🧪 CardDeck Generator & Segmenter Unit Tests
验证 3:4 知识卡片海报生成器切片准确性、Pillow 渲染输出完整性与 ZIP 打包。
"""

import os
import io
from PIL import Image

from core.design.card_deck.deck_segmenter import DeckSegmenter, DeckCardData
from core.design.card_deck.deck_card_renderer import render_deck_card
from core.design.card_deck.deck_generator import DeckGenerator


SAMPLE_MARKDOWN = """---
title: "深入理解现代出版主权架构"
author: "Eason"
category: "系统设计"
description: "本文系统性剖析了如何构建完全属于创作者的离线优先多端出版流水线。"
---

# 深入理解现代出版主权架构

前言导读：在数字化时代，内容创作者需要真正掌握数据主权与排版控制权。

## 01. 核心工程契约与去中心化存储

- 本地优先优先策略，原稿 100% 存储于物理文库。
- 零破坏性门禁保障，任何外部推送均具备沙箱模拟。
- 基于 Git 与 SQLite 双轨持久化，状态可追溯。

> “主权不仅是拥有数据，更是拥有独立解释与分发数据的能力。”

## 02. 多态排版与多媒介衍生

通过单一 Markdown 源稿，实现网站全站静态托管、电子书离线装订与社交媒体高清卡片输出。
支持移动端 3:4 黄金画幅适配与自动化微排版。

## 03. 智能自愈与端到端闭环

当外部网络或第三方平台拦截请求时，系统自愈诊断中枢能够提取出口 IP 并给出指引。
一键重发无需重新编译全文。
"""


def test_deck_segmenter_with_sample_markdown():
    cards = DeckSegmenter.segment_document(
        content=SAMPLE_MARKDOWN,
        metadata={"title": "深入理解现代出版主权架构", "author": "Eason", "category": "系统设计"},
        max_cards=6
    )

    assert len(cards) >= 3
    # 第一张必须是封面
    assert cards[0].card_type == "cover"
    assert "深入理解现代出版主权架构" in cards[0].title
    assert cards[0].author == "Eason"

    # 中间必须有 content 卡片
    content_cards = [c for c in cards if c.card_type == "content"]
    assert len(content_cards) >= 2
    assert any("核心工程契约" in c.title for c in content_cards)
    assert any(len(c.points) > 0 for c in content_cards)

    # 最后一张必须是 closing
    assert cards[-1].card_type == "closing"
    assert cards[-1].total == len(cards)


def test_deck_card_renderer_generates_valid_image():
    card = DeckCardData(
        index=1,
        total=5,
        card_type="cover",
        title="测试卡片标题排版",
        subtitle="这是一段测试用的副标题摘要说明文本",
        category="技术架构",
        author="Tester",
        brand_name="TEST BRAND"
    )

    # 1. 验证 3:4 比例 (900x1200)
    img_3x4 = render_deck_card(card, offset=0, aspect_ratio="3:4")
    assert img_3x4 is not None
    img = Image.open(io.BytesIO(img_3x4))
    assert img.size == (900, 1200)
    assert img.format == "JPEG"

    # 2. 验证 1:1 比例 (1080x1080)
    img_1x1 = render_deck_card(card, offset=1, aspect_ratio="1:1")
    assert img_1x1 is not None
    img_sq = Image.open(io.BytesIO(img_1x1))
    assert img_sq.size == (1080, 1080)

    # 3. 验证 16:9 比例 (1200x675)
    img_16x9 = render_deck_card(card, offset=2, aspect_ratio="16:9")
    assert img_16x9 is not None
    img_wide = Image.open(io.BytesIO(img_16x9))
    assert img_wide.size == (1200, 675)


def test_deck_generator_full_pipeline(tmp_path):
    result = DeckGenerator.generate_deck(
        content=SAMPLE_MARKDOWN,
        slug="test-sovereign-deck",
        metadata={"title": "深入理解现代出版主权架构", "author": "Eason"},
        offset=2,
        max_cards=5,
        aspect_ratio="3:4",
        cache_base_dir=str(tmp_path)
    )

    assert result["status"] == "ok"
    assert result["slug"] == "test-sovereign-deck"
    assert result["aspect_ratio"] == "3:4"
    assert result["total"] >= 3
    assert len(result["cards"]) == result["total"]

    # 验证生成的文件物理存在于画幅隔离目录中
    deck_dir = os.path.join(tmp_path, "test-sovereign-deck_3x4")
    assert os.path.isdir(deck_dir)

    for c in result["cards"]:
        card_file = os.path.join(deck_dir, c["filename"])
        assert os.path.isfile(card_file)
        assert os.path.getsize(card_file) > 1000

    # 验证 ZIP 压缩包物理存在
    zip_file = os.path.join(deck_dir, result["zip_filename"])
    assert os.path.isfile(zip_file)
    assert os.path.getsize(zip_file) > 5000


def test_xiaohongshu_syndicator_auto_mounts_deck_cards(monkeypatch, tmp_path):
    from adapters.egress.syndication.xiaohongshu import XiaohongshuSyndicator
    syndicator = XiaohongshuSyndicator({}, site_url="https://example.com")

    # 生成一个临时的 deck
    slug = "mock-xhs-deck"
    deck_cache_dir = os.path.join(os.getcwd(), ".plenipes", "cache", "cards", slug)
    os.makedirs(deck_cache_dir, exist_ok=True)

    try:
        # 写入 3 张 mock 卡片图片
        for i in range(1, 4):
            with open(os.path.join(deck_cache_dir, f"card_{i:02d}.jpg"), "wb") as f:
                f.write(b"\xff\xd8\xff\xe0mock_jpeg_bytes")

        payload = syndicator.format_payload(
            title="测试小红书图集",
            slug=slug,
            content="正文内容",
            metadata={"tags": ["科技", "架构"]}
        )

        assert "images" in payload
        assert len(payload["images"]) == 3
        assert payload["images"][0] == f"https://example.com/api/design/assets/cards/{slug}/card_01.jpg"
        assert payload["images"][1] == f"https://example.com/api/design/assets/cards/{slug}/card_02.jpg"
        assert payload["images"][2] == f"https://example.com/api/design/assets/cards/{slug}/card_03.jpg"

    finally:
        import shutil
        if os.path.isdir(deck_cache_dir):
            shutil.rmtree(deck_cache_dir, ignore_errors=True)

