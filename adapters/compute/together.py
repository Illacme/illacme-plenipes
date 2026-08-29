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
        api_key = self.config.api_key
        if not api_key:
            raise ValueError("未填写 API Key 物理密钥")
            
        loop = asyncio.get_event_loop()
        url = self.safe_get_url("/models")
        headers = {"Authorization": f"Bearer {api_key}"}
        timeout = self.get_network_timeout(default=15.0)
        proxies = self.get_proxy_dict()
        resp = await loop.run_in_executor(None, lambda: self._session.get(url, headers=headers, proxies=proxies, timeout=timeout))
        if resp.status_code == 200:
            return [m['id'] for m in resp.json()]
            
        resp.raise_for_status()
        return []

    def get_archetype_params(self) -> Dict[str, Any]:
        return {
            "temperature": 0.7,
            "top_p": 0.7,
            "max_tokens": 4096,
            "repetition_penalty": 1
        }
