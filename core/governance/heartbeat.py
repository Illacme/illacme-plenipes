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
        
        # 🚀 [Cold-Start Recovery] 冷启动物理加载恢复：若存在 pulse.json，继承其历史轨迹以防断崖
        # 🚀 [V75.7] 自适应读取系统底座遥测保存点数上限限制，并做好安全自愈退避
        config = getattr(engine, "config", None)
        sys_limit = 150
        if config and hasattr(config, "system"):
            sys_limit = getattr(config.system, "telemetry_history_limit", 150)
            
        self.history_limit = sys_limit
        self.history_cpu = [0.0] * self.history_limit
        self.history_mem = [0.0] * self.history_limit
        self.history_comp = [0.0] * self.history_limit
        self.history_tokens_rate = [0.0] * self.history_limit
        self.history_active_workers = [0.0] * self.history_limit

        # 🚀 [V75.7] 动态长效历史归档设置加载与安全退避
        sys_archive_limit = 360
        sys_archive_interval = 120
        if config and hasattr(config, "system"):
            sys_archive_limit = getattr(config.system, "telemetry_archive_limit", 360)
            sys_archive_interval = getattr(config.system, "telemetry_archive_interval_seconds", 120)
            
        self.history_archive_limit = sys_archive_limit
        self.archive_interval_seconds = sys_archive_interval
        
        self.history_archive_cpu = [0.0] * self.history_archive_limit
        self.history_archive_mem = [0.0] * self.history_archive_limit
        self.history_archive_comp = [0.0] * self.history_archive_limit
        self.history_archive_tokens_rate = [0.0] * self.history_archive_limit
        self.history_archive_active_workers = [0.0] * self.history_archive_limit

        # 归档缓存与计数器
        self.archive_buffer_cpu = []
        self.archive_buffer_mem = []
        self.archive_buffer_comp = []
        self.archive_buffer_tokens = []
        self.archive_buffer_workers = []
        self.tick_counter = 0
        
        if os.path.exists(self.pulse_path):
            try:
                with open(self.pulse_path, 'r', encoding='utf-8') as f:
                    old_data = json.load(f)
                    old_hist = old_data.get("history", {})
                    
                    def restore_list(key, default_val):
                        lst = old_hist.get(key, [])
                        if not isinstance(lst, list):
                            return [default_val] * self.history_limit
                        if len(lst) < self.history_limit:
                            return [default_val] * (self.history_limit - len(lst)) + lst
                        return lst[-self.history_limit:]
                        
                    self.history_cpu = restore_list("cpu", 0.0)
                    self.history_mem = restore_list("memory", 0.0)
                    self.history_comp = restore_list("compute_memory", 0.0)
                    self.history_tokens_rate = restore_list("tokens_rate", 0.0)
                    self.history_active_workers = restore_list("active_workers", 0.0)

                    # 物理冷启动归档数据继承
                    old_hist_arch = old_data.get("history_archive", {})
                    
                    def restore_archive_list(key, default_val):
                        lst = old_hist_arch.get(key, [])
                        if not isinstance(lst, list):
                            return [default_val] * self.history_archive_limit
                        if len(lst) < self.history_archive_limit:
                            return [default_val] * (self.history_archive_limit - len(lst)) + lst
                        return lst[-self.history_archive_limit:]

                    self.history_archive_cpu = restore_archive_list("cpu", 0.0)
                    self.history_archive_mem = restore_archive_list("memory", 0.0)
                    self.history_archive_comp = restore_archive_list("compute_memory", 0.0)
                    self.history_archive_tokens_rate = restore_archive_list("tokens_rate", 0.0)
                    self.history_archive_active_workers = restore_archive_list("active_workers", 0.0)

                    tlog.info("💓 [Heartbeat] 物理冷启动成功继承旧遥测时序历史与长效归档")
            except Exception as e:
                tlog.warning(f"⚠️ [Heartbeat] 物理冷启动载入旧历史及归档异常: {e}")
        
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
        # 🚀 [V75.7] 动态负载历史点数上限热加载与内存历史数据自适应缩放
        config = getattr(self.engine, "config", None)
        if config and hasattr(config, "system"):
            new_limit = getattr(config.system, "telemetry_history_limit", 150)
            if new_limit != self.history_limit:
                self.history_limit = new_limit
                
                def resize_history(lst):
                    if len(lst) > self.history_limit:
                        return lst[-self.history_limit:]
                    elif len(lst) < self.history_limit:
                        return [0.0] * (self.history_limit - len(lst)) + lst
                    return lst

                self.history_cpu = resize_history(self.history_cpu)
                self.history_mem = resize_history(self.history_mem)
                self.history_comp = resize_history(self.history_comp)
                self.history_tokens_rate = resize_history(self.history_tokens_rate)
                self.history_active_workers = resize_history(self.history_active_workers)

            # 🚀 [V75.7] 动态长效历史归档限制及热生效自愈
            new_arch_limit = getattr(config.system, "telemetry_archive_limit", 360)
            new_arch_interval = getattr(config.system, "telemetry_archive_interval_seconds", 120)
            
            if new_arch_limit != self.history_archive_limit:
                self.history_archive_limit = new_arch_limit
                def resize_archive_history(lst):
                    if len(lst) > self.history_archive_limit:
                        return lst[-self.history_archive_limit:]
                    elif len(lst) < self.history_archive_limit:
                        return [0.0] * (self.history_archive_limit - len(lst)) + lst
                    return lst
                
                self.history_archive_cpu = resize_archive_history(self.history_archive_cpu)
                self.history_archive_mem = resize_archive_history(self.history_archive_mem)
                self.history_archive_comp = resize_archive_history(self.history_archive_comp)
                self.history_archive_tokens_rate = resize_archive_history(self.history_archive_tokens_rate)
                self.history_archive_active_workers = resize_archive_history(self.history_archive_active_workers)
                
            self.archive_interval_seconds = new_arch_interval

        pulse_data = self._gather_pulse()
        
        # 🚀 [V75.7] 累加最新采样点至归档缓冲区
        self.archive_buffer_cpu.append(self.history_cpu[-1] if self.history_cpu else 0.0)
        self.archive_buffer_mem.append(self.history_mem[-1] if self.history_mem else 0.0)
        self.archive_buffer_comp.append(self.history_comp[-1] if self.history_comp else 0.0)
        self.archive_buffer_tokens.append(self.history_tokens_rate[-1] if self.history_tokens_rate else 0.0)
        self.archive_buffer_workers.append(self.history_active_workers[-1] if self.history_active_workers else 0.0)
        
        self.tick_counter += 1
        
        # 计算当前归档所需要的 tick 数量（心跳周期默认是 2.0s）
        ticks_needed = max(1, int(self.archive_interval_seconds / self.interval))
        
        should_force_write = False
        if self.tick_counter >= ticks_needed:
            # 计算均值并写入长效归档
            def calc_avg(lst):
                return sum(lst) / len(lst) if lst else 0.0
                
            self.history_archive_cpu.append(calc_avg(self.archive_buffer_cpu))
            self.history_archive_mem.append(calc_avg(self.archive_buffer_mem))
            self.history_archive_comp.append(calc_avg(self.archive_buffer_comp))
            self.history_archive_tokens_rate.append(calc_avg(self.archive_buffer_tokens))
            self.history_archive_active_workers.append(calc_avg(self.archive_buffer_workers))
            
            # 维持归档点数上限限制
            if len(self.history_archive_cpu) > self.history_archive_limit:
                self.history_archive_cpu.pop(0)
                self.history_archive_mem.pop(0)
                self.history_archive_comp.pop(0)
                self.history_archive_tokens_rate.pop(0)
                self.history_archive_active_workers.pop(0)
                
            # 清空缓冲区及复位计数器
            self.archive_buffer_cpu.clear()
            self.archive_buffer_mem.clear()
            self.archive_buffer_comp.clear()
            self.archive_buffer_tokens.clear()
            self.archive_buffer_workers.clear()
            self.tick_counter = 0
            
            # 晋归后重新拼装 pulse_data 以固化写入，并强制落盘
            pulse_data = self._gather_pulse()
            should_force_write = True

        # 🚀 [V75.6] 自适应降频写入物理磁盘：
        # 判断当前系统是否处于“闲置 (Idle)”状态
        # 闲置指标：
        # 1. 最后一个 CPU 时序负载低于 5.0%
        # 2. 内存中的 active workers 时序全为 0
        cpu_val = self.history_cpu[-1] if self.history_cpu else 0.0
        workers_val = self.history_active_workers[-1] if self.history_active_workers else 0.0
        
        is_idle = (cpu_val < 5.0) and (workers_val == 0.0)
        
        now = time.time()
        # 如果处于闲置状态且距离上一次物理写入不足 10 秒，且非归档强落盘，则跳过物理落盘
        if is_idle and (now - self.last_write_time < 10.0) and not should_force_write:
            pass
        else:
            atomic_write(self.pulse_path, json.dumps(pulse_data, indent=2, ensure_ascii=False))
            self.last_write_time = now

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
        
        # 🚀 [新增] 计量修复与 Token 即时速率计算
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
