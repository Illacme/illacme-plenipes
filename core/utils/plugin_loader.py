#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Plugin Loader Utility
模块职责：提供动态目录扫描与插件自动发现能力。
🛡️ [AEL-Iter-v5.3]：增强版的自发现加载器（支持显式 ID）。
"""

import os
import pkgutil
import importlib
import inspect
import logging
import re

logger = logging.getLogger("Illacme.plenipes")

def discover_and_register(package_path, package_name, base_class, registry_func):
    """
    🚀 自动扫描包目录并注册符合条件的类
    """
    for _, module_name, is_pkg in pkgutil.iter_modules(package_path):
        if is_pkg:
            continue
        if module_name in ['base', 'registry', 'runner', 'common', 'strategies']:
            continue
            
        full_module_name = f"{package_name}.{module_name}"
        try:
            module = importlib.import_module(full_module_name)
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, base_class) and obj is not base_class:
                    # 1. 优先使用类定义的 PLUGIN_ID
                    # 2. 其次使用剥离后缀后的 kebab-case 名称
                    plugin_id = getattr(obj, 'PLUGIN_ID', None)
                    if not plugin_id:
                        # 剥离常见后缀并转为 kebab-case
                        short_name = name.replace('Adapter', '').replace('Dialect', '').replace('Syndicator', '').replace('Translator', '')
                        plugin_id = re.sub(r'(?<!^)(?=[A-Z])', '-', short_name).lower()
                    
                    registry_func(plugin_id, obj)
                    
        except Exception as e:
            logger.error(f"❌ [加载器] 无法加载插件模块 {full_module_name}: {e}")
