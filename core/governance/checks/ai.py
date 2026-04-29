# -*- coding: utf-8 -*-
import time
from typing import Dict, Any

class AIChecker:
    """🚀 [V24.6] AI 算力网关诊断器"""
    
    @staticmethod
    def check(engine) -> Dict[str, Any]:
        """AI 算力节点审计"""
        res = {"name": "AI Gateway", "status": "PASS", "details": []}

        if engine.no_ai:
            res.get('details').append("ℹ️ 当前处于 NO-AI 模式，跳过检查。")
            return res

        translator = engine.translator
        nodes_to_test = []

        if hasattr(translator, 'primary') and hasattr(translator, 'secondary'):
            nodes_to_test = [("Primary", translator.primary), ("Secondary", translator.secondary)]
        else:
            nodes_to_test = [("Active", translator)]

        for label, node in nodes_to_test:
            try:
                start = time.time()
                if hasattr(node, 'ping'):
                    alive = node.ping()
                    latency = (time.time() - start) * 1000
                    if alive:
                        res.get('details').append(f"✅ {label} 节点 ({node.node_name}) 在线 (响应耗时: {latency:.1f}ms)")
                    else:
                        res['status'] = "FAIL"
                        res.get('details').append(f"❌ {label} 节点 ({node.node_name}) 响应异常 (Ping Failed)")
                else:
                    res_slug, ok = node.generate_slug("Health Check", is_dry_run=False)
                    if ok:
                        res.get('details').append(f"✅ {label} 节点 ({node.node_name}) 功能验证通过")
                    else:
                        res['status'] = "WARN"
                        res.get('details').append(f"⚠️ {label} 节点 ({node.node_name}) 功能受限 (Slug Generator Failed)")
            except Exception as e:
                res['status'] = "FAIL"
                res.get('details').append(f"❌ {label} 节点诊断崩溃: {e}")

        return res
