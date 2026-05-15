#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from .openai import OpenAICompatibleTranslator

class DashScopeTranslator(OpenAICompatibleTranslator):
    """🚀 阿里云通义千问 (DashScope) 适配器"""
    PLUGIN_ID = 'dashscope'
    DISPLAY_NAME = 'Aliyun (Qwen)'
    VERSION = "V1.0"
    DESCRIPTION = "提供阿里云通义千问官方协议支持，适配 Qwen 系列全尺寸模型的大规模生产环境。"
    PROTOCOL_FAMILY = 'standard'
    DEFAULT_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
