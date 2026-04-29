#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes AI Plugin - SiliconFlow Adapter
职责：负责硅基流动 (SiliconFlow) 算力平台的协议适配。
🛡️ [V15.9] 极速接入：预置国内主流算力网关地址。
"""
from typing import Dict, Any
from .openai import OpenAICompatibleTranslator

class SiliconFlowTranslator(OpenAICompatibleTranslator):
    """🚀 [V15.9] SiliconFlow 专属适配器"""
    PLUGIN_ID = 'siliconflow'
    
    def __init__(self, node_name, trans_cfg):
        if not trans_cfg.base_url:
            # 自动指向硅基流动国内节点
            trans_cfg.base_url = "https://api.siliconflow.cn/v1"
        super().__init__(node_name, trans_cfg)

    def get_archetype_params(self) -> Dict[str, Any]:
        """针对 DeepSeek/Qwen 等国产模型优化的参数"""
        return {
            "temperature": 0.3,
            "top_p": 0.7,
            "max_tokens": 4096,
            "stream": False
        }
