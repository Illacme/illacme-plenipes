#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Governance - Resource Guard
模块职责：全量资源守卫。监控 CPU/RAM 负载，并动态触发算力下调以保护宿主系统稳定性。
🛡️ [AEL-Iter-v1.0]：基于物理压力的自适应并发治理系统。
"""

import threading
import time
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

from core.utils.tracing import tlog

class ResourceGuard:
    """🚀 [V1.0] 资源守卫：自适应算力调节中枢"""

    def __init__(self, engine, check_interval: float = 5.0):
        self.engine = engine
        self.interval = check_interval
        self.stop_flag = threading.Event()
        self.thread = None
        
        # 🚀 [V24.6] 阈值控制权回传：优先从配置中心读取，兜底值为 85%
        governance_cfg = getattr(engine.config.system, 'governance', None)
        rg_cfg = getattr(governance_cfg, 'resource_guard', None) if governance_cfg else None
        
        self.cpu_threshold = getattr(rg_cfg, 'cpu_threshold', 85.0) if rg_cfg else 85.0
        self.ram_threshold = getattr(rg_cfg, 'ram_threshold', 85.0) if rg_cfg else 85.0
        self.interval = getattr(rg_cfg, 'check_interval', check_interval) if rg_cfg else check_interval
        
        self.is_throttled = False
        self.original_concurrency = None
        
        self.cpu_usage = 0.0
        self.ram_usage = 0.0

    def start(self):
        """在后台启动资源监控线程"""
        if self.thread and self.thread.is_alive():
            return
            
        tlog.info("🛡️ [ResourceGuard] 资源守卫已上线，正在实时监控物理负载...")
        self.stop_flag.clear()
        self.thread = threading.Thread(target=self._monitor_loop, name="ResourceGuard", daemon=True)
        self.thread.start()

    def stop(self):
        self.stop_flag.set()
        if self.thread:
            self.thread.join(timeout=1.0)

    def _monitor_loop(self):
        if not HAS_PSUTIL:
            tlog.warning("🛡️ [ResourceGuard] 环境缺失 psutil，资源自适应削峰功能已降级关闭。")
            return

        while not self.stop_flag.is_set():
            try:
                cpu_usage = psutil.cpu_percent(interval=1)
                ram_usage = psutil.virtual_memory().percent
                
                self.cpu_usage = cpu_usage
                self.ram_usage = ram_usage
                
                # 记录原始并发数（初次启动时）
                if self.original_concurrency is None:
                    self.original_concurrency = {
                        "global": self.engine.config.system.concurrency.global_workers,
                        "ai": self.engine.config.system.concurrency.ai_workers
                    }

                # 🚀 [V24.6] 引入滞后区间 (Hysteresis) 以防止震荡
                # 触发阈值后，必须回落 5% 才能恢复，避免临界点反复弹跳
                upper_cpu = self.cpu_threshold
                upper_ram = self.ram_threshold
                lower_cpu = upper_cpu - 5.0
                lower_ram = upper_ram - 5.0
                
                if not self.is_throttled:
                    should_throttle = cpu_usage > upper_cpu or ram_usage > upper_ram
                else:
                    # 已处于削峰状态，只有降到 lower 以下才释放
                    should_throttle = cpu_usage > lower_cpu and ram_usage > lower_ram

                if should_throttle and not self.is_throttled:
                    # 🚀 [V24.6] 静默治理：只有在真正有任务在跑时才打印警告
                    from core.logic.orchestration.task_orchestrator import global_executor
                    has_active_tasks = global_executor.get_queue_size() > 0 or global_executor.get_active_count() > 0
                    
                    self._apply_throttle(cpu_usage, ram_usage, silent=not has_active_tasks)
                elif not should_throttle and self.is_throttled:
                    self._release_throttle()
                    
            except Exception as e:
                tlog.error(f"⚠️ [ResourceGuard] 监控异常: {e}")
            
            time.sleep(self.interval)

    def _apply_throttle(self, cpu, ram, silent=False):
        """执行紧急削峰：将并发下调至最低保障水平"""
        if not silent:
            tlog.warning(f"🚨 [ResourceGuard] 物理负载过高 (CPU: {cpu}% | RAM: {ram}%)！正在紧急削峰...")
        else:
            tlog.debug(f"🛡️ [ResourceGuard] 环境负载高 (RAM: {ram}%)，已提前预置算力削峰 (静默模式)")
        
        from core.logic.orchestration.task_orchestrator import global_executor, ai_executor
        
        # 下调至最小保护值 (由 Orchestrator 保证不低于 1)
        global_executor.update_concurrency(1)
        # AI 池也下调，但保留基本响应能力
        ai_executor.update_concurrency(4)
        
        self.is_throttled = True
        from core.utils.event_bus import bus
        bus.emit("UI_RESOURCE_THROTTLE", active=True, cpu=cpu, ram=ram)

    def _release_throttle(self):
        """负载回落：恢复至配置定义的并发水平"""
        tlog.info("🟢 [ResourceGuard] 物理负载已回落，正在恢复满血算力...")
        
        from core.logic.orchestration.task_orchestrator import global_executor, ai_executor
        
        orig = self.original_concurrency
        global_executor.update_concurrency(orig["global"])
        ai_executor.update_concurrency(orig["ai"])
        
        self.is_throttled = False
        from core.utils.event_bus import bus
        bus.emit("UI_RESOURCE_THROTTLE", active=False)
