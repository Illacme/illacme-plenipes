#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Doctor Service
模块职责：全域主权诊断中心（编排器）。
🛡️ [V48.3 Refactored]：基于委托模式的轻量化诊断中枢，严格对齐 300 行红线。
"""

import time
from typing import Dict, List, Any
from core.utils.tracing import tlog

# 🚀 [V48.3] 导入模块化后的检查器
from .checks.infra import InfraChecker
from .checks.ledger import LedgerChecker
from .checks.ai import AIChecker
from .checks.plugins import PluginChecker
from .checks.matrix import MatrixChecker
from .healer import CodeHealer

class DoctorService:
    """🚀 [V48.3] 诊断编排器：职责分离，逻辑外挂"""
    
    def __init__(self, engine):
        self.engine = engine

    def run_full_check(self) -> Dict[str, Any]:
        """执行全链路深度体检 (编排逻辑)"""
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "status": "PASS",
            "checks": []
        }

        # 1. 物理基础设施
        report["checks"].append(InfraChecker.check(self.engine.paths))

        # 2. 账本一致性
        report["checks"].append(LedgerChecker.check(self.engine))

        # 3. 渲染矩阵
        report["checks"].append(PluginChecker.check_rendering(self.engine))

        # 4. AI 算力网关
        report["checks"].append(AIChecker.check(self.engine))

        # 5. 契约守卫审计
        report["checks"].append(PluginChecker.check_contracts())

        # 6. 多语言与 SEO 矩阵
        report["checks"].append(MatrixChecker.check_i18n(self.engine.config))

        # 7. 可观测性审计
        report["checks"].append(MatrixChecker.check_observability())

        # 汇总状态判断
        self._summarize_status(report)
        return report

    def _summarize_status(self, report: Dict[str, Any]):
        """内部状态汇总逻辑"""
        statuses = [c.get('status') for c in report.get('checks', [])]
        if "FAIL" in statuses:
            report['status'] = "FAIL"
        elif "WARN" in statuses:
            report['status'] = "WARN"

    def heal(self) -> List[str]:
        """执行自愈手术"""
        from core.governance.autopilot import Autopilot
        return Autopilot.perform_safe_surgery(self.engine)

    def _auto_heal_loggers(self) -> List[str]:
        """委托给专门的 Healer 处理 (兼容旧版调用)"""
        return CodeHealer.auto_heal_loggers()
