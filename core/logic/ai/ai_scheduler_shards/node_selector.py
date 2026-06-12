# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - AI Scheduler Shards - Node Selector
职责：算力路由寻址与智能最优节点决选原子 Shard
🛡️ [AEL-Iter-v10.3]：完美恢复路由决选智能算子
"""
from core.utils.tracing import tlog

class AISchedulerNodeSelector:
    @staticmethod
    def get_best_translator(engine, preferred_node: str = None):
        """🚀 [V11.1] 调度收敛：全局绝对服从配置的翻译策略 (不再越权智能路由)"""
        # 如果当前策略是 global_smart，引擎加载的 translator 是 GlobalSmartRoutingStrategy，每次会内部动态决选。
        # 如果是 single 或 fallback，则绝对尊重用户的物理控制。
        return engine.translator
