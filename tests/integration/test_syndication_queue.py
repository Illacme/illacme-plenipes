# -*- coding: utf-8 -*-
"""
🧪 [Test] 多渠道分发异步重试队列 (Syndication Retry Queue) 集成测试
"""
import os
import sys
import time
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from core.syndication.hub import ContentSyndicator
from core.archives.ledger import MetadataManager
from core.adapters.syndication.base import BaseSyndicator
from core.adapters.syndication.targets import TARGET_REGISTRY

# 1. 声明并注册 Mock 分发插件
class MockRetrySyndicator(BaseSyndicator):
    def __init__(self, cfg, sys_tuning):
        self.cfg = cfg
        self.sys_tuning = sys_tuning
        self.push_count = 0
        self.should_fail = False
        self.last_payload = None

    def push(self, payload):
        self.push_count += 1
        self.last_payload = payload
        if self.should_fail:
            raise RuntimeError("Mock network error")
        return {"status": "success"}

    def is_enabled(self, rel_path, lang_code):
        return True

    def format_payload(self, title, slug, content, metadata):
        return {"title": title, "slug": slug, "content": content}

# 动态载入注册中心
TARGET_REGISTRY["mock_retry"] = MockRetrySyndicator


class TestSyndicationRetryQueue(unittest.TestCase):
    def setUp(self):
        # 初始化测试专属临时 SQLite 数据库
        self.db_path = "tests/integration/temp_test_syndication.db"
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        self.ledger = MetadataManager(self.db_path)
        
        # 注册一个测试文档
        self.ledger.register_document("doc1.md", "Doc One", slug="doc-one", source_hash="hash123")

        # 配置分发渠道
        self.syndication_cfg = {
            "mock_retry": {
                "enabled": True,
                "platform": "mock_retry"
            }
        }
        self.syndicator = ContentSyndicator(
            syndication_cfg=self.syndication_cfg,
            site_url="https://example.com",
            sys_tuning_cfg=None,
            meta=self.ledger
        )

    def tearDown(self):
        # 保证关闭所有 SQLite 连接并清理
        if hasattr(self.ledger, "sqlite") and hasattr(self.ledger.sqlite, "_local"):
            if hasattr(self.ledger.sqlite._local, "conn"):
                self.ledger.sqlite._local.conn.close()
                del self.ledger.sqlite._local.conn
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        # 清理 WAL 产生的临时文件
        for ext in ["-shm", "-wal"]:
            if os.path.exists(self.db_path + ext):
                os.remove(self.db_path + ext)

    def test_syndication_retry_lifecycle(self):
        # 获取我们实例化的插件
        plugin = self.syndicator.plugins[0]
        self.assertIsInstance(plugin, MockRetrySyndicator)

        # 🚀 场景 1: 分发失败，期望成功排入 SQLite 持久化队列
        plugin.should_fail = True
        
        # 为了同步验证，这里我们手动直接调用，不走 executor 异步
        self.syndicator._dispatch_to_plugin(
            plugin=plugin,
            title="Doc One Title",
            slug="doc-one",
            content="Hello world",
            metadata={"source_hash": "hash123"},
            rel_path="doc1.md",
            lang_code="zh",
            is_dry_run=False
        )

        # 检查是否成功排入队列
        tasks = self.ledger.get_pending_syndication_tasks()
        self.assertEqual(len(tasks), 1)
        
        task = tasks[0]
        self.assertEqual(task["rel_path"], "doc1.md")
        self.assertEqual(task["target_id"], "MockRetrySyndicator")
        self.assertEqual(task["retry_count"], 0)
        self.assertEqual(task["status"], "PENDING")
        self.assertEqual(task["title"], "Doc One Title")
        self.assertEqual(task["content"], "Hello world")
        self.assertEqual(task["metadata"]["source_hash"], "hash123")

        # 🚀 场景 2: 触发重试且依然失败，期望 retry_count + 1 并且退避推后
        plugin.should_fail = True
        
        # 手动调度单任务重试，进行断言
        self.syndicator._dispatch_retry_task(plugin, task)
        
        # 检查状态：由于 backoff_seconds 使得下一次重试时间变大，
        # 我们用 get_pending_syndication_tasks 会因为时间窗口未到而过滤，所以我们要直接查数据库
        conn = self.ledger.sqlite._get_conn()
        row = conn.execute("SELECT * FROM syndication_queue WHERE rel_path = ? AND target_id = ?", ("doc1.md", "MockRetrySyndicator")).fetchone()
        self.assertIsNotNone(row)
        task_data = dict(row)
        self.assertEqual(task_data["retry_count"], 1)
        self.assertEqual(task_data["status"], "PENDING")
        self.assertTrue(task_data["next_retry_time"] > time.time())
        self.assertEqual(task_data["last_error"], "Mock network error")

        # 🚀 场景 3: 渠道自愈，触发重试并期望分发成功，任务移出队列
        plugin.should_fail = False
        
        # 手动将 next_retry_time 设为过去（0），以便进入重试窗口
        conn.execute("UPDATE syndication_queue SET next_retry_time = 0 WHERE rel_path = ?", ("doc1.md",))
        conn.commit()
        
        # 重新扫描重试队列并执行
        self.syndicator.process_pending_retries()
        
        # 等待异步重试任务在 global_executor 中执行完成
        for _ in range(40):
            conn = self.ledger.sqlite._get_conn()
            row = conn.execute("SELECT COUNT(*) FROM syndication_queue").fetchone()
            if row[0] == 0:
                break
            time.sleep(0.05)
        
        # 检查队列，应该已经被清空（物理删除）
        tasks_after = self.ledger.get_pending_syndication_tasks()
        self.assertEqual(len(tasks_after), 0)
        
        # 验证账本中的发布状态，应该是 DONE
        status = self.ledger.get_syndication_status("doc1.md", "MockRetrySyndicator")
        self.assertEqual(status["status"], "DONE")
        self.assertEqual(status["hash"], "hash123")

    def test_syndication_retry_exhausted(self):
        plugin = self.syndicator.plugins[0]
        plugin.should_fail = True

        # 1. 首次失败进队列
        self.syndicator._dispatch_to_plugin(
            plugin=plugin, title="Doc One", slug="doc-one", content="Hello",
            metadata={"source_hash": "hash123"}, rel_path="doc1.md", lang_code="zh", is_dry_run=False
        )

        # 2. 连续重试至上限 (max_retries 默认为 3)
        # 重试 1
        tasks = self.ledger.get_pending_syndication_tasks()
        self.syndicator._dispatch_retry_task(plugin, tasks[0])
        
        # 重试 2
        conn = self.ledger.sqlite._get_conn()
        conn.execute("UPDATE syndication_queue SET next_retry_time = 0")
        conn.commit()
        tasks = self.ledger.get_pending_syndication_tasks()
        self.syndicator._dispatch_retry_task(plugin, tasks[0])
        
        # 重试 3 （达到上限）
        conn.execute("UPDATE syndication_queue SET next_retry_time = 0")
        conn.commit()
        tasks = self.ledger.get_pending_syndication_tasks()
        # 由于 retry_count = 2，下一次重试 retry_count + 1 = 3，达到上限 max_retries = 3
        self.syndicator._dispatch_retry_task(plugin, tasks[0])

        # 3. 验证队列中的状态变更为 FAILED，不再是 PENDING，因此不会被 process_pending_retries 扫描到
        row = conn.execute("SELECT * FROM syndication_queue WHERE rel_path = ?", ("doc1.md",)).fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(dict(row)["status"], "FAILED")
        
        # 且 get_pending_syndication_tasks 应不再返回此任务
        tasks_final = self.ledger.get_pending_syndication_tasks()
        self.assertEqual(len(tasks_final), 0)


if __name__ == "__main__":
    unittest.main()
