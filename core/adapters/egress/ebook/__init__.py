# -*- coding: utf-8 -*-
"""
Illacme Plenipes - EBook Egress Adapters Matrix
模块职责：电子书与数字出版物装订出口插件的动态发现与调度中心。
🚀 [Zero-Touch] 架构：自动扫描并注册内置与外部扩展电子书驱动。
"""

import os
import sys
from .base import BaseEBookAdapter, EBookRegistry
from core.utils.plugin_loader import discover_and_register

# 1. 扫描并自动注册当前包下的所有内置电子书驱动
discover_and_register(__path__, __name__, BaseEBookAdapter, EBookRegistry.register_class)

# 2. 扫描并自动注册外部全局扩展装订驱动
global_ebook_path = os.path.abspath("adapters/egress/ebook")
if os.path.exists(global_ebook_path):
    if os.path.abspath("adapters") not in sys.path:
        sys.path.append(os.path.abspath("adapters"))
    discover_and_register([global_ebook_path], "adapters.egress.ebook", BaseEBookAdapter, EBookRegistry.register_class)

__all__ = ["BaseEBookAdapter", "EBookRegistry"]
