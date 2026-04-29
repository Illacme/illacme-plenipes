#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes AI Plugin - OpenRouter Adapter
职责：负责 OpenRouter 算力网关的协议适配。
🛡️ [V15.9] 极致零配置：自动处理路由头部。
"""
from typing import Dict, Any
from .openai import OpenAICompatibleTranslator

class OpenRouterTranslator(OpenAICompatibleTranslator):
    """🚀 [V15.9] OpenRouter 专属适配器"""
    PLUGIN_ID = 'openrouter'
    
    def _ask_ai(self, payload: Dict[str, Any]) -> str:
        # 🚀 OpenRouter 要求的特殊 Header，用于统计和优化路由
        extra_headers = {
            "HTTP-Referer": "https://github.com/Illacme-plenipes/illacme-plenipes",
            "X-Title": "Illacme-plenipes Engine"
        }
        
        # 动态修改 trans_cfg 里的 base_url，如果用户没填的话
        if not self.trans_cfg.base_url:
            self.trans_cfg.base_url = "https://openrouter.ai/api/v1"
            
        # 调用父类的 OpenAI 逻辑，但注入特殊 Header
        # 注意：requests.Session 会自动合并 headers
        self._session.headers.update(extra_headers)
        return super()._ask_ai(payload)
