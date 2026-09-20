#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Governance - Heartbeat Service
模块职责：全量观测性。周期性聚合系统负载、算力进度与任务流，导出 Pulse 数据供仪表盘展示。
🛡️ [SOP-01 & SOP-02]：自底向上物理拆分重构版本，单文件物理行数严格 ≤300 行。
"""

import threading
import time
import json
import os
from datetime import datetime
from core.utils.tracing import tlog
from core.utils.common import atomic_write
from .heartbeat_telemetry import TelemetryArchiveMixin


class HeartbeatService(TelemetryArchiveMixin):
    """🚀 [V1.0] 心跳服务：引擎实时脉搏"""

    def __init__(self, engine, pulse_interval: float = 2.0):
        self.engine = engine
        self.interval = pulse_interval
        self.stop_flag = threading.Event()
        self.thread = None
        
        # 🚀 [V24.0] 引用主权路径协议，防御性探测时序冲突
        self.pulse_path = engine._resolve_path(engine.config.get_pulse_path())
        
        # 🛡️ [原子化对齐] 确保目录存在且不报 Errno 17
        os.makedirs(os.path.dirname(self.pulse_path), exist_ok=True)
        
        self.start_time = time.time()
        
        # 动态算力池待处理任务最大值记录，用于平滑进度计算
        self._max_pending_ai = 0
        self._max_pending_asset = 0
        
        # 遥测历史与长效归档初始化
        self.init_telemetry_state(getattr(engine, "config", None), self.pulse_path)
        
        self.last_tokens_count = 0
        self.last_time = time.time()
        self.last_write_time = 0.0

    def start(self):
        """点火心跳线程"""
        if self.thread and self.thread.is_alive():
            return
            
        tlog.info(f"💓 [Heartbeat] 心跳服务点火，Pulse 导出至: {self.pulse_path}")
        self.stop_flag.clear()
        self.thread = threading.Thread(target=self._pulse_loop, name="Heartbeat", daemon=True)
        self.thread.start()

    def stop(self):
        self.stop_flag.set()
        if self.thread:
            self.thread.join(timeout=1.0)

    def _pulse_loop(self):
        while not self.stop_flag.is_set():
            try:
                self._pulse_step()
            except Exception as e:
                tlog.error(f"⚠️ [Heartbeat] 脉搏采集异常: {e}")
            
            self.stop_flag.wait(self.interval)

    def _pulse_step(self):
        """单次脉搏采集与自适应写盘决策"""
        config = getattr(self.engine, "config", None)
        self.adapt_telemetry_limits(config)

        pulse_data = self._gather_pulse()
        
        should_force_write = self.process_archive_tick()
        if should_force_write:
            pulse_data = self._gather_pulse()

        # 🚀 [V75.6] 自适应降频写入物理磁盘：判断当前系统是否处于“闲置 (Idle)”状态
        cpu_val = self.history_cpu[-1] if self.history_cpu else 0.0
        workers_val = self.history_active_workers[-1] if self.history_active_workers else 0.0
        is_idle = (cpu_val < 5.0) and (workers_val == 0.0)
        
        now = time.time()
        if is_idle and (now - self.last_write_time < 10.0) and not should_force_write:
            pass
        else:
            atomic_write(self.pulse_path, json.dumps(pulse_data, indent=2, ensure_ascii=False))
            self.last_write_time = now

    def _gather_pulse(self):
        """聚合全量实时指标"""
        from core.logic.orchestration.task_orchestrator import global_executor, ai_executor, asset_executor
        
        # 1. 采集算力池实时统计
        global_stats = global_executor.get_stats()
        ai_stats = ai_executor.get_stats()
        asset_stats = asset_executor.get_stats()
        
        pending_ai = (ai_stats or {}).get("queue_size", 0) + (ai_stats or {}).get("active_workers", 0)
        pending_asset = (asset_stats or {}).get("queue_size", 0) + (asset_stats or {}).get("active_workers", 0)
        pending_global = (global_stats or {}).get("queue_size", 0) + (global_stats or {}).get("active_workers", 0)
            
        # 2. 采集负载指标
        load = {}
        gov = getattr(self.engine, 'governance', None)
        if gov and hasattr(gov, 'resource_guard'):
            rg = gov.resource_guard
            load = {
                "cpu_percent": getattr(rg, 'cpu_usage', 0),
                "memory_percent": getattr(rg, 'ram_usage', 0),
                "compute_memory_percent": getattr(rg, 'compute_ram_usage', 0.0)
            }
        
        # 计量修复与 Token 即时速率计算
        tokens_count = 0
        cost_amount = 0.0
        if gov and hasattr(gov, 'meter') and hasattr(gov.meter, 'get_summary_report'):
            summary = gov.meter.get_summary_report() or {}
            tokens_count = summary.get("input_tokens", 0) + summary.get("output_tokens", 0)
            cost_amount = summary.get("cost", 0.0)
            
        now = time.time()
        time_delta = now - self.last_time
        if time_delta > 0.5:
            tokens_rate = max(0.0, (tokens_count - self.last_tokens_count) / time_delta)
            self.last_tokens_count = tokens_count
            self.last_time = now
        else:
            tokens_rate = self.history_tokens_rate[-1] if self.history_tokens_rate else 0.0

        cpu_pct = load.get("cpu_percent", 0.0) or 0.0
        mem_pct = load.get("memory_percent", 0.0) or 0.0
        comp_pct = load.get("compute_memory_percent", 0.0) or 0.0
        active_workers = (ai_stats or {}).get("active_workers", 0) or 0

        self.history_cpu.append(cpu_pct)
        self.history_mem.append(mem_pct)
        self.history_comp.append(comp_pct)
        self.history_tokens_rate.append(tokens_rate)
        self.history_active_workers.append(active_workers)

        if len(self.history_cpu) > self.history_limit:
            self.history_cpu.pop(0)
            self.history_mem.pop(0)
            self.history_comp.pop(0)
            self.history_tokens_rate.pop(0)
            self.history_active_workers.pop(0)
        
        # 3. 采集进度
        current = getattr(self.engine, '_last_progress', 0)
        total = getattr(self.engine, '_total_progress', 0)
        
        # 主权自愈进度计算：引入异步算力池的排队待处理任务，实现进度平滑过渡
        if total > 0:
            if pending_ai > self._max_pending_ai:
                self._max_pending_ai = pending_ai
            if pending_asset > self._max_pending_asset:
                self._max_pending_asset = pending_asset
                
            adjusted_total = total + self._max_pending_ai + self._max_pending_asset
            adjusted_current = current + (self._max_pending_ai - pending_ai) + (self._max_pending_asset - pending_asset)
            adjusted_current = max(0, min(adjusted_current, adjusted_total))
            percentage = round((adjusted_current / adjusted_total * 100), 2) if adjusted_total > 0 else 0
            current, total = adjusted_current, adjusted_total
        elif pending_ai > 0 or pending_asset > 0:
            if pending_ai > self._max_pending_ai:
                self._max_pending_ai = pending_ai
            if pending_asset > self._max_pending_asset:
                self._max_pending_asset = pending_asset
            
            temp_max = max(1, self._max_pending_ai + self._max_pending_asset)
            adjusted_total = temp_max
            adjusted_current = max(0, temp_max - (pending_ai + pending_asset))
            adjusted_current = max(0, min(adjusted_current, adjusted_total))
            percentage = round((adjusted_current / adjusted_total * 100), 2) if adjusted_total > 0 else 0
            current, total = adjusted_current, adjusted_total
        else:
            self._max_pending_ai = 0
            self._max_pending_asset = 0
            percentage = 0
        
        return {
            "version": "V24.0",
            "timestamp": datetime.now().isoformat(),
            "uptime": int(time.time() - self.start_time),
            "status": "RUNNING" if not self.stop_flag.is_set() else "IDLE",
            "progress": {
                "current": current,
                "total": total,
                "percentage": percentage
            },
            "pools": {
                "global": global_stats,
                "ai": ai_stats,
                "asset": asset_stats,
                "total_queue": pending_global + pending_ai + pending_asset
            },
            "load": load,
            "usage": {
                "tokens": tokens_count,
                "cost": cost_amount
            },
            "history": {
                "cpu": self.history_cpu,
                "memory": self.history_mem,
                "compute_memory": self.history_comp,
                "tokens_rate": self.history_tokens_rate,
                "active_workers": self.history_active_workers
            },
            "history_archive": {
                "cpu": self.history_archive_cpu,
                "memory": self.history_archive_mem,
                "compute_memory": self.history_archive_comp,
                "tokens_rate": self.history_archive_tokens_rate,
                "active_workers": self.history_archive_active_workers
            }
        }
