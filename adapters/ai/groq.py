#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes AI Plugin - Groq Adapter
职责：负责 Groq 极速算力的协议适配。
"""
import asyncio
from typing import Dict, Any, List
from .openai import OpenAICompatibleTranslator




class GroqTranslator(OpenAICompatibleTranslator):
    """🚀 [V15.9] Groq 专属适配器"""
    PLUGIN_ID = 'groq'
    DISPLAY_NAME = 'Groq'
    PROTOCOL_FAMILY = 'standard'
    DEFAULT_URL = 'https://api.groq.com/openai/v1'

    async def list_models(self) -> list[str]:
        """🚀 Groq 实时模型感应"""
        try:
            loop = asyncio.get_event_loop()
            url = f"{self.DEFAULT_URL}/models"
            headers = {"Authorization": f"Bearer {self.config.api_key}"}
            resp = await loop.run_in_executor(None, lambda: self._session.get(url, headers=headers, timeout=5))
            if resp.status_code == 200:
                return [m['id'] for m in resp.json().get('data', [])]
            return ["llama3-70b-8192", "mixtral-8x7b-32768"]
        except: return ["llama3-70b-8192", "mixtral-8x7b-32768"]

    def get_archetype_params(self) -> Dict[str, Any]:
        """Groq 追求极致速度，默认参数更偏向稳定性"""
        return {
            "temperature": 0.1,
            "max_tokens": 4096,
            "stream": False
        }
