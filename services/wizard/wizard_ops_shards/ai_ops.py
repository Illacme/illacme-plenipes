#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧙‍♂️ ai_ops.py - 远程/本地 LLM 算力供应商模型的动态拉取与高频网络连接的健壮性诊断
"""

from core.adapters.ai.registry import AIProviderRegistry
from core.logic.diagnostics import DiagnosticsService

async def get_ai_models_logic(req):
    p_cls = AIProviderRegistry.get_provider(req.provider)
    if not p_cls: return {"models": []}
    try:
        url = req.base_url or getattr(p_cls, "DEFAULT_URL", "")
        n_cfg = type('N', (), {'base_url': url, 'api_key': req.api_key, 'type': req.provider,
                               'limits': type('L', (), {'max_concurrency': 1, 'timeout': 10})()})()
        cfg = type('D', (), {'base_url': url, 'api_key': req.api_key, 'model': req.model, 'api_timeout': 10,
                             'compute_nodes': {'w': n_cfg}})()
        t = p_cls("w", cfg)
        return {"models": await t.list_models()}
    except Exception as e:
        err_str = str(e)
        return {"models": [], "error": f"原始提示: {err_str}"}

async def validate_ai_logic(req):
    return await DiagnosticsService.validate_ai_connectivity(req.provider, req.model, req.api_key, req.base_url)
