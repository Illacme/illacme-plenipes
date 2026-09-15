# -*- coding: utf-8 -*-
"""
🛡️ [V1.0] 媒体资产分页与切片查询自动化测试 (Design Assets Pagination Test)
职责：验证 /api/design/assets 分页参数、total/total_pages 计算、offset 切片及 strategy 过滤。
🛡️ [SOP-01] 物理行数严格保持在 300 行以内。
"""

import os
import sqlite3
import tempfile
from unittest.mock import patch, MagicMock
import pytest
from fastapi.testclient import TestClient

from core.api.server import app
from core.runtime.engine_singleton import get_global_engine


@pytest.fixture
def mock_pagination_env():
    """构造含 25 条资产记录的测试 SQLite 环境"""
    with tempfile.TemporaryDirectory() as tmpdir:
        vault_dir = os.path.join(tmpdir, "vault")
        os.makedirs(vault_dir, exist_ok=True)

        db_path = os.path.join(tmpdir, "meta.db")
        conn = sqlite3.connect(db_path, check_same_thread=False)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE visual_assets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rel_path TEXT,
                asset_type TEXT,
                strategy TEXT,
                source_url TEXT,
                cdn_url TEXT,
                media_id TEXT,
                prompt TEXT,
                created_at TEXT
            )
        """)

        # 插入 25 条记录，其中 15 条为 ai_openai，10 条为 ai_gemini
        for i in range(1, 26):
            strat = "ai_openai" if i <= 15 else "ai_gemini"
            cur.execute(
                "INSERT INTO visual_assets (rel_path, asset_type, strategy, source_url, prompt, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (f"covers/img_{i}.jpg", "cover", strat, f"/api/design/assets/covers/img_{i}.jpg", f"Prompt {i}", f"2026-09-15 12:{i:02d}:00")
            )
        conn.commit()

        mock_sqlite = MagicMock()
        mock_sqlite.get_connection.return_value = conn

        orig_engine = get_global_engine()
        engine = MagicMock()
        engine.vault_root = vault_dir
        engine.meta = MagicMock()
        engine.meta.sqlite = mock_sqlite
        engine.config = MagicMock()
        engine.config.system = MagicMock()
        engine.config.system.api_token = None

        with patch("core.runtime.engine_singleton.get_global_engine", return_value=engine), \
             patch("services.api.routes.design_shards.design_assets_routes.get_global_engine", return_value=engine):
            yield


def test_design_assets_pagination_defaults(mock_pagination_env):
    """验证默认分页参数与总量计算"""
    client = TestClient(app)
    res = client.get("/api/design/assets?page=1&limit=10")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["total"] == 25
    assert data["page"] == 1
    assert data["limit"] == 10
    assert data["total_pages"] == 3
    assert len(data["assets"]) == 10
    # 倒序排列：第 1 条应为 id 25
    assert data["assets"][0]["id"] == 25


def test_design_assets_pagination_page_2_and_3(mock_pagination_env):
    """验证第二页和第三页（尾页）切片"""
    client = TestClient(app)
    # 第 2 页：应返回 10 条
    res2 = client.get("/api/design/assets?page=2&limit=10")
    data2 = res2.json()
    assert len(data2["assets"]) == 10
    assert data2["page"] == 2

    # 第 3 页（尾页）：剩余 5 条
    res3 = client.get("/api/design/assets?page=3&limit=10")
    data3 = res3.json()
    assert len(data3["assets"]) == 5
    assert data3["page"] == 3
    assert data3["assets"][-1]["id"] == 1


def test_design_assets_pagination_with_provider_filter(mock_pagination_env):
    """验证结合 provider 过滤条件的分页与总量统计"""
    client = TestClient(app)
    # 过滤 gemini (共 10 条)
    res = client.get("/api/design/assets?provider=gemini&page=1&limit=6")
    data = res.json()
    assert data["success"] is True
    assert data["total"] == 10
    assert data["total_pages"] == 2
    assert len(data["assets"]) == 6
    for a in data["assets"]:
        assert a["strategy"] == "ai_gemini"
