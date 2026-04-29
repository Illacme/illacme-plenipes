#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Syndication Targets Auto-Discovery
模块职责：自动扫描并注册所有平台分发插件。
🛡️ [AEL-Iter-v5.3]：实现 Zero-Touch 分发端扩展。
"""

from core.adapters.syndication.base import BaseSyndicator
from core.utils.plugin_loader import discover_and_register

# 🚀 此处定义一个本地注册容器，供 ContentSyndicator 消费
TARGET_REGISTRY = {}

def register_target(name, cls):
    TARGET_REGISTRY[name] = cls

import os
import sys

# 🚀 [Zero-Touch] 1. 扫描内置分发插件
discover_and_register(__path__, __name__, BaseSyndicator, register_target)

# 🚀 [Zero-Touch] 2. 扫描全局扩展分发插件
global_syn_path = os.path.abspath("adapters/syndication")
if os.path.exists(global_syn_path):
    if os.path.abspath("adapters") not in sys.path:
        sys.path.append(os.path.abspath("adapters"))
    discover_and_register([global_syn_path], "adapters.syndication", BaseSyndicator, register_target)
