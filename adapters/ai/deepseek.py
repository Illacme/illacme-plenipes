#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes AI Plugin - DeepSeek Adapter
职责：负责 DeepSeek 官方 API 的深度适配。
🛡️ [V15.9] 极速接入：预置 DeepSeek 官方基准地址。
"""
from typing import Dict, Any
from .openai import OpenAICompatibleTranslator

class DeepSeekTranslator(OpenAICompatibleTranslator):
    """🚀 [V15.9] DeepSeek 专属适配器"""
    PLUGIN_ID = 'deepseek'
    
    def __init__(self, node_name, trans_cfg):
        if not trans_cfg.base_url:
            # 自动指向 DeepSeek 官方 API
            trans_cfg.base_url = "https://api.deepseek.com"
        super().__init__(node_name, trans_cfg)

    def get_archetype_params(self) -> Dict[str, Any]:
        """针对 DeepSeek-V3/R1 优化的黄金参数"""
        return {
            "temperature": 0.0,  # 翻译任务建议 0.0 以获得最稳定的输出
            "max_tokens": 8192,  # DeepSeek 支持较大的上下文输出
            "stream": False
        }
