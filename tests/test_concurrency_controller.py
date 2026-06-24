#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_concurrency_controller.py
🛡️ [V88.0] 自适应并发控制器测试
验证任务结果上报、429 惩罚分累加、以及动态扩缩容评估算法。
"""

import time
import pytest
from unittest.mock import MagicMock, patch
from core.logic.orchestration.concurrency_controller import ConcurrencyController


class TestConcurrencyController:
    """自适应并发控制器测试类"""

    @patch("core.logic.orchestration.concurrency_controller.global_executor")
    def test_init_and_properties(self, mock_executor):
        """测试并发控制器的初始状态与属性对正"""
        mock_executor.max_workers = 8
        controller = ConcurrencyController(min_workers=2, max_workers=16)

        assert controller.min_workers == 2
        assert controller.max_workers == 16
        assert controller.current_workers == 8
        assert controller.penalty_points == 0
        assert len(controller.history) == 0

    @patch("core.logic.orchestration.concurrency_controller.global_executor")
    def test_report_result_429_penalty(self, mock_executor):
        """测试检测到 429 (Too Many Requests) 时惩罚分的即时累加与警告"""
        mock_executor.max_workers = 8
        controller = ConcurrencyController(min_workers=2, max_workers=16)

        controller.report_result(duration=0.5, success=False, error_code=429)
        assert controller.penalty_points == 10

    @patch("core.logic.orchestration.concurrency_controller.global_executor")
    def test_evaluate_and_adjust_scale_down(self, mock_executor):
        """测试当成功率低于 90% 或惩罚分大于 0 时，触发半数紧急缩容"""
        mock_executor.max_workers = 10
        controller = ConcurrencyController(min_workers=2, max_workers=20)
        # 强制设置冷却时间已过
        controller.last_adjustment_time = time.time() - 10.0

        # 1. 模拟低成功率场景 (4 失败, 1 成功 -> 20% 成功率)
        for _ in range(4):
            controller.report_result(duration=0.5, success=False)
        # 第 5 次上报触发评估
        controller.report_result(duration=0.5, success=True)

        # 初始 current_workers = 10，半数缩容后应为 5
        assert controller.current_workers == 5
        mock_executor.update_concurrency.assert_called_with(5)

        # 2. 模拟 429 惩罚导致的缩容，且惩罚分逐步递减消化
        mock_executor.reset_mock()
        controller.penalty_points = 10
        controller.current_workers = 6
        controller.history.clear()
        controller.last_adjustment_time = time.time() - 10.0

        # 注入 5 个成功案例 (成功率 100%，但有 penalty_points)
        for _ in range(4):
            controller.history.append({"duration": 0.2, "success": True, "error_code": 0, "timestamp": time.time()})
        controller.report_result(duration=0.2, success=True)

        assert controller.current_workers == 3  # 6 * 0.5 = 3
        # 惩罚分被消化 2 分：10 - 2 = 8
        assert controller.penalty_points == 8
        mock_executor.update_concurrency.assert_called_with(3)

    @patch("core.logic.orchestration.concurrency_controller.global_executor")
    def test_evaluate_and_adjust_scale_up_fast(self, mock_executor):
        """测试在低延迟、高成功率场景下触发平滑双并发扩容"""
        mock_executor.max_workers = 4
        controller = ConcurrencyController(min_workers=2, max_workers=10)
        controller.last_adjustment_time = time.time() - 10.0

        # 注入 5 个高成功率且耗时极短 (avg < 1s) 的案例
        for _ in range(4):
            controller.history.append({"duration": 0.5, "success": True, "error_code": 0, "timestamp": time.time()})
        controller.report_result(duration=0.5, success=True)

        # 应该扩容 2 个 workers：4 + 2 = 6
        assert controller.current_workers == 6
        mock_executor.update_concurrency.assert_called_with(6)

    @patch("core.logic.orchestration.concurrency_controller.global_executor")
    def test_evaluate_and_adjust_scale_up_slow(self, mock_executor):
        """测试在中等延迟、高成功率场景下触发单步平滑扩容"""
        mock_executor.max_workers = 4
        controller = ConcurrencyController(min_workers=2, max_workers=10)
        controller.last_adjustment_time = time.time() - 10.0

        # 注入 5 个高成功率且耗时在 1s 至 3s 之间 (avg = 2s) 的案例
        for _ in range(4):
            controller.history.append({"duration": 2.0, "success": True, "error_code": 0, "timestamp": time.time()})
        controller.report_result(duration=2.0, success=True)

        # 应该慢速扩容 1 个 worker：4 + 1 = 5
        assert controller.current_workers == 5
        mock_executor.update_concurrency.assert_called_with(5)
