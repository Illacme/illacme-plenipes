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
        import asyncio
        loop = asyncio.get_event_loop()
        url = self.safe_get_url("/models")
        headers = {
            'HTTP-Referer': 'https://github.com/Illacme-plenipes/illacme-plenipes',
            'X-Title': 'Illacme-plenipes Engine',
            'User-Agent': 'Illacme-Plenipes/V100.0'
        }
        api_key = self.safe_get_config('api_key')
        if api_key and api_key not in ["not-needed", "none", "empty", ""]:
            headers["Authorization"] = f"Bearer {api_key}"
            
        proxies = self.get_proxy_dict()
        timeout = self.get_network_timeout(default=15.0)

        def _fetch():
            return self._session.get(url, headers=headers, proxies=proxies, timeout=timeout)

        resp = await loop.run_in_executor(None, _fetch)
        if resp.status_code == 200:
            data = resp.json()
            items = data.get('data', [])
            return [m['id'] for m in items if isinstance(m, dict) and 'id' in m]
            
        resp.raise_for_status()
        return ["openai/gpt-4o", "anthropic/claude-3.5-sonnet"]

    def _ask_ai(self, payload: Dict[str, Any]) -> str:
        # OpenRouter 需要额外的 Header 标识
        self._session.headers.update({
            'HTTP-Referer': 'https://github.com/Illacme-plenipes/illacme-plenipes',
            'X-Title': 'Illacme-plenipes Engine'
        })
        return super()._ask_ai(payload)
