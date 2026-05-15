#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes AI Plugin - SiliconFlow Adapter
🛡️ [V67.0]：对正工业级协议感应逻辑。
"""
import requests
import asyncio
from .openai import OpenAICompatibleTranslator
from core.utils.tracing import tlog

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
        try:
            loop = asyncio.get_event_loop()
            url = f"{self.DEFAULT_URL}/models"
            headers = {"Authorization": f"Bearer {self.config.api_key}"}
            resp = await loop.run_in_executor(None, lambda: requests.get(url, headers=headers, timeout=5))
            if resp.status_code == 200:
                return [m['id'] for m in resp.json().get('data', [])]
            return ["deepseek-ai/DeepSeek-V3", "deepseek-ai/DeepSeek-R1"]
        except Exception as e:
            tlog.warning(f"⚠️ [SiliconFlow] 无法感应模型列表: {e}")
            return ["deepseek-ai/DeepSeek-V3"]
