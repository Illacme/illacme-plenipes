#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes AI Plugin - Baichuan Adapter
🛡️ [V67.0]：对齐工业级模型感应逻辑。
"""
from typing import Dict, Any, List
from .openai import OpenAICompatibleTranslator

class BaichuanTranslator(OpenAICompatibleTranslator):
    """🚀 Baichuan 专属适配器"""
    PLUGIN_ID = 'baichuan'
    DISPLAY_NAME = 'Baichuan'
    PROTOCOL_FAMILY = 'standard'
    DEFAULT_URL = "https://api.baichuan-ai.com/v1"
    
    async def list_models(self) -> list[str]:
        return ["Baichuan4", "Baichuan3-Turbo", "Baichuan2-Turbo"]

    def get_archetype_params(self) -> Dict[str, Any]:
        return {"temperature": 0.3, "max_tokens": 4096}
