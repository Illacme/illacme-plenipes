#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 [Test] 物理原稿安全新建 RESTful API 单元测试
职责：全面覆盖 /ledger/document/create 端点的创建、重名校验、与路径穿越拦截逻辑。
"""
import sys
import os
import tempfile
import shutil
import pytest
from fastapi.testclient import TestClient

# 将项目根目录加入 python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.api.server import app
from core.runtime.engine_singleton import get_global_engine

# 构造 Mock 引擎和元数据管理器
class MockSystemConfig:
    def __init__(self):
        self.api_token = None # 绕过 token 校验以便测试

class MockConfig:
    def __init__(self):
        self.system = MockSystemConfig()

class MockSQLiteBackend:
    def __init__(self):
        self.registry = {}

    def get_document(self, rel_path):
        return self.registry.get(rel_path)

    def upsert_document(self, rel_path, data):
        self.registry[rel_path] = data

class MockMetadataManager:
    def __init__(self):
        self.sqlite = MockSQLiteBackend()
        self.registry = {}

    def register_document(self, rel_path, title, **kwargs):
        self.registry[rel_path] = {
            "title": title,
            "slug": kwargs.get("slug"),
            **kwargs
        }

class MockEngine:
    def __init__(self, vault_root):
        self.vault_root = vault_root
        self.meta = MockMetadataManager()
        self.config = MockConfig()

def test_document_creation_flow():
    print("🧪 [Test] 启动原稿物理新建及安全防御单元测试...")
    
    with tempfile.TemporaryDirectory() as temp_vault:
        # 1. 实例化 Mock 引擎并注入单例
        mock_engine = MockEngine(temp_vault)
        
        # 物理注入到全局单例（用于 api server 的 get_global_engine）
        import core.runtime.engine_singleton as singleton
        original_engine = singleton.get_global_engine()
        singleton.set_global_engine(mock_engine)
        
        client = TestClient(app)
        
        try:
            # 2. 正常场景：在子目录下创建原稿
            payload = {
                "doc_id": "blog/fresh-post",
                "title": "我的新鲜创作"
            }
            res = client.post("/ledger/document/create", json=payload)
            assert res.status_code == 200, "API 状态响应非 200"
            data = res.json()
            assert data.get("success") is True, f"创建失败: {data.get('error')}"
            assert data.get("doc_id") == "blog/fresh-post.md", "物理文件名后缀未正确补足为 .md"
            
            # 验证物理文件真的在临时文库中生成
            physical_file = os.path.join(temp_vault, "blog/fresh-post.md")
            assert os.path.exists(physical_file), "物理原稿文件未在磁盘中创建"
            
            with open(physical_file, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "我的新鲜创作" in content, "初始标题未被缝合写入文件"
                assert "slug: fresh-post" in content, "默认 slug 未被正确注入 YAML"
                
            # 验证 SQLite 索引是否完成入库注册
            registered_data = mock_engine.meta.registry.get("blog/fresh-post.md")
            assert registered_data is not None, "元数据索引未同步入库"
            assert registered_data["title"] == "我的新鲜创作", "注册的标题不符"
            
            print("  ✅ [测试] 正常新建物理流程与 Frontmatter 自动缝合完美通过！")
            
            # 3. 冲突场景：重名拦截
            res_conflict = client.post("/ledger/document/create", json=payload)
            assert res_conflict.status_code == 200
            data_conflict = res_conflict.json()
            assert data_conflict.get("success") is not True, "未能阻止重复同名文件的创建"
            assert "已存在" in data_conflict.get("error"), f"非预期的重名拦截提示: {data_conflict.get('error')}"
            print("  ✅ [测试] 物理重名防覆盖校验顺利通过！")
            
            # 4. 安全场景：路径穿越恶意阻断 (L3 级防御)
            payload_bypass = {
                "doc_id": "../../../etc/passwd",
                "title": "穿越测试"
            }
            res_bypass = client.post("/ledger/document/create", json=payload_bypass)
            assert res_bypass.status_code == 200
            data_bypass = res_bypass.json()
            assert data_bypass.get("success") is not True, "未能有效防御路径穿越穿越漏洞"
            assert "非法的物理路径穿越" in data_bypass.get("error"), f"非预期的安全拦截报错: {data_bypass.get('error')}"
            
            passwd_file_in_vault = os.path.join(temp_vault, "../../../etc/passwd.md")
            assert not os.path.exists(passwd_file_in_vault), "穿越文件违规被物理写入"
            print("  ✅ [测试] L3 级防路径穿越（Directory Traversal）安全拦截高分通过！")
            
        finally:
            # 恢复单例原状，防止干扰其他用例
            singleton.set_global_engine(original_engine)

if __name__ == "__main__":
    test_document_creation_flow()
