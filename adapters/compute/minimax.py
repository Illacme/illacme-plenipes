#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes AI Plugin - MiniMax Adapter
🛡️ [V67.0]：对齐工业级模型感应逻辑。
"""
from typing import Dict, Any, List
from .openai import OpenAICompatibleTranslator

class MiniMaxTranslator(OpenAICompatibleTranslator):
    """🚀 MiniMax 专属适配器"""
    PLUGIN_ID = 'minimax'
    DISPLAY_NAME = 'MiniMax (abab)'
    DESCRIPTION = "提供 MiniMax 官方协议支持，适配 abab 系列具备强逻辑理解能力的国产大模型算力节点。"
    PROTOCOL_FAMILY = 'standard'
    DEFAULT_URL = "https://api.minimax.chat/v1"
    
    async def list_models(self) -> list[str]:
        return ["abab6.5-chat", "abab6.5s-chat", "abab7-chat"]

    def get_archetype_params(self) -> Dict[str, Any]:
        return {"temperature": 0.1, "max_tokens": 4096}
