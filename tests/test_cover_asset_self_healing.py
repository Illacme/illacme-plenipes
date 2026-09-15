#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes - Cover Asset Self-Healing Test Suite
测试职责：验证封面静态资源端点 JIT 即时自愈生成、磁盘写盘补齐与默认占位图平滑兜底。
严格遵守用户规则 10（不破坏用户真实文库与配置）与规则 11（全自动化闭环凭据）。
"""

import os
import io
import shutil
import tempfile
import unittest
from PIL import Image
from fastapi.testclient import TestClient

from services.api.server import app
from services.api.routes.design_shards.cover_asset_healer import (
    serve_cover_asset_or_heal,
    serve_default_cover,
    heal_missing_covers_in_vault
)

class TestCoverAssetSelfHealing(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.covers_dir = os.path.join(self.temp_dir, ".plenipes", "cache", "covers")
        os.makedirs(self.covers_dir, exist_ok=True)
        self.client = TestClient(app)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_jit_healing_non_existent_cover_returns_200_and_persists(self):
        fake_filename = "cover_auto_heal_test_888.jpg"
        target_path = os.path.join(self.covers_dir, fake_filename)
        self.assertFalse(os.path.isfile(target_path))

        # 1. 模拟 JIT 供给接口调用
        response = serve_cover_asset_or_heal(fake_filename, vault_root=self.temp_dir)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.media_type, "image/jpeg")
        self.assertEqual(response.headers.get("X-Cover-Healed"), "true")

        # 断言图片为合法且可解码的 JPEG
        img = Image.open(io.BytesIO(response.body))
        self.assertIn(img.format, ("JPEG", "PNG"))
        self.assertGreater(img.width, 0)
        self.assertGreater(img.height, 0)

        # 断言物理文件已经被自愈写盘落盘
        self.assertTrue(os.path.isfile(target_path))
        self.assertGreater(os.path.getsize(target_path), 0)

        # 2. 第二次请求同一文件，应当直接命中物理文件
        second_resp = serve_cover_asset_or_heal(fake_filename, vault_root=self.temp_dir)
        self.assertEqual(second_resp.status_code, 200)
        # 命中物理文件使用 FileResponse，不会有 X-Cover-Healed 动态生成标记
        self.assertIsNone(second_resp.headers.get("X-Cover-Healed"))

    def test_default_cover_endpoint(self):
        # 测试官方默认占位图端点
        resp = serve_default_cover(vault_root=self.temp_dir)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.media_type, "image/jpeg")

        # 校验默认文件已被持久化缓存
        default_file = os.path.join(self.covers_dir, "default_placeholder.jpg")
        self.assertTrue(os.path.isfile(default_file))

    def test_batch_heal_missing_covers_in_vault(self):
        # 在临时文库中创建两篇 Markdown 原稿，一篇引用了缺失封面，一篇无封面
        missing_cover_fn = "cover_broken_asset_999.jpg"
        doc1_path = os.path.join(self.temp_dir, "post1.md")
        with open(doc1_path, "w", encoding="utf-8") as f:
            f.write(f"""---
title: 测试文章标题999
category: Technology
cover: /api/design/assets/covers/{missing_cover_fn}
---
正文内容测试
""")

        doc2_path = os.path.join(self.temp_dir, "post2.md")
        with open(doc2_path, "w", encoding="utf-8") as f:
            f.write("""---
title: 无封面文章
---
正文内容
""")

        # 执行全库批量自愈扫描
        res = heal_missing_covers_in_vault(vault_root=self.temp_dir)
        self.assertGreaterEqual(res["scanned"], 2)
        self.assertIn(missing_cover_fn, res["healed_files"])
        self.assertEqual(res["healed_count"], 1)

        # 断言磁盘上生成了该缺失封面
        healed_path = os.path.join(self.covers_dir, missing_cover_fn)
        self.assertTrue(os.path.isfile(healed_path))
        img = Image.open(healed_path)
        self.assertEqual(img.format, "JPEG")

    def test_http_api_routes_integration(self):
        # 验证通过 FastAPI HTTP Client 请求
        res = self.client.get("/api/design/assets/default-cover.jpg")
        self.assertEqual(res.status_code, 200)
        self.assertIn("image/jpeg", res.headers.get("content-type", ""))

        # 验证请求不存在的封面时返回 200 并被自愈
        res_heal = self.client.get("/api/design/assets/covers/test_http_client_auto_heal_123.jpg")
        self.assertEqual(res_heal.status_code, 200)
        self.assertIn("image/jpeg", res_heal.headers.get("content-type", ""))

if __name__ == "__main__":
    unittest.main()
