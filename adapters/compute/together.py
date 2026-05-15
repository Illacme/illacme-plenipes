#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes AI Plugin - Together AI Adapter
职责：负责 Together AI 算力平台的协议适配。
"""
import asyncio
from typing import Dict, Any
from .openai import OpenAICompatibleTranslator




class TogetherTranslator(OpenAICompatibleTranslator):
    """🚀 [V15.9] Together AI 专属适配器"""
    PLUGIN_ID = 'together'
    DISPLAY_NAME = 'Together AI'
    VERSION = "V1.0"
    DESCRIPTION = "提供 Together AI 全球加速节点支持，兼容 Llama 3.1、Qwen 2 等顶级开源算力矩阵。"
    PROTOCOL_FAMILY = 'standard'
    DEFAULT_URL = 'https://api.together.xyz/v1'

    async def list_models(self) -> list[str]:
        """🚀 Together AI 实时模型感应"""
        try:
            loop = asyncio.get_event_loop()
            url = f"{self.DEFAULT_URL}/models"
            headers = {"Authorization": f"Bearer {self.config.api_key}"}
            resp = await loop.run_in_executor(None, lambda: self._session.get(url, headers=headers, timeout=5))
            if resp.status_code == 200:
                return [m['id'] for m in resp.json()]
            return []
        except: return []

    def get_archetype_params(self) -> Dict[str, Any]:
        return {
            "temperature": 0.7,
            "top_p": 0.7,
            "max_tokens": 4096,
            "repetition_penalty": 1
        }
