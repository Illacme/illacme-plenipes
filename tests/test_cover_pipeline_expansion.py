#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes - Cover Pipeline Expansion Test Suite
测试职责：验证正文首图优先提取 (first_image) 与 AI 智能生图 (ai_generation) 后端供给链路及容错自愈。
严格遵守用户规则 10（不破坏用户真实文库与配置）与规则 11（全自动化闭环凭据）。
"""

import os
import io
import shutil
import tempfile
import unittest
from PIL import Image

from core.design.cover_engine.cover_resolver import CoverResolver
from core.design.cover_engine.first_image_extractor import extract_first_image_from_doc
from core.design.cover_engine.ai_cover_generator import generate_ai_cover

class TestCoverPipelineExpansion(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.img_dir = os.path.join(self.temp_dir, "images")
        os.makedirs(self.img_dir, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_first_image_extractor_with_local_file(self):
        # 1. 创建一张真实的本地测试图片
        test_img_path = os.path.join(self.img_dir, "sample_cover.jpg")
        img = Image.new("RGB", (800, 600), color=(0, 200, 255))
        img.save(test_img_path, format="JPEG")

        # 2. 创建引用该图片的 Markdown 文稿
        doc_path = os.path.join(self.temp_dir, "post_with_img.md")
        with open(doc_path, "w", encoding="utf-8") as f:
            f.write("""---
title: 测试正文首图
---
这是正文导言。

![示例配图](images/sample_cover.jpg)

更多正文。
""")

        # 3. 执行提取与指定画幅裁切 (2.35:1 微信头条)
        data = extract_first_image_from_doc(
            doc_id="post_with_img.md",
            vault_root=self.temp_dir,
            aspect_ratio="2.35:1"
        )
        self.assertIsNotNone(data)
        out_img = Image.open(io.BytesIO(data))
        self.assertEqual(out_img.size, (1200, 510))

    def test_first_image_extractor_fallback_when_no_image(self):
        # 创建不含任何图片的文稿
        doc_path = os.path.join(self.temp_dir, "plain.md")
        with open(doc_path, "w", encoding="utf-8") as f:
            f.write("# 纯文本文章\n没有图片。")

        data = extract_first_image_from_doc(
            doc_id="plain.md",
            vault_root=self.temp_dir
        )
        self.assertIsNone(data)

        # 验证 CoverResolver 在 first_image 失败后能优雅降级至兜底 (不会抛异常)
        res_bytes, strat = CoverResolver.resolve_cover(
            title="纯文本文章",
            doc_id="plain.md",
            vault_root=self.temp_dir,
            strategy="first_image"
        )
        self.assertIsNotNone(res_bytes)
        # 降级至阶梯 1: og_card
        self.assertEqual(strat, "og_card")

    def test_ai_cover_generator_execution_and_self_healing(self):
        # 调用 AI 封面生成器 (在无外部付费 Key 环境下应平滑借道免 Key picsum 或优雅回退)
        res = generate_ai_cover(
            title="Sovereign AI Publishing",
            category="Technology",
            aspect_ratio="16:9",
            offset=1
        )
        # 即使无外部生图环境或由于网络离线，也必须安全无崩溃
        if res is not None:
            img_bytes, used_provider = res
            self.assertGreater(len(img_bytes), 1000)
            self.assertTrue(used_provider.startswith("ai_gen"))

    def test_cover_resolver_ai_generation_strategy_dispatch(self):
        # 调度 ai_generation 策略
        data, strat = CoverResolver.resolve_cover(
            title="Distributed Architecture",
            slug="dist-arch",
            strategy="ai_generation",
            aspect_ratio="16:9"
        )
        self.assertIsNotNone(data)
        self.assertGreater(len(data), 500)
        # 应该要么是 ai_gen (...) 要么是降级到 og_card
        self.assertTrue(strat.startswith("ai_gen") or strat in ("og_card", "brand_presets", "minimal_badge"))

if __name__ == "__main__":
    unittest.main()
