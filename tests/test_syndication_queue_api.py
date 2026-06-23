#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 [Test] 多渠道分发死信队列 RESTful API 单元测试
职责：全面覆盖 /api/governance/syndication/queue 及其 retry, delete 端点的接口行为与防御安全拦截。
"""

import sys
import os
from fastapi.testclient import TestClient

# 将项目根目录加入 python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.api.server import app

class MockSystemConfig:
    def __init__(self):
        self.api_token = None  # 初始无 token，免密测试

class MockConfig:
    def __init__(self):
        self.system = MockSystemConfig()
        self.syndication = {"MockTarget": {"enabled": True}}
        self.site_url = "https://example.com"

class MockMeta:
    def __init__(self):
        self.tasks = [
            {
                "id": 1,
                "rel_path": "doc1.md",
                "target_id": "MockTarget",
                "title": "Title 1",
                "slug": "title-1",
                "content": "Content",
                "metadata_json": "{}",
                "lang_code": "zh",
                "retry_count": 3,
                "max_retries": 3,
                "last_error": "Connection Timeout",
                "next_retry_time": 1000,
                "status": "FAILED"
            }
        ]

    def list_all_syndication_tasks(self):
        return self.tasks

    def retry_syndication_task(self, rel_path=None, target_id=None):
        if rel_path and target_id:
            for t in self.tasks:
                if t["rel_path"] == rel_path and t["target_id"] == target_id:
                    t["retry_count"] = 0
                    t["status"] = "PENDING"
                    t["next_retry_time"] = 0
                    t["last_error"] = None
        else:
            for t in self.tasks:
                if t["status"] == "FAILED":
                    t["retry_count"] = 0
                    t["status"] = "PENDING"
                    t["next_retry_time"] = 0
                    t["last_error"] = None

    def delete_syndication_task(self, rel_path=None, target_id=None):
        if rel_path and target_id:
            self.tasks = [t for t in self.tasks if not (t["rel_path"] == rel_path and t["target_id"] == target_id)]
        else:
            self.tasks = [t for t in self.tasks if t["status"] != "FAILED"]

class MockEngine:
    def __init__(self):
        self.config = MockConfig()
        self.meta = MockMeta()
        self.vault_root = "/tmp"

def test_syndication_queue_api():
    print("🧪 [Test] 启动多渠道分发队列 API 单元测试...")

    # 实例化 Mock 引擎并注入单例
    mock_engine = MockEngine()
    
    import core.runtime.engine_singleton as singleton
    original_engine = singleton.get_global_engine()
    singleton.set_global_engine(mock_engine)
    
    client = TestClient(app)
    
    try:
        # 1. 正常获取队列
        res = client.get("/api/governance/syndication/queue")
        assert res.status_code == 200, f"API 返回非 200: {res.status_code}"
        data = res.json()
        assert "tasks" in data
        assert len(data["tasks"]) == 1
        assert data["tasks"][0]["rel_path"] == "doc1.md"
        assert data["tasks"][0]["status"] == "FAILED"
        print("  ✅ [测试] 获取分发队列数据格式校验通过")

        # 2. 身份验证拦截测试
        mock_engine.config.system.api_token = "secure-synd-secret"
        res_forbidden = client.get("/api/governance/syndication/queue")
        assert res_forbidden.status_code == 403, "未授权请求未被成功拦截"

        # 带有正确 X-Token
        res_auth = client.get("/api/governance/syndication/queue", headers={"X-Token": "secure-synd-secret"})
        assert res_auth.status_code == 200, "合法 Token 被误判拦截"
        
        # 3. 测试特定单条任务重试
        res_retry = client.post(
            "/api/governance/syndication/queue/retry",
            json={"rel_path": "doc1.md", "target_id": "MockTarget"},
            headers={"X-Token": "secure-synd-secret"}
        )
        assert res_retry.status_code == 200
        assert res_retry.json() == {"success": True}
        
        # 检查是否变为了 PENDING 状态
        res_check = client.get("/api/governance/syndication/queue", headers={"X-Token": "secure-synd-secret"})
        tasks = res_check.json()["tasks"]
        assert tasks[0]["status"] == "PENDING"
        assert tasks[0]["retry_count"] == 0
        print("  ✅ [测试] 单条分发任务重试逻辑自愈通过")

        # 4. 测试一键重试所有 FAILED 任务
        # 我们先把状态手动改回 FAILED，并且把 target_id 换一下方便测试
        mock_engine.meta.tasks[0]["status"] = "FAILED"
        mock_engine.meta.tasks[0]["retry_count"] = 3
        
        res_retry_all = client.post(
            "/api/governance/syndication/queue/retry",
            json={},
            headers={"X-Token": "secure-synd-secret"}
        )
        assert res_retry_all.status_code == 200
        assert res_retry_all.json() == {"success": True}
        
        res_check_all = client.get("/api/governance/syndication/queue", headers={"X-Token": "secure-synd-secret"})
        tasks_all = res_check_all.json()["tasks"]
        assert tasks_all[0]["status"] == "PENDING"
        print("  ✅ [测试] 一键重试所有失败任务逻辑自愈通过")

        # 5. 测试删除特定任务
        res_delete = client.post(
            "/api/governance/syndication/queue/delete",
            json={"rel_path": "doc1.md", "target_id": "MockTarget"},
            headers={"X-Token": "secure-synd-secret"}
        )
        assert res_delete.status_code == 200
        assert res_delete.json() == {"success": True}

        res_check_del = client.get("/api/governance/syndication/queue", headers={"X-Token": "secure-synd-secret"})
        assert len(res_check_del.json()["tasks"]) == 0
        print("  ✅ [测试] 单条分发任务删除操作通过")

        # 6. 测试一键清空所有失败任务
        # 重新加入一个 FAILED 任务和一个 PENDING 任务
        mock_engine.meta.tasks = [
            {"rel_path": "failed.md", "target_id": "Target1", "status": "FAILED"},
            {"rel_path": "pending.md", "target_id": "Target2", "status": "PENDING"}
        ]
        
        res_clear = client.post(
            "/api/governance/syndication/queue/delete",
            json={},
            headers={"X-Token": "secure-synd-secret"}
        )
        assert res_clear.status_code == 200
        assert res_clear.json() == {"success": True}

        res_check_clear = client.get("/api/governance/syndication/queue", headers={"X-Token": "secure-synd-secret"})
        remaining_tasks = res_check_clear.json()["tasks"]
        assert len(remaining_tasks) == 1
        assert remaining_tasks[0]["rel_path"] == "pending.md"
        print("  ✅ [测试] 一键清空所有失败死信任务操作通过")

    finally:
        # 恢复单例
        singleton.set_global_engine(original_engine)

if __name__ == "__main__":
    test_syndication_queue_api()
