#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from .openai import OpenAICompatibleTranslator

class XAITranslator(OpenAICompatibleTranslator):
    """🚀 xAI (Grok) 协议适配器"""
    PLUGIN_ID = 'xai'
    ALIASES = ['grok', 'twitter']
    DISPLAY_NAME = 'xAI (Grok)'
    VERSION = "V1.0"
    DESCRIPTION = "提供马斯克旗下 xAI 官方 API 支持，底层兼容标准 OpenAI 协议族。"
    PROTOCOL_FAMILY = 'standard'
    DEFAULT_URL = "https://api.x.ai/v1"

    async def list_models(self) -> list[str]:
        """覆盖模型列表端点以专门感应 Grok 模型族"""
        # xAI 支持标准的 /models 接口，这里复用 OpenAICompatibleTranslator 内部自带的逻辑，
        # 如果父类未完全处理好，也可以在此做特定重写。
        # 由于它是 100% 兼容的，这里可以直接使用继承的方法，我们将其显式标记以体现架构地位。
        return await super().list_models()
