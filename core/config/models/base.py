#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Config - Base Models
职责：定义配置中心通用的枚举与基础常量。
🛡️ [V24.0] Pydantic 严格校验体系：基于 Pydantic V2 构建的基础设施。
"""
from enum import Enum

class LogFormat(str, Enum):
    """日志输出格式"""
    JSON = "json"
    PLAIN = "plain"
    RICH = "rich"

class ProviderType:
    """🚀 [V15.9] 插件化兼容：改为常量类，允许第三方插件通过字符串扩展"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    OLLAMA = "ollama"
    DEEPSEEK = "deepseek"
    OPENROUTER = "openrouter"
    LMSTUDIO = "lmstudio"
    GROQ = "groq"
    MISTRAL = "mistral"
    TOGETHER = "together"
    COHERE = "cohere"
    SILICONFLOW = "siliconflow"
    AZURE = "azure"
    MOCK = "mock"

class StrategyType(str, Enum):
    """同步与 AI 调用策略"""
    SINGLE = "single"
    FALLBACK = "fallback"
    CONCURRENT = "concurrent"
    NONE = "none"
