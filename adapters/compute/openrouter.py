#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes AI Plugin - OpenRouter Adapter
🛡️ [V67.0]：对齐工业级模型感应逻辑。
"""
import asyncio
from typing import Dict, Any
from .openai import OpenAICompatibleTranslator

class OpenRouterTranslator(OpenAICompatibleTranslator):
    """🚀 OpenRouter 专属适配器"""
    PLUGIN_ID = 'openrouter'
    DISPLAY_NAME = 'OpenRouter'
    VERSION = "V2.1"
    DESCRIPTION = "提供 OpenRouter 全球统一网关支持，一站式接入 Anthropic、Llama 3、Mistral 等顶级模型算力。"
    PROTOCOL_FAMILY = 'standard'
    DEFAULT_URL = 'https://openrouter.ai/api/v1'
    
    async def list_models(self) -> list[str]:
        """🚀 OpenRouter 实时模型感应"""
        try:
            loop = asyncio.get_event_loop()
            url = f"{self.DEFAULT_URL}/models"
            resp = await loop.run_in_executor(None, lambda: self._session.get(url, timeout=5))
            if resp.status_code == 200:
                return [m['id'] for m in resp.json().get('data', [])]
            return ["openai/gpt-4o", "anthropic/claude-3.5-sonnet"]
        except: return []

    def _ask_ai(self, payload: Dict[str, Any]) -> str:
        # OpenRouter 需要额外的 Header 标识
        self._session.headers.update({
            'HTTP-Referer': 'https://github.com/Illacme-plenipes/illacme-plenipes',
            'X-Title': 'Illacme-plenipes Engine'
        })
        return super()._ask_ai(payload)
