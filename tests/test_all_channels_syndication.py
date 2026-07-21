#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛡️ [V89.0] 全渠道联动与待同步社交资产检测逻辑单元测试
"""
import os
import sys
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath('.'))

def test_get_pending_syndication_logic():
    """验证获取待同步社交文章列表的过滤算法"""
    from services.api.logic.dispatch_ops_shards.pipeline_ops import get_pending_syndication_logic
    
    # 1. 模拟 engine, config, meta, sqlite
    engine = MagicMock()
    config = MagicMock()
    
    # 模拟启用的社交同步配置
    config.syndication = {
        "dev_to": {"enabled": True},
        "medium": {"enabled": False}  # 未启用
    }
    engine.config = config
    
    # 模拟主权账本中的文档列表
    meta = MagicMock()
    sqlite = MagicMock()
    
    # doc1: dev_to 已成功 (不应在 pending)
    # doc2: dev_to 失败 (应该在 pending)
    # doc3: dev_to 没同步过 (应该在 pending)
    all_docs = [
        {
            "rel_path": "docs/doc1.md",
            "title": "Document 1",
            "publish_status": {
                "dev_to": {"status": "success", "timestamp": 12345}
            }
        },
        {
            "rel_path": "docs/doc2.md",
            "title": "Document 2",
            "publish_status": {
                "dev_to": {"status": "failed", "timestamp": 12345, "error": "Auth Error"}
            }
        },
        {
            "rel_path": "docs/doc3.md",
            "title": "Document 3",
            "publish_status": {}
        }
    ]
    sqlite.get_all_documents.return_value = all_docs
    meta.sqlite = sqlite
    engine.meta = meta
    
    res = get_pending_syndication_logic(engine)
    assert res["count"] == 2
    paths = [d["rel_path"] for d in res["pending_docs"]]
    assert "docs/doc2.md" in paths
    assert "docs/doc3.md" in paths
    assert "docs/doc1.md" not in paths

@patch("os.path.exists")
def test_telemetry_ops_append_channels(mock_exists):
    """验证 telemetry_ops 在扫描时正确追加了激活的 Hosting 与 Syndication 卡片"""
    mock_exists.return_value = True
    
    from services.api.logic.dispatch_ops_shards.telemetry_ops import get_dispatch_status_logic
    
    engine = MagicMock()
    config = MagicMock()
    
    # 模拟 i18n
    config.i18n_settings.enabled = False
    config.i18n_settings.source.lang_code = "zh-Hans"
    config.i18n_settings.targets = []
    
    # 模拟启用的 Hosting 渠道 (github_pages) 
    config.publish_control.direct_upload = {
        "github_pages": {"enabled": True, "public_url": "https://host.com"},
        "cloudflare_pages": {"enabled": False}
    }
    
    # 模拟启用的 社交渠道
    config.syndication = {
        "dev_to": {"enabled": True}
    }
    
    engine.config = config
    
    # 模拟账本返回的数据
    meta = MagicMock()
    meta.get_doc_info.return_value = {
        "title": "Test Title",
        "slug": "test-slug",
        "publish_status": {
            "github_pages": {"status": "success", "timestamp": 112233},
            "dev_to": {"status": "failed", "timestamp": 445566, "error": "API Limit"}
        }
    }
    engine.meta = meta
    engine.vault_root = "/tmp"
    
    # 避开文件读取
    with patch("builtins.open", patch("builtins.open")):
        with patch("core.utils.extract_frontmatter", return_value=({}, "body")):
            res = get_dispatch_status_logic(engine, "docs/test.md")
            
            sync_matrix = res["sync_matrix"]
            # 应包含: 默认语种卡片 + 1个 Hosting 卡片 + 1个 Social 卡片
            assert len(sync_matrix) == 3
            
            hosting_card = next(c for c in sync_matrix if c["lang_code"] == "HOSTING")
            assert hosting_card["locale"] == "🌐 Github Pages (全站部署)"
            assert hosting_card["status"] == "success"
            
            social_card = next(c for c in sync_matrix if c["lang_code"] == "SOCIAL")
            assert social_card["locale"] == "📡 Dev To (社交同步)"
            assert social_card["status"] == "failed"
            assert social_card["reason"] == "API Limit"
