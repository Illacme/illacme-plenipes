#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Governance - Heartbeat Telemetry & Archive Shard
模块职责：时序性能遥测管理、冷启动历史继承、动态采样扩缩容与长效归档持久化缓冲。
🛡️ [SOP-01 & SOP-02]：从 heartbeat.py 物理拆解出的遥测与归档能力 Mixin。
"""

import json
import os
from core.utils.tracing import tlog


class TelemetryArchiveMixin:
    """心跳服务的时序指标与归档缓冲区治理 Mixin"""

    def init_telemetry_state(self, config, pulse_path: str):
        """初始化遥测与长效归档配置与冷启动继承"""
        sys_limit = 150
        if config and hasattr(config, "system"):
            sys_limit = getattr(config.system, "telemetry_history_limit", 150)
            
        self.history_limit = sys_limit
        self.history_cpu = [0.0] * self.history_limit
        self.history_mem = [0.0] * self.history_limit
        self.history_comp = [0.0] * self.history_limit
        self.history_tokens_rate = [0.0] * self.history_limit
        self.history_active_workers = [0.0] * self.history_limit

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

        self._restore_telemetry_from_file(pulse_path)

    def _restore_telemetry_from_file(self, pulse_path: str):
        """冷启动物理加载恢复：若存在 pulse.json，继承其历史轨迹以防断崖"""
        if not os.path.exists(pulse_path):
            return
        try:
            with open(pulse_path, 'r', encoding='utf-8') as f:
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

    def adapt_telemetry_limits(self, config):
        """动态负载历史点数上限热加载与内存历史数据自适应缩放"""
        if not (config and hasattr(config, "system")):
            return
            
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

    def process_archive_tick(self) -> bool:
        """累加最新采样点至归档缓冲区并在到达周期时固化归档。返回是否需要强制落盘"""
        self.archive_buffer_cpu.append(self.history_cpu[-1] if self.history_cpu else 0.0)
        self.archive_buffer_mem.append(self.history_mem[-1] if self.history_mem else 0.0)
        self.archive_buffer_comp.append(self.history_comp[-1] if self.history_comp else 0.0)
        self.archive_buffer_tokens.append(self.history_tokens_rate[-1] if self.history_tokens_rate else 0.0)
        self.archive_buffer_workers.append(self.history_active_workers[-1] if self.history_active_workers else 0.0)
        
        self.tick_counter += 1
        ticks_needed = max(1, int(self.archive_interval_seconds / self.interval))
        
        if self.tick_counter >= ticks_needed:
            def calc_avg(lst):
                return sum(lst) / len(lst) if lst else 0.0
                
            self.history_archive_cpu.append(calc_avg(self.archive_buffer_cpu))
            self.history_archive_mem.append(calc_avg(self.archive_buffer_mem))
            self.history_archive_comp.append(calc_avg(self.archive_buffer_comp))
            self.history_archive_tokens_rate.append(calc_avg(self.archive_buffer_tokens))
            self.history_archive_active_workers.append(calc_avg(self.archive_buffer_workers))
            
            if len(self.history_archive_cpu) > self.history_archive_limit:
                self.history_archive_cpu.pop(0)
                self.history_archive_mem.pop(0)
                self.history_archive_comp.pop(0)
                self.history_archive_tokens_rate.pop(0)
                self.history_archive_active_workers.pop(0)
                
            self.archive_buffer_cpu.clear()
            self.archive_buffer_mem.clear()
            self.archive_buffer_comp.clear()
            self.archive_buffer_tokens.clear()
            self.archive_buffer_workers.clear()
            self.tick_counter = 0
            return True
            
        return False
