# -*- coding: utf-8 -*-
"""
🧪 Unit & Integration Tests: Vault Frontmatter Quick Patch & State Reflection
🛡️ [SOP-01] 物理行数严格保持在 300 行以内。
"""

import os
import tempfile
from core.utils.text import parse_frontmatter
from services.api.logic.content_ops_shards.vault_patch_ops import patch_frontmatter_logic


class MockEngine:
    def __init__(self, root_dir: str):
        self.vault_root = root_dir
        self.cache_dir = os.path.join(root_dir, ".plenipes", "cache")
        self.imprint_id = "default"
        self.meta = self

    class sqlite:
        @staticmethod
        def update_document_metadata(rel_path, updates):
            return True


def test_patch_frontmatter_physical_sync():
    """测试原子修改 Frontmatter 物理文件落盘与正文保全"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        doc_rel = "docs/sample_guide.md"
        doc_abs = os.path.join(tmp_dir, doc_rel)
        os.makedirs(os.path.dirname(doc_abs), exist_ok=True)

        initial_content = """---
title: 架构指南
slug: arch-guide
draft: false
---
# 核心架构

这是正文内容段落，不可被破坏。
"""
        with open(doc_abs, "w", encoding="utf-8") as f:
            f.write(initial_content)

        engine = MockEngine(tmp_dir)

        # 1. 执行 Patch 操作：关闭播客，标记为草稿，设为精选
        res = patch_frontmatter_logic(engine, {
            "rel_path": doc_rel,
            "patch": {
                "podcast": False,
                "draft": True,
                "featured": True
            }
        })

        assert res["success"] is True
        assert res["frontmatter"]["podcast"] is False
        assert res["frontmatter"]["draft"] is True
        assert res["frontmatter"]["featured"] is True
        assert res["frontmatter"]["title"] == "架构指南"
        assert res["frontmatter"]["slug"] == "arch-guide"

        # 2. 物理读取磁盘文件验证
        with open(doc_abs, "r", encoding="utf-8") as f:
            disk_content = f.read()

        meta, body, has_fm = parse_frontmatter(disk_content)
        assert has_fm is True
        assert meta["podcast"] is False
        assert meta["draft"] is True
        assert meta["featured"] is True
        assert meta["title"] == "架构指南"
        assert "这是正文内容段落，不可被破坏。" in body

        # 3. 字段删除测试 (传入 None)
        res_del = patch_frontmatter_logic(engine, {
            "rel_path": doc_rel,
            "patch": {
                "featured": None
            }
        })
        assert res_del["success"] is True
        assert "featured" not in res_del["frontmatter"]

        with open(doc_abs, "r", encoding="utf-8") as f:
            disk_content_del = f.read()
        meta_del, _, _ = parse_frontmatter(disk_content_del)
        assert "featured" not in meta_del


def test_api_patch_frontmatter_route():
    """测试 REST API /api/vault/patch-frontmatter 接口连通性"""
    from fastapi.testclient import TestClient
    from services.api.server import app

    client = TestClient(app)

    # 非法入参拦截
    resp_bad = client.post(
        "/api/vault/patch-frontmatter",
        json={"rel_path": ""},
        headers={"Authorization": "Bearer test-token"}
    )
    assert resp_bad.status_code == 200
    assert resp_bad.json()["success"] is False


def test_patch_draft_toggle_preserves_title_and_cover():
    """测试原稿草稿/发布状态切换时，标题绝不变成 Unknown 且封面完整保全"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        doc_rel = "Showcase/test-doc.md"
        doc_abs = os.path.join(tmp_dir, doc_rel)
        os.makedirs(os.path.dirname(doc_abs), exist_ok=True)

        initial = """---
title: 测试文章标题
slug: test-doc
cover: /api/design/assets/covers/cover_test123.jpg
draft: false
---
# 测试标题

正文内容。
"""
        with open(doc_abs, "w", encoding="utf-8") as f:
            f.write(initial)

        db_records = {}

        class SpyEngine:
            vault_root = tmp_dir
            cache_dir = os.path.join(tmp_dir, ".plenipes", "cache")
            imprint_id = "default"

            class meta:
                class sqlite:
                    @staticmethod
                    def update_document_metadata(rel_path, updates):
                        db_records.setdefault(rel_path, {}).update(updates)
                        return True

                    @staticmethod
                    def get_documents_count_filtered(query=None, folder=None):
                        return 1

                    @staticmethod
                    def list_documents_paginated(page=1, limit=20, query=None, folder=None):
                        rec = db_records.get(doc_rel, {})
                        return [{
                            "rel_path": doc_rel,
                            "title": rec.get("title", "测试文章标题"),
                            "cover": rec.get("cover", "/api/design/assets/covers/cover_test123.jpg"),
                            "draft": rec.get("draft", False),
                            "seo_data": {"title": "测试文章标题"}
                        }]

        # 1. 切换为草稿 (draft: true)
        res_draft = patch_frontmatter_logic(SpyEngine, {
            "rel_path": doc_rel,
            "patch": {"draft": True}
        })
        assert res_draft["success"] is True
        assert res_draft["frontmatter"]["draft"] is True
        assert res_draft["frontmatter"]["title"] == "测试文章标题"
        assert res_draft["frontmatter"]["cover"] == "/api/design/assets/covers/cover_test123.jpg"
        assert db_records[doc_rel]["cover"] == "/api/design/assets/covers/cover_test123.jpg"
        assert db_records[doc_rel]["title"] == "测试文章标题"

        # 2. 模拟检索列表
        from services.api.logic.content_ops_shards.vault_ops import search_vault_logic
        search_res = search_vault_logic(SpyEngine, q="test", page=1, limit=10)
        found = search_res["items"][0]
        assert found["title"] == "测试文章标题"
        assert found["title"] != "Unknown"
        assert found["cover"] == "/api/design/assets/covers/cover_test123.jpg"

        # 3. 再次切换为已发布 (draft: false)
        res_pub = patch_frontmatter_logic(SpyEngine, {
            "rel_path": doc_rel,
            "patch": {"draft": False}
        })
        assert res_pub["success"] is True
        assert res_pub["frontmatter"]["draft"] is False
        assert res_pub["frontmatter"]["title"] == "测试文章标题"
        assert res_pub["frontmatter"]["cover"] == "/api/design/assets/covers/cover_test123.jpg"
        assert db_records[doc_rel]["draft"] is False


