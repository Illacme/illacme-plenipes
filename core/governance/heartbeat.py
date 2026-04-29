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
        theme = getattr(engine, 'active_theme', 'default')
        self.pulse_path = getattr(engine, 'paths', {}).get('pulse') or engine._resolve_path(f"metadata/pulse_{theme}.json")
        
        # 🛡️ [原子化对齐] 确保目录存在且不报 Errno 17
        os.makedirs(os.path.dirname(self.pulse_path), exist_ok=True)
        
        self.start_time = time.time()

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
            
            time.sleep(self.interval)

    def _gather_pulse(self):
        """聚合全量实时指标"""
        from core.logic.orchestration.task_orchestrator import global_executor, ai_executor, asset_executor
        
        # 1. 采集算力池实时统计 (🚀 [V24.0] 使用标准化观测接口)
        global_stats = global_executor.get_stats()
        ai_stats = ai_executor.get_stats()
        asset_stats = asset_executor.get_stats()
            
        # 2. 采集负载指标
        load = {}
        if hasattr(self.engine, 'resource_guard'):
            rg = self.engine.resource_guard
            load = {
                "cpu_percent": getattr(rg, 'cpu_percent', 0),
                "memory_percent": getattr(rg, 'memory_percent', 0)
            }
        
        # 3. 采集进度
        current = getattr(self.engine, '_last_progress', 0)
        total = getattr(self.engine, '_total_progress', 0)
        percentage = round((current / total * 100), 2) if total > 0 else 0
        
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
                "total_queue": global_stats["queue_size"] + ai_stats["queue_size"] + asset_stats["queue_size"]
            },
            "load": load,
            "usage": {
                "tokens": getattr(self.engine.meter, 'total_usage', 0) if hasattr(self.engine, 'meter') else 0,
                "cost": getattr(self.engine.meter, 'total_cost', 0) if hasattr(self.engine, 'meter') else 0
            }
        }
