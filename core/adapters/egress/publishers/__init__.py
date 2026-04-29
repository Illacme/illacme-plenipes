#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import logging
from .base import BasePublisher, PublisherRegistry
from core.utils.plugin_loader import discover_and_register

from core.utils.tracing import tlog

# 🚀 [Zero-Touch] 1. 扫描内置发布器
discover_and_register(__path__, __name__, BasePublisher, PublisherRegistry._targets.__setitem__)

# 🚀 [Zero-Touch] 2. 扫描全局扩展发布器
global_pub_path = os.path.abspath("adapters/publishers")
if os.path.exists(global_pub_path):
    if os.path.abspath("adapters") not in sys.path:
        sys.path.append(os.path.abspath("adapters"))
    discover_and_register([global_pub_path], "adapters.publishers", BasePublisher, PublisherRegistry._targets.__setitem__)

__all__ = ["BasePublisher", "PublisherRegistry"]
