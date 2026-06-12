"""
🤖 AI 校验模块 — 人工智能服务可用性与配额检查。
验证 AI 翻译/摘要服务的连通性、Token 配额与模型可用性。
"""
# -*- coding: utf-8 -*-
import time
import asyncio
from typing import Dict, Any
from concurrent.futures import ThreadPoolExecutor

def run_sync(coro):
    """安全地在同步上下文中执行异步协程"""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            with ThreadPoolExecutor(max_workers=1) as pool:
                return pool.submit(lambda: asyncio.run(coro)).result()
        else:
            return loop.run_until_complete(coro)
    except RuntimeError:
        return asyncio.run(coro)

class AIChecker:
    """🚀 [V48.3] AI 算力网关诊断器"""
    
    @staticmethod
    def check(engine) -> Dict[str, Any]:
        """AI 算力节点审计"""
        res = {"name": "AI Gateway", "status": "PASS", "details": []}

        # 🚀 [V74.98] 算力总控前置防御：若 AI 关闭，跳过可用性诊断
        if engine.no_ai or not getattr(engine.config.translation, 'enable_ai', True):
            res.get('details').append("ℹ️ AI 算力总控已关闭，跳过检查。")
            return res

        translator = engine.translator
        if not translator:
            res['status'] = "FAIL"
            res.get('details').append("❌ 未检测到可用的 AI 翻译器对象")
            return res

        nodes_to_test = []
        if hasattr(translator, 'primary') and hasattr(translator, 'secondary'):
            nodes_to_test = [("Primary", translator.primary), ("Secondary", translator.secondary)]
        else:
            nodes_to_test = [("Active", translator)]

        node_statuses = {}
        for label, node in nodes_to_test:
            if not node:
                node_statuses[label] = "FAIL"
                res.get('details').append(f"❌ {label} 节点未配置或不存在")
                continue
            try:
                start = time.time()
                # 优先使用 BaseTranslator 原生的 test_connection 连通性物理探针
                if hasattr(node, 'test_connection'):
                    success, message = run_sync(node.test_connection())
                    latency = (time.time() - start) * 1000
                    if success:
                        res.get('details').append(f"✅ {label} 节点 ({node.node_name}) 在线 (响应耗时: {latency:.1f}ms): {message}")
                        node_statuses[label] = "PASS"
                    else:
                        res.get('details').append(f"❌ {label} 节点 ({node.node_name}) 响应异常: {message}")
                        node_statuses[label] = "FAIL"
                elif hasattr(node, 'ping'):
                    alive = node.ping()
                    latency = (time.time() - start) * 1000
                    if alive:
                        res.get('details').append(f"✅ {label} 节点 ({node.node_name}) 在线 (响应耗时: {latency:.1f}ms)")
                        node_statuses[label] = "PASS"
                    else:
                        res.get('details').append(f"❌ {label} 节点 ({node.node_name}) 响应异常 (Ping Failed)")
                        node_statuses[label] = "FAIL"
                else:
                    res_slug, ok = node.generate_slug("Health Check", is_dry_run=False)
                    if ok:
                        res.get('details').append(f"✅ {label} 节点 ({node.node_name}) 功能验证通过")
                        node_statuses[label] = "PASS"
                    else:
                        res.get('details').append(f"❌ {label} 节点 ({node.node_name}) 功能异常 (Slug Generator Failed)")
                        node_statuses[label] = "FAIL"
            except Exception as e:
                res.get('details').append(f"❌ {label} 节点诊断崩溃: {e}")
                node_statuses[label] = "FAIL"

        if not nodes_to_test:
            res['status'] = "FAIL"
            res.get('details').append("❌ 未检测到任何可用的 AI 算力节点配置")
        else:
            fails = [l for l, s in node_statuses.items() if s == "FAIL"]
            if len(fails) == len(nodes_to_test):
                res['status'] = "FAIL"
            elif len(fails) > 0:
                res['status'] = "WARN"
            else:
                res['status'] = "PASS"

        return res


def check_ai_availability_or_raise(engine):
    """🛡️ [V76.8] 翻译矩阵与算力可用性强关联校验熔断门禁"""
    # 🚀 [V74.98] 算力总控前置防御：只有在 AI 开启时，才执行强关联检验，防止物理透传时虚假熔断
    if getattr(engine.config.translation, 'enable_ai', True):
        i18n = engine.config.i18n_settings
        if i18n and i18n.enabled and i18n.targets:
            if engine.no_ai:
                raise RuntimeError("翻译矩阵已开启，但系统当前处于 NO-AI 模式，无法启动发布！")
            
            ai_report = AIChecker.check(engine)
            if ai_report.get("status") == "FAIL":
                err_msg = "、".join(ai_report.get("details", []))
                raise RuntimeError(f"翻译矩阵已开启，但 AI 算力网关诊断失败: {err_msg}")

