#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes AI Plugin - Groq Adapter
职责：负责 Groq 极速算力的协议适配。
"""
import asyncio
from typing import Dict, Any
from .openai import OpenAICompatibleTranslator




class GroqTranslator(OpenAICompatibleTranslator):
    """🚀 [V15.9] Groq 专属适配器"""
    PLUGIN_ID = 'groq'
    DISPLAY_NAME = 'Groq'
    VERSION = "V1.0"
    DESCRIPTION = "提供 Groq LPU 加速协议支持，实现极速推理响应（400+ tokens/sec）。"
    PROTOCOL_FAMILY = 'standard'
    DEFAULT_URL = 'https://api.groq.com/openai/v1'

    async def list_models(self) -> list[str]:
        """🚀 Groq 实时模型感应"""
        api_key = self.config.api_key
        if not api_key:
            raise ValueError("未填写 API Key 物理密钥")
            
        loop = asyncio.get_event_loop()
        url = self.safe_get_url("/models")
        headers = {"Authorization": f"Bearer {api_key}"}
        resp = await loop.run_in_executor(None, lambda: self._session.get(url, headers=headers, timeout=5))
        if resp.status_code == 200:
            return [m['id'] for m in resp.json().get('data', [])]
            
        resp.raise_for_status()
        return ["llama3-70b-8192", "mixtral-8x7b-32768"]

    def get_archetype_params(self) -> Dict[str, Any]:
        """Groq 追求极致速度，默认参数更偏向稳定性"""
        return {
            "temperature": 0.1,
            "max_tokens": 4096,
            "stream": False
        }
