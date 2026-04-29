#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes AI Plugin - Groq Adapter
职责：负责 Groq 极速算力的协议适配。
"""
from typing import Dict, Any
from .openai import OpenAICompatibleTranslator

class GroqTranslator(OpenAICompatibleTranslator):
    """🚀 [V15.9] Groq 极速适配器"""
    PLUGIN_ID = 'groq'
    
    def __init__(self, node_name, trans_cfg):
        if not trans_cfg.base_url:
            trans_cfg.base_url = "https://api.groq.com/openai/v1"
        super().__init__(node_name, trans_cfg)

    def get_archetype_params(self) -> Dict[str, Any]:
        """Groq 追求极致速度，默认参数更偏向稳定性"""
        return {
            "temperature": 0.1,
            "max_tokens": 4096,
            "stream": False
        }
