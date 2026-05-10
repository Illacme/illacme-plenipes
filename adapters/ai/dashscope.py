#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from .openai import OpenAICompatibleTranslator

class DashScopeTranslator(OpenAICompatibleTranslator):
    """🚀 阿里云通义千问 (DashScope) 适配器"""
    PLUGIN_ID = 'dashscope'
    DISPLAY_NAME = 'Aliyun (Qwen)'
    PROTOCOL_FAMILY = 'standard'
    DEFAULT_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
