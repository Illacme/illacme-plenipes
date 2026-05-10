#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes AI Plugin - DeepSeek Adapter
职责：负责 DeepSeek 官方 API 的深度适配。
🛡️ [V15.9] 极速接入：预置 DeepSeek 官方基准地址。
"""
import asyncio
from typing import Dict, Any, List
from .openai import OpenAICompatibleTranslator



class DeepSeekTranslator(OpenAICompatibleTranslator):
    """🚀 [V15.9] DeepSeek 专属适配器"""
    PLUGIN_ID = 'deepseek'
    DISPLAY_NAME = 'DeepSeek'
    PROTOCOL_FAMILY = 'standard'
    DEFAULT_URL = "https://api.deepseek.com"
    
    async def list_models(self) -> list[str]:
        """🚀 DeepSeek 实时模型感应"""
        try:
            loop = asyncio.get_event_loop()
            url = f"{self.config.base_url}/models"
            headers = {"Authorization": f"Bearer {self.config.api_key}"}
            resp = await loop.run_in_executor(None, lambda: self._session.get(url, headers=headers, timeout=5))
            if resp.status_code == 200:
                return [m['id'] for m in resp.json().get('data', [])]
            return ["deepseek-chat", "deepseek-reasoner"]
        except: return ["deepseek-chat", "deepseek-reasoner"]

    def get_archetype_params(self) -> Dict[str, Any]:
        """针对 DeepSeek-V3/R1 优化的黄金参数"""
        return {
            "temperature": 0.0,  # 翻译任务建议 0.0 以获得最稳定的输出
            "max_tokens": 8192,  # DeepSeek 支持较大的上下文输出
            "stream": False
        }

class DeepSeekR1Translator(DeepSeekTranslator):
    """🚀 [V67.0] DeepSeek R1 深度适配器 (自动处理推理链)"""
    PLUGIN_ID = 'deepseek-r1'
    DISPLAY_NAME = 'DeepSeek R1 (Sovereign Clean)'
    PROTOCOL_FAMILY = 'native' # 因为有特殊的后处理逻辑，视为原生增强
    
    def get_archetype_params(self) -> Dict[str, Any]:
        """针对 R1 推理模型优化的参数"""
        return {
            "temperature": 0.6,
            "max_tokens": 8192,
            "stream": False
        }

    def _ask_ai(self, payload: Dict[str, Any]) -> str:
        # 基类 BaseTranslator 已经实现了自动清洗逻辑
        return super()._ask_ai(payload)
