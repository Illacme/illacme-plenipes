#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - AI Provider Auto-Discovery
模块职责：自动扫描并注册所有 AI 算力协议。
🛡️ [AEL-Iter-v5.3]：实现 Zero-Touch 算力层扩展。
"""

from .registry import AIProviderRegistry
from core.adapters.ai.base import BaseTranslator
from core.utils.plugin_loader import discover_and_register

import os
import sys

# 🚀 [Zero-Touch] 1. 扫描核心内置插件
discover_and_register(__path__, __name__, BaseTranslator, AIProviderRegistry.register)

# 🚀 [Zero-Touch] 2. 扫描全局扩展插件
global_ai_path = os.path.abspath("adapters/ai")
if os.path.exists(global_ai_path):
    if os.path.abspath("adapters") not in sys.path:
        sys.path.append(os.path.abspath("adapters"))
    discover_and_register([global_ai_path], "adapters.ai", BaseTranslator, AIProviderRegistry.register)
