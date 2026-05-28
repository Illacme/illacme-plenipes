#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from .openai import OpenAICompatibleTranslator

class HuggingFaceTranslator(OpenAICompatibleTranslator):
    """🚀 HuggingFace (Serverless Inference) 协议适配器"""
    PLUGIN_ID = 'huggingface'
    ALIASES = ['hf', 'hf-inference']
    DISPLAY_NAME = 'HuggingFace'
    VERSION = "V1.0"
    DESCRIPTION = "提供 HuggingFace Serverless Inference API 支持，兼容最新的 Messages API 标准协议。"
    PROTOCOL_FAMILY = 'standard'
    DEFAULT_URL = "https://api-inference.huggingface.co/v1"

    async def list_models(self) -> list[str]:
        """覆盖模型列表端点以专门感应 HF 模型族"""
        return await super().list_models()
