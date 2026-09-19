# -*- coding: utf-8 -*-
"""
⚡ [V66.5] Compute Node Probe & Model Discovery Operations Shard
职责：负责算力环境嗅探、网络连通性测试与动态模型发现。
"""

import time
from typing import Dict, Any
from types import SimpleNamespace
from core.utils.tracing import tlog


def _get_engine():
    """获取全局引擎实例，优先兼容外部对主模块的动态 patch / mock"""
    try:
        import services.api.routes.compute as parent_mod
        if hasattr(parent_mod, "get_global_engine"):
            return parent_mod.get_global_engine()
    except Exception:
        pass
    from core.runtime.engine_singleton import get_global_engine
    return get_global_engine()


def probe_compute_logic() -> Dict[str, Any]:
    """🚀 [V76.0] 实时嗅探本地算力（LM Studio / Ollama）与本地凭据环境"""
    from core.logic.diagnostics import DiagnosticsService
    from services.wizard.wizard_ops_shards.probe_ops import probe_local_github_credential
    
    local_nodes = DiagnosticsService.probe_local_compute()
    github_cred = probe_local_github_credential()
    
    return {
        "local_nodes": local_nodes,
        "github": github_cred,
        "has_local_compute": len(local_nodes) > 0,
        "recommended_provider": local_nodes[0]["provider"] if local_nodes else "deepseek"
    }


async def test_node_connectivity_logic(req: dict) -> Dict[str, Any]:
    """执行算力节点连通性物理探针"""
    engine = _get_engine()
    if not engine:
        return {"error": "Engine not initialized"}
    
    node_id = req.get("id")
    if not node_id:
        return {"error": "Missing node id"}
    
    # 🚀 [V66.5] 支持实时配置覆盖测试
    from core.config.models.ai import TranslationSettings
    config_override = req.get("config")
    if config_override:
        try:
            trans_cfg = TranslationSettings(**config_override)
            tlog.info(f"⚡ [算力探测] 正在对节点 '{node_id}' 发起 [实时动态] 连通性测试...")
        except Exception as e:
            tlog.error(f"🛑 [探测预检失败] 动态配置格式错误: {e}")
            return {"status": "error", "error": f"Invalid config: {e}"}
    else:
        trans_cfg = engine.config.translation
        tlog.info(f"⚡ [算力探测] 正在对节点 '{node_id}' 发起 [持久化] 连通性测试...")
    
    start_time = time.time()
    try:
        from core.logic.ai.ai_factory import TranslatorFactory
        translator = TranslatorFactory._build_node(node_id, trans_cfg)
        
        success, message = await translator.test_connection()
        latency = int((time.time() - start_time) * 1000)
        
        if success:
            tlog.success(f"✅ [探测成功] 节点 '{node_id}' 正常，延迟: {latency}ms")
            return {"status": "success", "latency": latency, "message": message}
        else:
            return {"status": "failed", "error": message}
            
    except Exception as e:
        tlog.error(f"🛑 [探测异常] 节点 '{node_id}' 响应异常: {e}")
        return {"status": "error", "error": str(e)}


async def get_node_models_logic(node_id: str, provider: str = None, api_key: str = None, base_url: str = None, proxy: str = None) -> Dict[str, Any]:
    """🚀 [V66.5] 动态模型发现：实时从算力节点获取可用模型列表"""
    from core.adapters.ai.registry import AIProviderRegistry
    
    engine = _get_engine()
    target_provider = provider
    target_key = api_key
    target_url = base_url
    target_proxy = proxy
    
    if engine and hasattr(engine, "config") and hasattr(engine.config, "translation"):
        compute_nodes = getattr(engine.config.translation, "compute_nodes", {})
        if node_id in compute_nodes:
            node_cfg = compute_nodes[node_id]
            target_provider = target_provider or getattr(node_cfg, "type", None)
            target_key = target_key or getattr(node_cfg, "api_key", None)
            target_url = target_url or getattr(node_cfg, "base_url", None)
            target_proxy = target_proxy or getattr(node_cfg, "proxy", None)
        if not target_proxy and hasattr(engine.config, "system"):
            target_proxy = getattr(engine.config.system, "global_proxy", None)
        
    if not target_provider:
        return {"models": []}
    p_cls = AIProviderRegistry.get_provider(target_provider)
    if not p_cls:
        return {"models": []}
    
    try:
        target_url = target_url or getattr(p_cls, "DEFAULT_URL", "")
        mock_limits = SimpleNamespace(max_concurrency=1, timeout=20)
        mock_node = SimpleNamespace(
            base_url=target_url,
            api_key=target_key,
            type=target_provider,
            limits=mock_limits,
            proxy=target_proxy
        )
        
        mock_config = SimpleNamespace(
            base_url=target_url,
            api_key=target_key,
            model="discovery",
            api_timeout=20,
            max_retries=1,
            global_proxy=target_proxy,
            compute_nodes={node_id: mock_node}
        )
        
        translator = p_cls(node_id, mock_config)
        models = await translator.list_models()
        return {"models": models}
    except Exception as e:
        tlog.warning(f"⚠️ [模型发现失败] 节点 '{node_id}' ({target_provider}): {e}")
        error_msg = str(e)
        try:
            if "translator" in locals() and translator:
                error_msg = translator.diagnose_error(e)
            else:
                from core.adapters.ai.base import BaseTranslator
                class TempTranslator(BaseTranslator):
                    def _ask_ai(self, payload):
                        return ""
                temp_node = SimpleNamespace(api_key=target_key)
                temp_cfg = SimpleNamespace(compute_nodes={node_id: temp_node})
                temp_trans = TempTranslator(node_id, temp_cfg)
                error_msg = temp_trans.diagnose_error(e)
        except Exception as diag_err:
            tlog.error(f"🛑 [诊断器自身异常] {diag_err}")
            error_msg = f"连接异常: {str(e)[:80]}..." if len(str(e)) > 80 else f"连接异常: {str(e)}"
        return {"models": [], "error": error_msg}
