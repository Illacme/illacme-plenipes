# -*- coding: utf-8 -*-
"""
🧪 Knowledge Card Deck API Routes Unit Tests
验证 /api/design/cards/generate 与 /api/design/cards/info 接口逻辑
"""

import os
import pytest
from fastapi.testclient import TestClient

from services.api.server import app
from core.runtime.engine_singleton import get_global_engine


@pytest.fixture
def api_client():
    return TestClient(app)


def test_card_deck_generate_endpoint_and_info(api_client, tmp_path):
    # 查找文库中已有的文章
    engine = get_global_engine()
    vault_root = getattr(engine, "vault_root", os.getcwd()) if engine else os.getcwd()

    # 在文库中准备一篇测试 Markdown 稿件
    test_rel_path = "Showcase/test_deck_article.md"
    test_file_path = os.path.join(vault_root, test_rel_path)
    os.makedirs(os.path.dirname(test_file_path), exist_ok=True)

    with open(test_file_path, "w", encoding="utf-8") as f:
        f.write("""---
title: "卡片工坊测试稿件"
author: "Antigravity"
category: "深度技术"
slug: "test-deck-article"
---

# 卡片工坊测试稿件

这是卡片工坊端到端测试文章。

## 01. 模块设计原则

- 遵循单一职责与 SOP-01 规范。
- 零依赖 Pillow 原生渲染。

> “代码即设计，设计即主权。”

## 02. 小红书轮播适配

针对 3:4 黄金比例深度定制。
""")

    try:
        # 1. 调用生成接口
        resp = api_client.post("/api/design/cards/generate", json={
            "rel_path": test_rel_path,
            "offset": 1,
            "max_cards": 5
        })

        assert resp.status_code == 200, f"Error: {resp.text}"
        data = resp.json()
        assert data["status"] == "ok"
        assert data["slug"] == "test-deck-article"
        assert data["total"] >= 3
        assert len(data["cards"]) == data["total"]
        assert "zip_url" in data

        # 2. 验证静态资源能正常通过 HTTP 访问 (200 OK)
        first_card_url = data["cards"][0]["url"]
        card_resp = api_client.get(first_card_url)
        assert card_resp.status_code == 200
        assert card_resp.headers["content-type"] in ("image/jpeg", "image/jpg")
        assert len(card_resp.content) > 1000

        # 3. 验证 ZIP 包能正常通过 HTTP 下载 (200 OK)
        zip_resp = api_client.get(data["zip_url"])
        assert zip_resp.status_code == 200
        assert zip_resp.headers["content-type"] == "application/zip"
        assert len(zip_resp.content) > 2000

        # 4. 调用 info 接口查询
        info_resp = api_client.get(f"/api/design/cards/info?rel_path={test_rel_path}")
        assert info_resp.status_code == 200
        info_data = info_resp.json()
        assert info_data["exists"] is True
        assert info_data["total"] == data["total"]
        assert len(info_data["cards"]) == data["total"]

    finally:
        # 清理测试文稿与生成的缓存
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
        deck_cache = os.path.join(vault_root, ".plenipes", "cache", "cards", "test-deck-article")
        if os.path.isdir(deck_cache):
            import shutil
            shutil.rmtree(deck_cache, ignore_errors=True)
