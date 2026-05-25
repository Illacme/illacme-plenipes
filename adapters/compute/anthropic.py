#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes AI Plugin - Anthropic Adapter
🛡️ [V67.0]：对正 Anthropic 标准协议基类。
"""
from typing import Dict, Any
from .anthropic_base import AnthropicCompatibleTranslator

class AnthropicTranslator(AnthropicCompatibleTranslator):
    """🚀 Anthropic 官方驱动 (Messages API)"""
    PLUGIN_ID = 'anthropic'
    DISPLAY_NAME = 'Anthropic Claude'
    VERSION = "V1.0"
    DESCRIPTION = "提供 Anthropic 官方协议支持，兼容 Claude 3.5 Sonnet、Claude 3 Opus 等长文本理解模型。"
    PROTOCOL_FAMILY = 'anthropic'
    DEFAULT_URL = "https://api.anthropic.com/v1"
    
    def get_auth_headers(self) -> dict:
        return {
            "x-api-key": self.config.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }

    async def list_models(self) -> list[str]:
        api_key = self.safe_get_config('api_key')
        if not api_key:
            raise ValueError("未填写 API Key 物理密钥")
        return ["claude-3-5-sonnet-20241022", "claude-3-opus-20240229", "claude-3-haiku-20240307"]

    def get_archetype_params(self) -> Dict[str, Any]:
        return {
            "temperature": 0.0, # 出版级任务建议 0
            "max_tokens": 4096
        }
