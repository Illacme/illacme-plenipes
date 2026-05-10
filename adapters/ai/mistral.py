#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes AI Plugin - Mistral Adapter
职责：负责 Mistral AI 官方 API 的适配（原生 + OpenAI 兼容双轨）。
🛡️ [V67.0]：主权双轨架构实装。
"""
import asyncio
from typing import Dict, Any, List
from .openai import OpenAICompatibleTranslator

class MistralNativeTranslator(OpenAICompatibleTranslator):
    """🚀 Mistral 官方原生协议适配器 (基于 La Plateforme 特性优化)"""
    PLUGIN_ID = 'mistral'
    DISPLAY_NAME = 'Mistral AI'
    PROTOCOL_FAMILY = 'native'
    DEFAULT_URL = "https://api.mistral.ai/v1"
    
    def get_archetype_params(self) -> Dict[str, Any]:
        """针对 Mistral 模型的原生黄金参数"""
        return {
            "temperature": 0.7,
            "top_p": 1,
            "max_tokens": 4096,
            "safe_prompt": False
        }

class MistralStandardTranslator(OpenAICompatibleTranslator):
    """🚀 Mistral 标准 OpenAI 兼容适配器"""
    PLUGIN_ID = 'mistral-openai'
    DISPLAY_NAME = 'Mistral AI'
    PROTOCOL_FAMILY = 'standard'
    DEFAULT_URL = "https://api.mistral.ai/v1"

    async def list_models(self) -> list[str]:
        """🚀 Mistral 实时模型感应"""
        try:
            loop = asyncio.get_event_loop()
            url = f"{self.DEFAULT_URL}/models"
            headers = {"Authorization": f"Bearer {self.config.api_key}"}
            resp = await loop.run_in_executor(None, lambda: self._session.get(url, headers=headers, timeout=5))
            if resp.status_code == 200:
                return [m['id'] for m in resp.json().get('data', [])]
            return ["mistral-tiny", "mistral-small", "mistral-medium", "mistral-large-latest"]
        except: return []
