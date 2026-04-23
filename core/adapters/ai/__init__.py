#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - AI Provider Auto-Discovery
模块职责：自动扫描并注册所有 AI 算力协议。
🛡️ [AEL-Iter-v5.3]：实现 Zero-Touch 算力层扩展。
"""

from .registry import AIProviderRegistry
from .base import BaseTranslator
from core.utils.plugin_loader import discover_and_register

# 🚀 [Zero-Touch] 自动扫描并注册当前包下的所有 AI 算力插件
# 注意：package_name 需要对齐物理路径
discover_and_register(__path__, __name__, BaseTranslator, AIProviderRegistry.register)
