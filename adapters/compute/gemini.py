#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes AI Plugin - Google Gemini Adapter
🛡️ [V67.0]：实现 Native (SDK) 与 Standard V3 (REST) 双轨制。
"""
from typing import Dict, Any
from .google_base import GoogleCompatibleTranslator
from .openai import OpenAICompatibleTranslator

class GeminiNativeTranslator(GoogleCompatibleTranslator):
    """🚀 [NATIVE] Google Gemini 原生驱动 (Standard V3)"""
    PLUGIN_ID = 'gemini'
    DISPLAY_NAME = 'Google Gemini'
    VERSION = "V1.0"
    DESCRIPTION = "提供 Google Gemini 官方协议支持，具备超长上下文理解与多模态分析能力。"
    PROTOCOL_FAMILY = 'google'
    
    async def list_models(self) -> list[str]:
        # 简化版模型感应
        return ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-1.0-pro"]

    def get_archetype_params(self) -> Dict[str, Any]:
        return {
            "temperature": 0.4,
            "max_tokens": 8192
        }

class GeminiStandardTranslator(OpenAICompatibleTranslator):
    """🚀 [STANDARD] Google Gemini 兼容驱动 (V1 协议路径)"""
    PLUGIN_ID = 'gemini-v1'
    DISPLAY_NAME = 'Google Gemini'
    VERSION = "V1.0"
    DESCRIPTION = "提供 Google Gemini 的 OpenAI 兼容接口支持，适配主流分发平台的标准协议路径。"
    PROTOCOL_FAMILY = 'standard'
    ALIASES = ['gemini-openai']
    DEFAULT_URL = "https://generativelanguage.googleapis.com/v1beta/openai"
