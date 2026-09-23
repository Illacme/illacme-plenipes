# -*- coding: utf-8 -*-
"""
🛰️ [V126.0] Illacme Plenipes - Tunnel Adapters Registry & Discovery
模块职责：自动扫描并注册网络穿透驱动插件。
🛡️ [SOP-01 规范]：单文件代码行数严格 ≤ 300 行。
"""

import os
import sys
from .base import BaseTunnelAdapter, TunnelRegistry
from core.utils.plugin_loader import discover_and_register

# 1. 扫描并自动注册内置穿透驱动
discover_and_register(__path__, __name__, BaseTunnelAdapter, TunnelRegistry.register)

# 2. 扫描并自动注册外部全局扩展穿透驱动
global_tunnel_path = os.path.abspath("adapters/tunnel")
if os.path.exists(global_tunnel_path):
    if os.path.abspath("adapters") not in sys.path:
        sys.path.append(os.path.abspath("adapters"))
    discover_and_register([global_tunnel_path], "adapters.tunnel", BaseTunnelAdapter, TunnelRegistry.register)

__all__ = ["BaseTunnelAdapter", "TunnelRegistry"]
