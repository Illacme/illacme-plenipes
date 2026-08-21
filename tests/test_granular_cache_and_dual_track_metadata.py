#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for Granular Cache Governance & Dual-Track Metadata File Persistence.
"""

import os
import shutil
import tempfile
import pytest
from core.archives.metadata_file_store import MetadataFileStore
from core.archives.ledger import MetadataManager

class TestGranularCacheAndDualTrackMetadata:

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        self.test_dir = tempfile.mkdtemp(prefix="illacme_cache_test_")
        self.db_path = os.path.join(self.test_dir, "test_ledger.db")
        self.meta_dir = os.path.join(self.test_dir, "metadata")
        yield
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_metadata_file_store_lifecycle(self):
        """测试 MetadataFileStore 独立文件的生命周期操作"""
        store = MetadataFileStore(self.meta_dir)
        doc_path = "docs/guides/installation.md"
        data = {
            "title": "安装指南",
            "slug": "install-guide",
            "source_hash": "hash_12345",
            "seo_data": {"description": "这是安装指南", "keywords": ["install", "guide"]},
            "translations": {"en": {"status": "DONE", "title": "Installation Guide"}}
        }

        # 1. 存盘
        assert store.save_document_metadata(doc_path, data) is True
        
        # 2. 读取
        loaded = store.get_document_metadata(doc_path)
        assert loaded is not None
        assert loaded["rel_path"] == doc_path
        assert loaded["slug"] == "install-guide"
        assert loaded["seo_data"]["description"] == "这是安装指南"

        # 3. 统计
        count, size_bytes = store.count_and_size()
        assert count == 1
        assert size_bytes > 0

        # 4. 全量扫描
        all_docs = store.scan_all_metadata()
        assert doc_path in all_docs
        assert all_docs[doc_path]["title"] == "安装指南"

        # 5. 删除
        assert store.delete_document_metadata(doc_path) is True
        assert store.get_document_metadata(doc_path) is None

    def test_metadata_manager_dual_track_and_rebuild(self):
        """测试 MetadataManager 的双轨持久化与 SQLite 账本丢失自愈重建"""
        meta_mgr = MetadataManager(self.db_path)
        doc1 = "articles/architecture.md"
        doc2 = "docs/api_reference.md"

        meta_mgr.register_document(
            doc1, "系统架构设计",
            slug="system-architecture",
            source_hash="src_hash_1",
            shadow_hash="shadow_hash_1",
            seo_data={"description": "核心架构解析"},
            translations={"en": {"status": "DONE"}}
        )

        meta_mgr.register_document(
            doc2, "API 接口参考",
            slug="api-ref",
            source_hash="src_hash_2",
            shadow_hash="shadow_hash_2",
            seo_data={"description": "全量 API 列表"}
        )

        # 验证 SQLite 写入
        assert meta_mgr.sqlite.get_total_documents_count() == 2
        
        # 验证物理文件写入
        assert meta_mgr.file_store.get_document_metadata(doc1) is not None
        assert meta_mgr.file_store.get_document_metadata(doc2) is not None

        # 模拟 SQLite 数据库被清空（但不清空物理文件）
        meta_mgr.sqlite.clear_all_documents()
        assert meta_mgr.sqlite.get_total_documents_count() == 0

        # 执行自愈重建
        restored_count = meta_mgr.rebuild_from_file_cache()
        assert restored_count == 2
        assert meta_mgr.sqlite.get_total_documents_count() == 2
        
        restored_doc = meta_mgr.get_doc_info(doc1)
        assert restored_doc["slug"] == "system-architecture"
        assert restored_doc["source_hash"] == "src_hash_1"
        assert restored_doc["seo_data"]["description"] == "核心架构解析"

    def test_clear_fingerprints_only(self):
        """测试仅重置指纹功能（0 LLM 算力消耗重编译）"""
        meta_mgr = MetadataManager(self.db_path)
        doc = "articles/demo.md"
        meta_mgr.register_document(
            doc, "演示文档",
            slug="demo-article",
            source_hash="demo_source_hash_999",
            shadow_hash="demo_shadow_hash_999",
            seo_data={"description": "演示 SEO 摘要"}
        )

        # 执行仅清空指纹
        meta_mgr.clear_fingerprints_only()

        # 检查：source_hash 与 shadow_hash 应被置空
        info = meta_mgr.get_doc_info(doc)
        assert info["source_hash"] is None
        assert info["shadow_hash"] is None

        # 检查：slug 与 seo_data 依然完好保留
        assert info["slug"] == "demo-article"
        assert info["seo_data"]["description"] == "演示 SEO 摘要"
        assert info["title"] == "演示文档"

        # 检查物理文件快照依然存在
        file_meta = meta_mgr.file_store.get_document_metadata(doc)
        assert file_meta is not None
        assert file_meta["slug"] == "demo-article"

    def test_clear_ai_metadata(self):
        """测试仅清空 AI 生成的 Slug 与 SEO 元数据"""
        meta_mgr = MetadataManager(self.db_path)
        doc = "articles/demo.md"
        meta_mgr.register_document(
            doc, "演示文档",
            slug="demo-article",
            source_hash="demo_source_hash_999",
            seo_data={"description": "演示 SEO 摘要"}
        )

        # 清空 AI 元数据
        meta_mgr.clear_ai_metadata(mode="all")

        info = meta_mgr.get_doc_info(doc)
        assert info.get("slug") is None
        assert "seo_data" not in info or not info.get("seo_data")
        # 指纹依然保留
        assert info.get("source_hash") == "demo_source_hash_999"
