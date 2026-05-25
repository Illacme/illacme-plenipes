#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes AI Plugin - Zhipu AI Adapter
🛡️ [V67.0]：对正智谱 GLM 工业级感应逻辑。
"""
from typing import Dict, Any
from .openai import OpenAICompatibleTranslator

class ZhipuTranslator(OpenAICompatibleTranslator):
    """🚀 智谱 GLM 专属适配器"""
    PLUGIN_ID = 'zhipu'
    DISPLAY_NAME = 'Zhipu GLM'
    VERSION = "V1.0"
    DESCRIPTION = "提供智谱 GLM 官方协议支持，基于清华系基座能力的国产自研大模型算力节点。"
    PROTOCOL_FAMILY = 'standard'
    DEFAULT_URL = "https://open.bigmodel.cn/api/paas/v4"
    
    async def list_models(self) -> list[str]:
        """🚀 智谱 GLM 常用模型感应"""
        api_key = self.safe_get_config('api_key')
        if not api_key:
            raise ValueError("未填写 API Key 物理密钥")
        return await super().list_models()

    def get_archetype_params(self) -> Dict[str, Any]:
        return {
            "temperature": 0.5,
            "max_tokens": 4096
        }
