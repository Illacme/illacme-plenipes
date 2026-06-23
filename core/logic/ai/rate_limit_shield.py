# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - AI Rate Limit Shield
职责：提供基于滑动窗口的自适应限流器，对大模型翻译网关的并发、QPS 与 TPM 进行多线程安全的主动保护与反馈减速自愈。
"""
import time
import collections
import threading
from typing import List, Dict, Any, Tuple, Optional
from core.utils.tracing import tlog


class RateLimitShield:
    """🛡️ [P4] 算力网关自适应滑动窗口限流盾
    通过滑动窗口主动检测和阻断超限请求，支持基于 AIMD 反馈的 429 自适应减速自愈。
    """
    def __init__(self, node_name: str, limits: Any, sleep_func: Optional[Any] = None):
        self.node_name: str = node_name
        self.limits: Any = limits  # limits 应包含 rate_limit_qps, max_tokens_per_min 等属性
        self.lock: threading.Lock = threading.Lock()
        self.sleep_func = sleep_func or time.sleep

        # QPS 滑动窗口：只存请求发起的物理时间戳 float
        self.qps_window: collections.deque = collections.deque()
        # TPM 滑动窗口：存放 [request_time, estimated_tokens, real_tokens, is_completed] 列表
        self.tpm_window: collections.deque = collections.deque()

        # 自适应限流调整参数 (AIMD 算法底座)
        self.adaptive_qps: float = float(getattr(limits, 'rate_limit_qps', 10.0))
        self.adaptive_tpm: float = float(getattr(limits, 'max_tokens_per_min', 40000.0))

        self.last_429_time: float = 0.0

    def acquire(self, estimated_tokens: int, sleep_func: Optional[Any] = None) -> None:
        """🛡️ 主动限流阻塞原子。若当前窗口的 QPS 或 TPM 已经超限，则进行精确微小休眠直到滑出窗口。"""
        sleep_fn = sleep_func or self.sleep_func
        while True:
            now = time.time()
            sleep_time = 0.0

            with self.lock:
                # 1. 物理清理：滑出 1.0 秒以外的 QPS 记录
                while self.qps_window and now - self.qps_window[0] > 1.0:
                    self.qps_window.popleft()

                # 2. 物理清理：滑出 60.0 秒以外的 TPM 记录
                while self.tpm_window and now - self.tpm_window[0][0] > 60.0:
                    self.tpm_window.popleft()

                # 3. 核算 QPS 滑动窗口限制
                current_qps = len(self.qps_window)
                if current_qps >= self.adaptive_qps:
                    oldest_qps_time = self.qps_window[0]
                    sleep_time = max(sleep_time, 1.0 - (now - oldest_qps_time))

                # 4. 核算 TPM 滑动窗口限制
                used_tokens = 0
                for item in self.tpm_window:
                    # 已完成的使用真实 Token 量，未完成的（正在网络调用中）使用估算 Token 量
                    used_tokens += item[2] if item[3] else item[1]

                if used_tokens + estimated_tokens > self.adaptive_tpm:
                    # 寻找滑出后能容纳本次请求的最早时间点
                    accumulated_wait_tokens = used_tokens + estimated_tokens
                    for item in self.tpm_window:
                        item_tokens = item[2] if item[3] else item[1]
                        if item_tokens > 0:
                            accumulated_wait_tokens -= item_tokens
                            if accumulated_wait_tokens <= self.adaptive_tpm:
                                sleep_time = max(sleep_time, 60.0 - (now - item[0]))
                                break

            if sleep_time > 0.0:
                # 带入微小随机偏差以防多线程同时唤醒造成瞬时并发冲突
                import random
                sleep_fn(sleep_time + random.uniform(0.01, 0.05))
            else:
                # 成功放行，物理注册本次发送时间与预估 Token
                with self.lock:
                    now_record = time.time()
                    self.qps_window.append(now_record)
                    self.tpm_window.append([now_record, estimated_tokens, 0, False])
                break

    def update_tokens(self, request_time: float, real_tokens: int) -> None:
        """🚀 修正预估。当调用成功时，将真实的 prompt + completion 写入窗口，并平滑加性递增恢复速度。"""
        with self.lock:
            best_item = None
            min_diff = 9999.0
            for item in self.tpm_window:
                if not item[3]:
                    diff = abs(item[0] - request_time)
                    if diff < min_diff:
                        min_diff = diff
                        best_item = item

            if best_item and min_diff < 10.0:
                best_item[2] = real_tokens
                best_item[3] = True

            # AIMD (Additive Increase): 成功调用后慢慢朝物理上限靠拢
            orig_qps = float(getattr(self.limits, 'rate_limit_qps', 10.0))
            orig_tpm = float(getattr(self.limits, 'max_tokens_per_min', 40000.0))

            if self.adaptive_qps < orig_qps:
                self.adaptive_qps = min(orig_qps, self.adaptive_qps + 0.1)
            if self.adaptive_tpm < orig_tpm:
                self.adaptive_tpm = min(orig_tpm, self.adaptive_tpm + 200.0)

    def record_rate_limit_error(self) -> None:
        """📉 AIMD (Multiplicative Decrease): 收到 429 报错时，乘性衰减速率限制，实施紧急避险。"""
        now = time.time()
        with self.lock:
            if now - self.last_429_time > 2.0:
                self.last_429_time = now
                old_qps = self.adaptive_qps
                old_tpm = self.adaptive_tpm

                # 乘性衰减 30% (即降至 70%)。保底 QPS 为 1.0，保底 TPM 为 5000.0
                self.adaptive_qps = max(1.0, self.adaptive_qps * 0.7)
                self.adaptive_tpm = max(5000.0, self.adaptive_tpm * 0.7)

                tlog.warning(
                    f"📉 [自适应流控避险] 节点 {self.node_name} 触碰限流门槛。QPS 阈值: {old_qps:.1f} -> {self.adaptive_qps:.1f}，TPM 阈值: {old_tpm:.0f} -> {self.adaptive_tpm:.0f}。"
                )
