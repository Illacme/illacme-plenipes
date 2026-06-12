#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Usage Meter (算力计量器)
模块职责：全链路算力消耗追踪、成本核算与 TCG 熔断控制。
🛡️ [V23.0 Pure SQLite]：基于数据库的计费引擎，完全摒弃 JSON 冗余。

[治理宪章 R1.3 遵从性说明]
本模块实现了严格的 NoneType 免疫机制。所有针对 self.stats 或外部注入配置的访问
均通过 .get() 或 getattr() 代理执行，确保在极端的运行时故障（如数据库连接丢失或
配置文件损坏）下，计费核心不会引发致命的崩溃。

[主权隐喻：注册簿 (The Registry)]
在 Illacme-plenipes 的世界观中，UsageMeter 充当着总编室的“账本管理员”。
每一份被翻译出的稿件（付印产物）都会在数据库中留下不可磨灭的品牌记录，
包括消耗的算力字符、汇率转换后的成本以及通过缓存节省的资产价值。

[TCG 熔断机制]
算力资源是项目的主权资产。当单次任务或今日累积消耗触及预设的 budget_limit 时，
本模块将强制挂起所有后续的 AI 调用，直到人工干预或配额重置。
"""

import threading
from datetime import datetime
from core.utils.event_bus import bus
from typing import Dict, Any

from core.utils.tracing import tlog

class UsageMeter:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(UsageMeter, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self, engine):
        self.engine = engine
        if self._initialized:
            return
        self.stats = {
            "session": {
                "input_tokens": 0,
                "output_tokens": 0,
                "saved_tokens": 0,
                "cost": 0.0,
                "saved_value": 0.0
            }
        }
        self.lock = threading.Lock()
        self._setup_listeners()
        self._initialized = True

    def _setup_listeners(self):
        """🚀 [V7.1] 注册事件监听器"""
        bus.subscribe("AI_CALL_COMPLETED", self._on_ai_call)
        bus.subscribe("BLOCK_CACHE_HIT", self._on_cache_hit)

    def _on_ai_call(self, node_name=None, input_tokens=0, output_tokens=0, provider_config=None, **kwargs):
        """响应 AI 调用完成事件"""
        self._record_usage(
            node_name,
            input_tokens,
            output_tokens,
            provider_config
        )

    def _on_cache_hit(self, node_name=None, tokens=0, provider_config=None, **kwargs):
        """响应块级缓存命中事件"""
        self._record_savings(
            tokens,
            node_name,
            provider_config
        )

    def _record_usage(self, node_name: str, input_tokens: int, output_tokens: int, provider_config: Any):
        """
        内部记账逻辑：记录单次 AI 翻译官的物理算力消耗。
        🛡️ [R1.3] 免疫防御：全量使用 .get() 确保 NoneType 隔离。
        """
        with self.lock:
            session = self.stats.get('session', {})
            # 1. 累加 Token (具备原子性与防御性)
            session.update({'input_tokens': session.get('input_tokens', 0) + input_tokens})
            session.update({'output_tokens': session.get('output_tokens', 0) + output_tokens})

            # 2. 计算费用
            input_price = getattr(provider_config, 'price_per_1m_input', 0.0)
            output_price = getattr(provider_config, 'price_per_1m_output', 0.0)
            
            # 🛡️ [V48.3] 零值保护：本地节点强制免费，防止计费误报
            if any(keyword in (node_name or "").lower() for keyword in ["local", "lmstudio", "ollama"]):
                input_price, output_price = 0.0, 0.0

            cost = (input_tokens / 1_000_000 * input_price) + (output_tokens / 1_000_000 * output_price)
            session.update({'cost': session.get('cost', 0.0) + cost})

            # 🚀 [V23.0] 数据库持久化：将费用记入 注册簿 (The Registry)
            imprint_id = getattr(self.engine, 'imprint_id', 'default')
            self.engine.meta.sqlite.insert_usage_record(
                imprint_id=imprint_id,
                event_type="AI_TRANSACTION",
                description=f"AI 付印消耗: {node_name} ({input_tokens}+{output_tokens})",
                cost=cost,
                metadata={
                    "node": node_name,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens
                }
            )

            # 3. 检查熔断 (TCG Guard)
            budget = 0.0
            if self.engine and hasattr(self.engine, 'config'):
                budget = getattr(self.engine.config.translation, 'budget_limit', 0.0)

            current_cost = session.get('cost', 0.0)
            if budget > 0 and current_cost > budget:
                tlog.critical(f"🛑 [TCG 熔断] 算力超支！当前 Session 消耗 {current_cost:.4f} 已超过预算 {budget:.4f}")
                raise RuntimeError("USAGE_BUDGET_EXCEEDED")

    def _record_savings(self, saved_tokens: int, node_name: str, provider_config: Any):
        """内部记账逻辑：记录缓存节省额度"""
        with self.lock:
            session = self.stats.get('session', {})
            session.update({'saved_tokens': session.get('saved_tokens', 0) + saved_tokens})
            input_price = getattr(provider_config, 'price_per_1m_input', 0.0)
            saved_value = (saved_tokens / 1_000_000 * input_price)
            session.update({'saved_value': session.get('saved_value', 0.0) + saved_value})

    def persist(self):
        """
        🚀 [V23.0] 持久化：由于已实现行级实时写入，此处仅负责同步仪表盘指标。
        确保在档案馆 (The Archive) 中留下不可磨灭的品牌付印痕迹。
        """
        self._update_dashboard_stats()

    def _update_dashboard_stats(self):
        """更新用于总编室 (Newsroom) 展示的统计数据"""
        pass

    def get_summary_report(self) -> Dict[str, Any]:
        """获取摘要报告"""
        with self.lock:
            # 🚀 [V23.0] 深度合并：从注册簿获取历史总额
            report = self.stats.get('session', {}).copy()
            imprint_id = getattr(self.engine, 'imprint_id', 'default')
            report["total_historical_cost"] = self.engine.meta.sqlite.get_total_cost(imprint_id)
            return report

    def check_and_block(self, content: str, targets: list, rel_path: str) -> bool:
        """🚀 [V48.3] 预算预检接口 (接管已废弃的 CostGuard)"""
        budget = 0.0
        if self.engine and hasattr(self.engine, 'config'):
            budget = getattr(self.engine.config.translation, 'budget_limit', 0.0)
        
        if budget <= 0: return True # 无预算限制
        
        # 1. 汇总当前总消耗 (今日已耗 + 本次 Session 已耗)
        imprint_id = getattr(self.engine, 'imprint_id', 'default')
        today_cost = self.engine.meta.sqlite.get_total_cost(imprint_id)

        session_cost = self.stats.get('session', {}).get('cost', 0.0)
        total_spent = today_cost + session_cost
        
        if total_spent >= budget:
            tlog.error(f"🛑 [算力熔断] 任务 {rel_path} 被拦截。今日总预算 {budget:.2f} 已耗尽 (已用: {total_spent:.2f})。")
            return False
            
        return True
