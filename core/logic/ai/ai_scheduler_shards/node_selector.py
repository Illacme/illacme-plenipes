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
        """🚀 [V11.0] 智能节点选择：利用 SmartRouter 决定最优算力去向"""
        if not hasattr(engine, 'smart_router'):
            from core.logic.smart_router import SmartRouter
            engine.smart_router = SmartRouter(engine)
        
        # 如果未指定首选节点，则从当前翻译器获取
        if not preferred_node:
            preferred_node = engine.translator.node_name

        best_node_name = engine.smart_router.get_best_node(preferred_node)
        
        # 如果路由器建议了不同节点，则通过工厂创建/获取
        if best_node_name != engine.translator.node_name:
            from core.logic.ai.ai_factory import TranslatorFactory
            # 注意：此处需要访问 trans_cfg，通常在 engine.config.translation
            return TranslatorFactory.create_node(best_node_name, engine.config.translation)
        
        return engine.translator
