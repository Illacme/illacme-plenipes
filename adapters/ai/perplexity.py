#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes AI Plugin - Perplexity Adapter
🛡️ [V67.0]：对正工业级协议感应逻辑。
"""
from typing import Dict, Any, List
from .openai import OpenAICompatibleTranslator

class PerplexityTranslator(OpenAICompatibleTranslator):
    """🚀 Perplexity 专属适配器"""
    PLUGIN_ID = 'perplexity'
    DISPLAY_NAME = 'Perplexity'
    PROTOCOL_FAMILY = 'standard'
    DEFAULT_URL = "https://api.perplexity.ai"
    
    async def list_models(self) -> list[str]:
        """🚀 Perplexity 常用模型对正"""
        return [
            "llama-3.1-sonar-small-128k-online", 
            "llama-3.1-sonar-large-128k-online", 
            "llama-3.1-sonar-huge-128k-online",
            "llama-3.1-sonar-small-128k-chat",
            "llama-3.1-sonar-large-128k-chat"
        ]

    def get_archetype_params(self) -> Dict[str, Any]:
        return {
            "temperature": 0.2,
            "max_tokens": 4096,
            "stream": False
        }
