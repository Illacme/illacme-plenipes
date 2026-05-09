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
    DEFAULT_URL = 'https://openrouter.ai/api/v1'
    
    def _ask_ai(self, payload: Dict[str, Any]) -> str:
        self._session.headers.update({
            'HTTP-Referer': 'https://github.com/Illacme-plenipes/illacme-plenipes',
            'X-Title': 'Illacme-plenipes Engine'
        })
        return super()._ask_ai(payload)

