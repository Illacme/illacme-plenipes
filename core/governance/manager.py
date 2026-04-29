#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omni-Hub Governance Manager
职责：协调所有自主治理组件（哨兵、医生、审计、熔断等）。
"""

from core.utils.tracing import tlog

class GovernanceManager:
    """🚀 [V15.1] 自主治理中枢：引擎的主权守卫者"""
    
    def __init__(self, engine):
        self.engine = engine
        
        # 1. 核心财务审计 (SQLite)
        from core.governance.audit_ledger import ledger
        from core.governance.meter import UsageMeter
        self.ledger = ledger
        self.meter = UsageMeter(engine)
        
        # 2. 物理主权监控 (Sentinel & Guards)
        from core.governance.indexing_sentinel import IndexingSentinel
        from core.governance.resource_guard import ResourceGuard
        from core.governance.heartbeat import HeartbeatService
        from core.governance.qa_guard import QAGuard
        from core.governance.sentinel import SentinelManager
        
        self.indexing_sentinel = IndexingSentinel(engine)
        self.resource_guard = ResourceGuard(engine)
        self.heartbeat = HeartbeatService(engine)
        self.qa_guard = QAGuard(engine)
        self.health_sentinel = SentinelManager(engine.config, engine=engine)
        
        # 3. 挂载向量索引 (V24.6 工业单例)
        from core.governance.vector_index import VectorIndex
        data_paths = engine.config.system.data_paths
        v_path = engine._resolve_path(data_paths.get("vectors_json", "vectors.json"))
        self.vector_index = VectorIndex(v_path)
        
        # 🚀 [V24.6] 启动后台治理服务
        self.indexing_sentinel.start()
        self.resource_guard.start()
        self.heartbeat.start()
        
        tlog.info("🛡️ [GovernanceManager] 自主治理大一统中枢已就位，所有守卫已上线。")

    def shutdown(self):
        """安全释放所有治理资源"""
        self.indexing_sentinel.stop()
        self.resource_guard.stop()
        self.heartbeat.stop()
        tlog.info("🛡️ [GovernanceManager] 治理资源已安全回收。")
