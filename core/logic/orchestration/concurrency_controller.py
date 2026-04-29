#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Adaptive Concurrency Controller
模块职责：算力自动驾驶仪。
根据任务执行的成功率、延迟以及 API 限制反馈（429），动态调整 OrchestratedExecutor 的并发规模。
🚀 [V16.1]：自适应流量削峰与动态算力扩缩容。
"""

import time
import threading
import collections
from core.utils.tracing import tlog
from core.logic.orchestration.task_orchestrator import global_executor

class ConcurrencyController:
    """🚀 [V16.1] 自适应并发控制器"""
    def __init__(self, min_workers: int = 2, max_workers: int = 32):
        self.min_workers = min_workers
        self.max_workers = max_workers
        self.current_workers = global_executor.max_workers

        # 统计窗口 (记录最近 50 次任务的耗时与状态)
        self.window_size = 50
        self.history = collections.deque(maxlen=self.window_size)
        self.lock = threading.Lock()

        # 惩罚计数（针对 429 错误）
        self.penalty_points = 0
        self.last_adjustment_time = time.time()
        self.adjustment_cooldown = 5.0 # 每 5 秒最多调整一次

    def report_result(self, duration: float, success: bool, error_code: int = 0):
        """上报任务执行结果"""
        with self.lock:
            self.history.append({
                "duration": duration,
                "success": success,
                "error_code": error_code,
                "timestamp": time.time()
            })

            # 如果出现 429 (Too Many Requests)，立即增加惩罚分
            if error_code == 429:
                self.penalty_points += 10
                tlog.warning("🚨 [控制器] 检测到 API 频控限制 (429)，算力红线报警！")

            # 触发周期性评估
            if len(self.history) >= 5 and (time.time() - self.last_adjustment_time > self.adjustment_cooldown):
                self._evaluate_and_adjust()

    def _evaluate_and_adjust(self):
        """核心评估算法：根据窗口数据决定扩缩容"""
        success_rate = sum(1 for x in self.history if x['success']) / len(self.history)
        avg_duration = sum(x['duration'] for x in self.history) / len(self.history)

        target_workers = self.current_workers

        # 1. 极其严格的成功率红线 (成功率低于 90% 必须缩容)
        if success_rate < 0.90 or self.penalty_points > 0:
            target_workers = max(self.min_workers, int(self.current_workers * 0.5))
            self.penalty_points = max(0, self.penalty_points - 2) # 逐步消化惩罚分
            tlog.debug(f"📉 [控制器] 性能恶化 (成功率: {success_rate:.1%})，执行紧急缩容")

        # 2. 延迟探测与扩容 (成功率极高且延迟较低时，尝试缓慢扩容)
        elif success_rate > 0.98:
            if avg_duration < 1.0: # 如果平均任务耗时小于 1s
                target_workers = min(self.max_workers, self.current_workers + 2)
            elif avg_duration < 3.0:
                target_workers = min(self.max_workers, self.current_workers + 1)

            if target_workers > self.current_workers:
                tlog.debug(f"📈 [控制器] 运行平稳 (平均耗时: {avg_duration:.2f}s)，尝试平滑扩容")

        # 3. 执行调整
        if target_workers != self.current_workers:
            self.current_workers = target_workers
            global_executor.update_concurrency(target_workers)
            self.last_adjustment_time = time.time()

# 🚀 全局共享控制器
concurrency_controller = ConcurrencyController()
