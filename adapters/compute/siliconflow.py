#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes AI Plugin - SiliconFlow Adapter
🛡️ [V67.0]：对正工业级协议感应逻辑。
"""
import requests
import asyncio
from .openai import OpenAICompatibleTranslator

class SiliconFlowTranslator(OpenAICompatibleTranslator):
    """🚀 SiliconFlow 专属适配器"""
    PLUGIN_ID = 'siliconflow'
    DISPLAY_NAME = 'SiliconFlow'
    VERSION = "V1.0"
    DESCRIPTION = "提供硅基流动（SiliconFlow）加速平台支持，具备极高并发处理能力的大规模模型分发节点。"
    PROTOCOL_FAMILY = 'standard'
    DEFAULT_URL = "https://api.siliconflow.cn/v1"
    
    async def list_models(self) -> list[str]:
        """🚀 SiliconFlow 实时模型感应"""
        api_key = self.config.api_key
        if not api_key:
            raise ValueError("未填写 API Key 物理密钥")
            
        loop = asyncio.get_event_loop()
        url = self.safe_get_url("/models")
        headers = {"Authorization": f"Bearer {api_key}"}
        timeout = self.get_network_timeout(default=15.0)
        proxies = self.get_proxy_dict()
        resp = await loop.run_in_executor(None, lambda: requests.get(url, headers=headers, proxies=proxies, timeout=timeout))
        if resp.status_code == 200:
            return [m['id'] for m in resp.json().get('data', [])]
            
        resp.raise_for_status()
        return ["deepseek-ai/DeepSeek-V3", "deepseek-ai/DeepSeek-R1"]
