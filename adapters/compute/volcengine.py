#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes AI Plugin - Volcengine Adapter
🛡️ [V67.0]：对正火山引擎（豆包）工业级感应逻辑。
"""
from typing import Dict, Any, List
from .openai import OpenAICompatibleTranslator

class VolcengineTranslator(OpenAICompatibleTranslator):
    """🚀 火山引擎 (豆包) 专属适配器"""
    PLUGIN_ID = 'volcengine'
    DISPLAY_NAME = 'Volcengine (Doubao)'
    DESCRIPTION = "提供字节跳动火山引擎官方协议支持，适配豆包（Doubao）系列大规模推断模型。"
    PROTOCOL_FAMILY = 'standard'
    DEFAULT_URL = "https://ark.cn-beijing.volces.com/api/v3"
    
    async def list_models(self) -> list[str]:
        """🚀 火山引擎模型对正 (通常为接入点 ID)"""
        return ["ep-xxxxxxxx-xxxx", "doubao-pro-4k", "doubao-pro-32k", "doubao-lite-4k"]

    def get_archetype_params(self) -> Dict[str, Any]:
        return {
            "temperature": 0.6,
            "max_tokens": 4096
        }
