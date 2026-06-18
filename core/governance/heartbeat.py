#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Governance - Heartbeat Service
模块职责：全量观测性。周期性聚合系统负载、算力进度与任务流，导出 Pulse 数据供仪表盘展示。
🛡️ [AEL-Iter-v1.0]：商用级实时监控引擎。
"""

import threading
import time
import json
import os
from datetime import datetime
from core.utils.tracing import tlog
from core.utils.common import atomic_write

class HeartbeatService:
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
        
        # 🚀 [新增] 动态算力池待处理任务最大值记录，用于平滑进度计算
        self._max_pending_ai = 0
        self._max_pending_asset = 0

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
                pulse_data = self._gather_pulse()
                atomic_write(self.pulse_path, json.dumps(pulse_data, indent=2, ensure_ascii=False))
            except Exception as e:
                tlog.error(f"⚠️ [Heartbeat] 脉搏采集异常: {e}")
            
            self.stop_flag.wait(self.interval)

    def _gather_pulse(self):
        """聚合全量实时指标"""
        from core.logic.orchestration.task_orchestrator import global_executor, ai_executor, asset_executor
        
        # 1. 采集算力池实时统计 (🚀 [V24.0] 使用标准化观测接口)
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
        
        # 3. 采集进度
        current = getattr(self.engine, '_last_progress', 0)
        total = getattr(self.engine, '_total_progress', 0)
        
        # 🚀 [主权自愈进度计算]：智能引入异步算力池的排队待处理任务，实现进度无缝平滑过渡
        if total > 0:
            if pending_ai > self._max_pending_ai:
                self._max_pending_ai = pending_ai
            if pending_asset > self._max_pending_asset:
                self._max_pending_asset = pending_asset
                
            adjusted_total = total + self._max_pending_ai + self._max_pending_asset
            adjusted_current = current + (self._max_pending_ai - pending_ai) + (self._max_pending_asset - pending_asset)
            
            # 防御性边界修剪
            adjusted_current = max(0, min(adjusted_current, adjusted_total))
            percentage = round((adjusted_current / adjusted_total * 100), 2) if adjusted_total > 0 else 0
            
            current = adjusted_current
            total = adjusted_total
        elif pending_ai > 0 or pending_asset > 0:
            # 大盘进度未设置，但算力池中确实存在活跃任务（如单文件热更新，或收割残留期）
            if pending_ai > self._max_pending_ai:
                self._max_pending_ai = pending_ai
            if pending_asset > self._max_pending_asset:
                self._max_pending_asset = pending_asset
            
            # 至少以 1 个文档或待处理总任务作为大盘分母
            temp_max = max(1, self._max_pending_ai + self._max_pending_asset)
            adjusted_total = temp_max
            adjusted_current = max(0, temp_max - (pending_ai + pending_asset))
            
            # 防御性边界修剪
            adjusted_current = max(0, min(adjusted_current, adjusted_total))
            percentage = round((adjusted_current / adjusted_total * 100), 2) if adjusted_total > 0 else 0
            
            current = adjusted_current
            total = adjusted_total
        else:
            # 任务全部完成，重置算力池最大跟踪值
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
                "tokens": getattr(gov.meter, 'total_usage', 0) if gov and hasattr(gov, 'meter') else 0,
                "cost": getattr(gov.meter, 'total_cost', 0) if gov and hasattr(gov, 'meter') else 0
            }
        }
