#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes AI Plugin - LocalAI Adapter
🛡️ [V67.0]：对正 LocalAI 本地主权感应逻辑。
"""
import requests
import asyncio
from .openai import OpenAICompatibleTranslator
from core.utils.tracing import tlog

class LocalAITranslator(OpenAICompatibleTranslator):
    """🚀 LocalAI 专属适配器"""
    PLUGIN_ID = 'localai'
    DISPLAY_NAME = 'LocalAI'
    VERSION = "V1.0"
    DESCRIPTION = "提供 LocalAI 本地开源算力支持，兼容 OpenAI 协议栈，支持在私有硬件上部署多种主流 AI 模型。"
    PROTOCOL_FAMILY = 'native'
    DEFAULT_URL = "http://localhost:8080/v1"
    
    async def list_models(self) -> list[str]:
        """🚀 LocalAI 实时模型感应"""
        try:
            loop = asyncio.get_event_loop()
            url = self.safe_get_url("/models")
            timeout = self.get_network_timeout(default=10.0)
            proxies = self.get_proxy_dict()
            resp = await loop.run_in_executor(None, lambda: requests.get(url, proxies=proxies, timeout=timeout))
            if resp.status_code == 200:
                return [m['id'] for m in resp.json().get('data', [])]
            return []
        except Exception as e:
            tlog.warning(f"⚠️ [LocalAI] 无法感应模型列表: {e}")
            return []

    async def test_connection(self) -> tuple[bool, str]:
        """测试 LocalAI 连通性"""
        try:
            models = await self.list_models()
            if models:
                return True, f"✅ LocalAI 已就绪。模型库: {', '.join(models)}"
            return True, "✅ LocalAI 服务在线，但未检测到已加载的模型。"
        except Exception as e:
            return False, f"❌ LocalAI 连通失败: {e}"
