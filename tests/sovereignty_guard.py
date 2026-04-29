#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes - Sovereignty Guard (主权治理烟雾测试)
用于验证核心治理红线（如 NoneType 免疫、逻辑剪枝保护）在物理代码层面的有效性。
"""
import sys
import os
import unittest

# 确保能导入 core 包
sys.path.append(os.getcwd())

from core.utils.tracing import Tracer, tlog
from core.logic.ai.model_intelligence import ModelIntelligenceHub

class TestSovereigntyGuard(unittest.TestCase):
    def setUp(self):
        """🚀 [V16.8] 确保所有自检函数均带有 test- 标识"""
        Tracer.set_id("SelfCheck")

    def tearDown(self):
        """🛡️ 物理清理：防止测试 ID 污染主进程上下文"""
        Tracer.set_id(None)

    def test_tracing_isolation_and_metadata(self):
        """验证全链路追踪的隔离性与元数据注入功能"""
        Tracer.add_metadata("reasoning", "thinking...")
        
        self.assertEqual(Tracer.get_id(), "SelfCheck")
        self.assertEqual(Tracer.get_metadata().get("reasoning"), "thinking...")
        tlog.debug("  └── [Pass] 全链路追踪与元数据注入正常。")

    def test_model_intelligence_resilience(self):
        """验证模型智能中枢的健康分自愈机制"""
        hub = ModelIntelligenceHub()
        node = "test-node-001"
        
        # 初始分 100
        self.assertEqual(hub.get_health_score(node), 100)
        
        # 记录失败
        hub.record_failure(node, reason="[自检] 模拟 API 超时")
        self.assertEqual(hub.get_health_score(node), 80)
        
        # 记录成功自愈
        hub.record_success(node, reason="[自检] 恢复心跳")
        self.assertEqual(hub.get_health_score(node), 81)
        tlog.debug("  └── [Pass] 节点健康分监测与惩罚机制正常。")

    def test_sovereign_core_decoration(self):
        """验证主权核心装饰器是否正确标记了关键方法"""
        from core.runtime.engine import IllacmeEngine
        # sync_document 应该是主权核心
        self.assertTrue(getattr(IllacmeEngine.sync_document, '_is_sovereign_core', False))
        tlog.debug("  └── [Pass] 主权核心逻辑标记验证通过。")

    def test_logic_integrity_audit(self):
        """物理审计：确保核心文件未被 AI 逻辑剪枝 (Logic Pruning Detection)"""
        core_files = [
            "core/bindery_dispatcher.py",
            "core/logic/strategies/fingerprint.py"
        ]
        # 锚点检查：必须存在的关键逻辑字符串
        anchors = {
            "core/bindery_dispatcher.py": ["sanitize_ai_response", "unmasker.unmask", "Tracer.get_id"],
            "core/logic/strategies/fingerprint.py": ["priority = TaskPriority", "AIScheduler.dispatch_targets"]
        }
        
        for file_path in core_files:
            abs_path = os.path.join(os.getcwd(), file_path)
            if not os.path.exists(abs_path): continue
            
            with open(abs_path, 'r', encoding='utf-8') as f:
                content = f.read()
                for anchor in anchors.get(file_path, []):
                    self.assertIn(anchor, content, f"🛑 [逻辑剪枝风险] 文件 {file_path} 中缺失关键锚点: {anchor}")
        tlog.debug("  └── [Pass] 核心逻辑完整性物理审计通过。")

    def test_nonetype_resilience_audit(self):
        """验证系统对 NoneType 的免疫力"""
        from core.bindery.bindery_dispatcher import BinderyDispatcher
        # 模拟 dispatcher
        try:
            # 即使传入 None，也不会抛出 AttributeError
            from unittest.mock import MagicMock
            dispatcher = BinderyDispatcher({}, {}, MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock(), [], "", MagicMock())
            # 这是一个简单的结构检查，确保逻辑中包含 or "" 或类似保护
            import inspect
            source = inspect.getsource(dispatcher.dispatch)
            self.assertIn("masked_body or \"\"", source)
            tlog.debug("  └── [Pass] NoneType 免疫逻辑存在。")
        except Exception as e:
            self.fail(f"NoneType 审计异常: {e}")

if __name__ == "__main__":
    tlog.debug("🚀 [Sovereignty Guard] 正在执行治理主权烟雾测试...")
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
