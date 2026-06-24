#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_sentinel_active.py
🛡️ [V88.0] Guardian Sentinel 健康审计与自愈测试
验证算力熔断 (TCG)、DNA 溯源标签注入与 Markdown 语义死链自愈。
"""

import os
import json
import pytest
from unittest.mock import MagicMock, patch, mock_open
from core.governance.sentinel import SentinelManager


class TestSentinelActive:
    """健康自愈哨兵测试类"""

    def test_sentinel_init_without_engine(self):
        """测试在无引擎上下文下的基本初始化与默认路径"""
        config = MagicMock()
        sentinel = SentinelManager(config, engine=None)
        assert sentinel.health_log_path == os.path.join(".plenipes", "sentinel_health.json")
        assert sentinel.current_iter_id == "UNKNOWN"

    def test_sentinel_init_with_engine(self):
        """测试在有引擎上下文下的路径解析与迭代状态提取"""
        config = MagicMock()
        config.get_health_report_path.return_value = "custom_report.json"
        config.get_history_dir.return_value = "history_dir"

        engine = MagicMock()
        engine.config = config
        engine._resolve_path = lambda p: f"/resolved/{p}"

        # 模拟历史迭代目录读取
        with patch("os.path.exists", return_value=True), \
             patch("os.listdir", return_value=["AEL-2026-06-01", "AEL-2026-06-02"]), \
             patch("os.path.isdir", return_value=True), \
             patch.object(SentinelManager, "_start_config_watcher"):
            sentinel = SentinelManager(config, engine=engine)
            assert sentinel.health_log_path == "/resolved/custom_report.json"
            assert sentinel.current_iter_id == "AEL-2026-06-02"

    def test_stop_signal(self):
        """测试 stop 方法能够正确设置停止事件标志"""
        config = MagicMock()
        sentinel = SentinelManager(config, engine=None)
        assert not sentinel._stop_event.is_set()
        sentinel.stop()
        assert sentinel._stop_event.is_set()

    def test_token_tracking_and_tcg_circuit_break(self):
        """测试算力追踪在耗尽时触发 TCG 熔断机制"""
        config = MagicMock()
        sentinel = SentinelManager(config, engine=None)
        sentinel.status_matrix["token_budget"] = 1000

        # 在预算范围内正常增加
        sentinel.track_token_usage(800)
        assert sentinel.status_matrix["token_usage"] == 800

        # 超出预算触发熔断
        with pytest.raises(RuntimeError, match="TCG_BUDGET_EXCEEDED"):
            sentinel.track_token_usage(300)

    def test_dna_trace_label_injection(self):
        """测试溯源 DNA 标签的幂等注入行为"""
        config = MagicMock()
        sentinel = SentinelManager(config, engine=None)
        sentinel.current_iter_id = "2026-06"

        code = "print('hello')"
        injected = sentinel.inject_trace_label(code)
        assert "🛡️ [AEL-2026-06]" in injected

        # 重复注入应该保持幂等
        injected_again = sentinel.inject_trace_label(injected)
        assert injected_again.count("🛡️ [AEL-2026-06]") == 1

    @patch("core.governance.sentinel.subprocess.run")
    def test_check_and_fix_lint(self, mock_run):
        """测试 Ruff Lint 检查与自愈逻辑的分支覆盖"""
        config = MagicMock()
        sentinel = SentinelManager(config, engine=None)

        # 模拟 ruff 检查成功
        mock_run.return_value = MagicMock(return_code=0)
        res = sentinel._check_and_fix_lint(auto_fix=True)
        assert res is False  # subprocess.run code 为 0 时为 True，但是 Mock 返回 code 属性而不是 returncode。
        # 让我们把 mock 改得更精确：returncode = 0
        mock_run.return_value.returncode = 0
        res = sentinel._check_and_fix_lint(auto_fix=True)
        assert res is True

        # 模拟 ruff 校验失败
        mock_run.return_value.returncode = 1
        res = sentinel._check_and_fix_lint(auto_fix=False)
        assert res is False

    @patch("core.governance.sentinel.os.walk")
    @patch("core.governance.sentinel.os.path.exists")
    def test_heal_markdown_links(self, mock_exists, mock_walk):
        """测试死链自愈的物理文件扫描与重定向自愈算法"""
        config = MagicMock()
        config.vault_root = "/vault"
        sentinel = SentinelManager(config, engine=None)
        sentinel.current_iter_id = "test-iter"

        mock_exists.return_value = True

        # 模拟文件夹结构：
        # /vault 下有两个文件：file_a.md 和 file_b.md
        # file_a.md 内容中包含了一个指向 [[file_b_moved]] 的 wiki 链接
        # 且 file_b.md 文件名刚好能用来进行别名重定位
        mock_walk.return_value = [
            ("/vault", [], ["file_a.md", "file_b.md"])
        ]

        file_contents = {
            "/vault/file_a.md": "Link to [[file_b]] and broken [[subpath/file_b]]",
            "/vault/file_b.md": "Content of B"
        }

        def mock_open_fn(path, mode="r", *args, **kwargs):
            if "w" in mode:
                # 记录写回的内容
                m = mock_open()()
                m.write = lambda data: file_contents.update({path: data})
                return m
            content = file_contents.get(path, "")
            return mock_open(read_data=content)()

        with patch("core.governance.sentinel.open", mock_open_fn, create=True):
            heal_count = sentinel._heal_markdown_links()
            # 应当发现 subpath/file_b 可以重定向至 file_b.md (对应 file_index 里的文件名)
            assert heal_count == 1
            # file_a.md 的内容应被修复并注入了 DNA 标签
            assert "broken [[file_b]]" in file_contents["/vault/file_a.md"]
            assert "🛡️ [AEL-test-iter]" in file_contents["/vault/file_a.md"]
