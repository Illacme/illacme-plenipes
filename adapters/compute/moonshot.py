#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes AI Plugin - Moonshot (Kimi) Adapter
🛡️ [V67.0]：对齐工业级模型感应逻辑。
"""
from typing import Dict, Any
from .openai import OpenAICompatibleTranslator

class MoonshotTranslator(OpenAICompatibleTranslator):
    """🚀 Moonshot (Kimi) 专属适配器"""
    PLUGIN_ID = 'moonshot'
    DISPLAY_NAME = 'Moonshot (Kimi)'
    VERSION = "V1.0"
    DESCRIPTION = "提供月之暗面 Kimi 官方协议支持，具备卓越的长文本分析与中文语境理解能力。"
    PROTOCOL_FAMILY = 'standard'
    DEFAULT_URL = "https://api.moonshot.cn/v1"
    
    async def list_models(self) -> list[str]:
        """🚀 Moonshot 实时模型感应"""
        api_key = self.config.api_key
        if not api_key:
            raise ValueError("未填写 API Key 物理密钥")
            
        import asyncio
        loop = asyncio.get_event_loop()
        url = self.safe_get_url("/models")
        headers = {"Authorization": f"Bearer {api_key}"}
        resp = await loop.run_in_executor(None, lambda: self._session.get(url, headers=headers, timeout=5))
        if resp.status_code == 200:
            return [m['id'] for m in resp.json().get('data', [])]
            
        resp.raise_for_status()
        return ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"]

    def get_archetype_params(self) -> Dict[str, Any]:
        return {"temperature": 0.3, "max_tokens": 4096}
