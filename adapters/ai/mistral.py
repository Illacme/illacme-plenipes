#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes AI Plugin - Mistral AI Adapter
职责：负责 Mistral AI 原生协议的适配。
"""
from typing import Dict, Any
from .openai import OpenAICompatibleTranslator

class MistralTranslator(OpenAICompatibleTranslator):
    """🚀 [V15.9] Mistral 原生适配器"""
    PLUGIN_ID = 'mistral'
    
    def __init__(self, node_name, trans_cfg):
        if not trans_cfg.base_url:
            trans_cfg.base_url = "https://api.mistral.ai/v1"
        super().__init__(node_name, trans_cfg)

    def get_archetype_params(self) -> Dict[str, Any]:
        return {
            "temperature": 0.2,
            "top_p": 1,
            "max_tokens": 4096
        }
