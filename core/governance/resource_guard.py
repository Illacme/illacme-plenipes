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
        self._interval = check_interval
        self.stop_flag = threading.Event()
        self.thread = None
        
        # 🚀 [V48.3] 属性控制权回传：初始化设值，优先从配置中动态获取
        governance_cfg = getattr(engine.config.system, 'governance', None)
        rg_cfg = getattr(governance_cfg, 'resource_guard', None) if governance_cfg else None
        
        self.interval = getattr(rg_cfg, 'check_interval', check_interval) if rg_cfg else check_interval
        self.compute_ram_usage = 0.0
        
        self.is_throttled = False
        self.original_concurrency = None
        
        self.cpu_usage = 0.0
        self.ram_usage = 0.0

    @property
    def cpu_threshold(self) -> float:
        governance_cfg = getattr(self.engine.config.system, 'governance', None)
        rg_cfg = getattr(governance_cfg, 'resource_guard', None) if governance_cfg else None
        return getattr(rg_cfg, 'cpu_threshold', 85.0) if rg_cfg else 85.0

    @property
    def ram_threshold(self) -> float:
        governance_cfg = getattr(self.engine.config.system, 'governance', None)
        rg_cfg = getattr(governance_cfg, 'resource_guard', None) if governance_cfg else None
        return getattr(rg_cfg, 'ram_threshold', 85.0) if rg_cfg else 85.0

    @property
    def compute_ram_threshold(self) -> float:
        governance_cfg = getattr(self.engine.config.system, 'governance', None)
        rg_cfg = getattr(governance_cfg, 'resource_guard', None) if governance_cfg else None
        return getattr(rg_cfg, 'compute_ram_threshold', 50.0) if rg_cfg else 50.0

    @property
    def compute_process_names(self) -> list:
        sys_cfg = getattr(getattr(self.engine, 'config', None), 'system', None)
        governance_cfg = getattr(sys_cfg, 'governance', None) if sys_cfg else None
        rg_cfg = getattr(governance_cfg, 'resource_guard', None) if governance_cfg else None
        return getattr(rg_cfg, 'compute_process_names', ["lmstudio", "ollama", "llama", "llama-box"]) if rg_cfg else ["lmstudio", "ollama", "llama", "llama-box"]

    @property
    def interval(self) -> float:
        sys_cfg = getattr(getattr(self.engine, 'config', None), 'system', None)
        governance_cfg = getattr(sys_cfg, 'governance', None) if sys_cfg else None
        rg_cfg = getattr(governance_cfg, 'resource_guard', None) if governance_cfg else None
        return getattr(rg_cfg, 'check_interval', self._interval) if rg_cfg else self._interval

    @interval.setter
    def interval(self, val: float):
        self._interval = val

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

                # 🚀 [精准监控] 遍历进程列表，累加白名单中算力进程的常驻内存集（RSS）物理占用
                total_compute_rss = 0
                for proc in psutil.process_iter(['name']):
                    try:
                        p_name = (proc.info['name'] or '').lower()
                        if any(pn.lower() in p_name for pn in self.compute_process_names):
                            total_compute_rss += proc.memory_info().rss
                    except Exception:
                        pass
                
                # 计算算力进程占物理总内存的比例百分比
                total_mem = psutil.virtual_memory().total
                compute_ram_percent = (total_compute_rss / total_mem) * 100.0 if total_mem > 0 else 0.0
                self.compute_ram_usage = compute_ram_percent
                
                # 🚀 [V1.2] 并发限制基线动态滑动同步
                if not self.is_throttled:
                    # 未处于限流削峰状态时，实时与引擎最新的并发限制配置对齐
                    self.original_concurrency = {
                        "global": self.engine.config.system.concurrency.global_workers,
                        "ai": self.engine.config.system.concurrency.ai_workers
                    }
                elif self.original_concurrency is None:
                    # 极端兜底防御：若一启动就是限流状态且original_concurrency为空，从配置获取
                    self.original_concurrency = {
                        "global": self.engine.config.system.concurrency.global_workers,
                        "ai": self.engine.config.system.concurrency.ai_workers
                    }

                # 🚀 [V48.3] 引入滞后区间 (Hysteresis) 以防止震荡
                upper_cpu = self.cpu_threshold
                upper_ram = self.ram_threshold
                upper_compute_ram = self.compute_ram_threshold
                
                lower_cpu = upper_cpu - 5.0
                lower_ram = upper_ram - 5.0
                lower_compute_ram = upper_compute_ram - 5.0
                
                if not self.is_throttled:
                    # 触发判定：CPU超限，或算力自身超限，或总RAM超限且算力进程有运行（共振）
                    should_throttle = (
                        cpu_usage > upper_cpu
                        or compute_ram_percent > upper_compute_ram
                        or (ram_usage > upper_ram and compute_ram_percent > 5.0)
                    )
                else:
                    # 释放判定：必须全面回落
                    should_throttle = (
                        cpu_usage > lower_cpu
                        or compute_ram_percent > lower_compute_ram
                        or (ram_usage > lower_ram and compute_ram_percent > 5.0)
                    )
                
                if should_throttle and not self.is_throttled:
                    # 🚀 [V51.0] 使用对齐的 get_stats() 获取运行指标
                    from core.logic.orchestration.task_orchestrator import global_executor
                    stats = global_executor.get_stats()
                    has_active_tasks = stats["queue_size"] > 0 or stats["active_workers"] > 0
                    
                    self._apply_throttle(cpu_usage, ram_usage, compute_ram_percent, silent=not has_active_tasks)
                elif not should_throttle and self.is_throttled:
                    self._release_throttle()
                    
            except Exception as e:
                tlog.error(f"⚠️ [ResourceGuard] 监控异常: {e}")
            
            self.stop_flag.wait(self.interval)

    def _apply_throttle(self, cpu, ram, compute_ram, silent=False):
        """执行紧急削峰：将并发下调至最低保障水平"""
        if not silent:
            tlog.warning(f"🚨 [ResourceGuard] 物理负载过高 (CPU: {cpu}% | RAM: {ram}% | 算力进程: {compute_ram:.2f}%)！正在紧急削峰...")
        else:
            tlog.debug(f"🛡️ [ResourceGuard] 环境负载高 (RAM: {ram}% | 算力进程: {compute_ram:.2f}%)，已提前预置算力削峰 (静默模式)")
        
        from core.logic.orchestration.task_orchestrator import global_executor, ai_executor
        
        # 下调至最小保护值 (由 Orchestrator 保证不低于 1)
        global_executor.update_concurrency(1)
        
        # 🚀 [V1.1] 修复并发倒挂缺陷：AI 并发降级为原始配置的一半，且不超过 4
        orig_ai = self.original_concurrency.get("ai", 4) if self.original_concurrency else 4
        target_ai = max(1, min(orig_ai // 2, 4))
        ai_executor.update_concurrency(target_ai)
        
        self.is_throttled = True
        from core.utils.event_bus import bus
        bus.emit("UI_RESOURCE_THROTTLE", active=True, cpu=cpu, ram=ram)

    def _release_throttle(self):
        """负载回落：恢复至配置定义的并发水平"""
        tlog.info("🟢 [ResourceGuard] 物理负载已回落，正在恢复满血算力...")
        
        from core.logic.orchestration.task_orchestrator import global_executor, ai_executor
        
        orig = self.original_concurrency or {}
        global_executor.update_concurrency(orig.get("global", 1))
        ai_executor.update_concurrency(orig.get("ai", 4))
        
        self.is_throttled = False
        from core.utils.event_bus import bus
        bus.emit("UI_RESOURCE_THROTTLE", active=False)
