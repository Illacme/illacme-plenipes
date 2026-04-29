#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Usage Meter (算力计量器)
模块职责：全链路算力消耗追踪、成本核算与 TCG 熔断控制。
🛡️ [V23.0 Pure SQLite]：基于数据库的计费引擎，完全摒弃 JSON 冗余。
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
        if self._initialized:
            return
        self.engine = engine
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
        """内部记账逻辑：记录单次 API 消耗"""
        with self.lock:
            # 1. 累加 Token
            self.stats.get('session')['input_tokens'] += input_tokens
            self.stats.get('session')['output_tokens'] += output_tokens

            # 2. 计算费用
            input_price = getattr(provider_config, 'price_per_1m_input', 0.0)
            output_price = getattr(provider_config, 'price_per_1m_output', 0.0)
            
            # 🛡️ [V24.6] 零值保护：本地节点强制免费，防止计费误报
            if any(keyword in node_name.lower() for keyword in ["local", "lmstudio", "ollama"]):
                input_price, output_price = 0.0, 0.0

            cost = (input_tokens / 1_000_000 * input_price) + (output_tokens / 1_000_000 * output_price)
            self.stats.get('session')['cost'] += cost

            # 🚀 [V23.0] 数据库持久化：将费用记入 usage_ledger 表
            workspace_id = getattr(self.engine, 'workspace_id', 'default')
            self.engine.meta.sqlite.insert_usage_record(
                workspace_id=workspace_id,
                event_type="AI_TRANSACTION",
                description=f"AI 调用: {node_name} ({input_tokens}+{output_tokens})",
                cost=cost,
                metadata={
                    "node": node_name,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens
                }
            )

            # 3. 检查熔断 (TCG Guard)
            budget = self.engine.config.translation.budget_limit if self.engine and self.engine.config else 0.0
            if budget > 0 and self.stats.get('session').get('cost') > budget:
                tlog.critical(f"🛑 [TCG 熔断] 算力超支！当前 Session 消耗 {self.stats.get('session').get('cost'):.4f} 已超过预算 {budget:.4f}")
                raise RuntimeError("USAGE_BUDGET_EXCEEDED")

    def _record_savings(self, saved_tokens: int, node_name: str, provider_config: Any):
        """内部记账逻辑：记录缓存节省额度"""
        with self.lock:
            self.stats.get('session')['saved_tokens'] += saved_tokens
            input_price = getattr(provider_config, 'price_per_1m_input', 0.0)
            saved_value = (saved_tokens / 1_000_000 * input_price)
            self.stats.get('session')['saved_value'] += saved_value

    def persist(self):
        """
        🚀 [V23.0] 持久化：由于已实现行级实时写入，此处仅负责同步仪表盘指标
        """
        self._update_dashboard_stats()

    def _update_dashboard_stats(self):
        """更新用于 Dashboard 展示的统计数据 (可选)"""
        # 实际全量数据可通过 engine.meta.sqlite.get_total_cost() 实时查询
        pass

    def get_summary_report(self) -> Dict[str, Any]:
        """获取摘要报告"""
        with self.lock:
            # 🚀 [V23.0] 深度合并：从数据库获取历史总额
            report = self.stats.get('session').copy()
            workspace_id = getattr(self.engine, 'workspace_id', 'default')
            report["total_historical_cost"] = self.engine.meta.sqlite.get_total_cost(workspace_id)
            return report

    def check_and_block(self, content: str, targets: list, rel_path: str) -> bool:
        """🚀 [V24.6] 预算预检接口 (接管已废弃的 CostGuard)"""
        budget = self.engine.config.translation.budget_limit if self.engine and self.engine.config else 0.0
        if budget <= 0: return True # 无预算限制
        
        # 1. 汇总当前总消耗 (今日已耗 + 本次 Session 已耗)
        workspace_id = getattr(self.engine, 'workspace_id', 'default')
        today_cost = self.engine.meta.sqlite.get_total_cost(workspace_id) # get_total_cost 内部应包含日期筛选逻辑
        session_cost = self.stats.get('session').get('cost', 0.0)
        total_spent = today_cost + session_cost
        
        if total_spent >= budget:
            tlog.error(f"🛑 [算力熔断] 任务 {rel_path} 被拦截。今日总预算 {budget:.2f} 已耗尽 (已用: {total_spent:.2f})。")
            return False
            
        return True
