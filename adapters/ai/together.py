#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes AI Plugin - Together AI Adapter
职责：负责 Together AI 算力平台的协议适配。
"""
from typing import Dict, Any
from .openai import OpenAICompatibleTranslator

class TogetherTranslator(OpenAICompatibleTranslator):
    """🚀 [V15.9] Together AI 专属适配器"""
    PLUGIN_ID = 'together'
    
    def __init__(self, node_name, trans_cfg):
        if not trans_cfg.base_url:
            trans_cfg.base_url = "https://api.together.xyz/v1"
        super().__init__(node_name, trans_cfg)

    def get_archetype_params(self) -> Dict[str, Any]:
        return {
            "temperature": 0.7,
            "top_p": 0.7,
            "max_tokens": 4096,
            "repetition_penalty": 1
        }
