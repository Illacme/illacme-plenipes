#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes AI Plugin - LMStudio Native Adapter
职责：负责 LMStudio 原生 v1 协议的深度适配。
🛡️ [V15.9] 原生主权：支持模型状态感知与动态加载逻辑。
"""
from typing import Dict, Any
from .openai import OpenAICompatibleTranslator
from core.utils.tracing import tlog

class LMStudioNativeTranslator(OpenAICompatibleTranslator):
    """🚀 [V15.9] LMStudio 原生协议适配器 (v1)"""
    PLUGIN_ID = 'lmstudio'
    
    def __init__(self, node_name, trans_cfg):
        # 🚀 LMStudio v1 原生基准地址
        if not trans_cfg.base_url:
            trans_cfg.base_url = "http://localhost:1234/api/v1"
        super().__init__(node_name, trans_cfg)
        self._is_ready = False

    def _check_model_health(self, model_name: str) -> bool:
        """[Native] 拨测 LMStudio 模型加载状态"""
        try:
            url = f"{self.trans_cfg.base_url}/models"
            resp = self._session.get(url, timeout=2)
            if resp.status_code == 200:
                models = resp.json().get('data', [])
                # 检查目标模型是否已在内存中
                loaded = any(m.get('id') == model_name for m in models)
                if not loaded:
                    tlog.warning(f"⚠️ [LMStudio] 模型 {model_name} 尚未加载，请在 LMStudio 中点击 Load 或通过 API 加载")
                return loaded
        except Exception as e:
            tlog.debug(f"❌ [LMStudio] 健康检查失败: {e}")
        return False

    def _ask_ai(self, payload: Dict[str, Any]) -> str:
        """[Native] 执行原生 v1 推理"""
        model_name = payload.get("model")
        
        # 🚀 第一次请求时进行健康检查
        if not self._is_ready:
            self._check_model_health(model_name)
            self._is_ready = True
            
        # 适配原生协议 Header
        self._session.headers.update({
            "Content-Type": "application/json"
        })
        
        # 调用父类的通用 OpenAI 格式（LMStudio Native v1 依然兼容此格式，但路径更正为 /api/v1）
        return super()._ask_ai(payload)

    def get_archetype_params(self) -> Dict[str, Any]:
        """针对本地算力调优的黄金参数"""
        return {
            "temperature": 0.7,
            "max_tokens": -1,
            "stream": False
        }
