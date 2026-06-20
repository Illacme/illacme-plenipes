#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Image Hosting Targets Auto-Discovery
职责：自动扫描并注册所有图床驱动插件。
🛡️ [SOP-01] 物理行数限制：保持在 300 行以内。
"""

from core.adapters.image_hosting.base import BaseImageHost
from core.utils.plugin_loader import discover_and_register

# 🚀 本地注册容器
IMAGE_HOST_REGISTRY = {}

def register_host(name, cls):
    IMAGE_HOST_REGISTRY[name] = cls

import os
import sys

# 🚀 1. 扫描内置图床插件
discover_and_register([os.path.dirname(__file__)], "core.adapters.image_hosting", BaseImageHost, register_host)

# 🚀 2. 扫描全局扩展图床插件
global_host_path = os.path.abspath("adapters/egress/image_hosting")
if os.path.exists(global_host_path):
    if os.path.abspath("adapters") not in sys.path:
        sys.path.append(os.path.abspath("adapters"))
    discover_and_register([global_host_path], "adapters.egress.image_hosting", BaseImageHost, register_host)
