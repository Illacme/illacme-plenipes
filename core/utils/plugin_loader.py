#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omni-Hub Plugin Loader
负责扫描外部插件目录并动态加载模块。
"""

import os
import importlib.util
import inspect
from typing import List, Type
from core.utils.tracing import tlog

class PluginLoader:
    """🚀 [V17.0] 动态插件加载器"""

    @staticmethod
    def load_plugins(plugin_dir: str, base_class: Type, package_name: str = None) -> List[Type]:
        """
        扫描指定目录下的 Python 文件，并加载继承自 base_class 的类。
        """
        plugins = []
        if not os.path.exists(plugin_dir):
            tlog.warning(f"⚠️ [插件加载] 目录不存在: {plugin_dir}")
            return plugins

        tlog.debug(f"🔍 [插件探测] 正在扫描目录: {plugin_dir}")

        for filename in os.listdir(plugin_dir):
            if filename.endswith(".py") and not filename.startswith("__") and filename != "base.py":
                module_name = filename[:-3]
                file_path = os.path.join(plugin_dir, filename)

                try:
                    # 🚀 [V17.2] 优先尝试通过标准包路径导入，以完美支持相对导入
                    if package_name:
                        full_module_name = f"{package_name}.{module_name}"
                        try:
                            module = importlib.import_module(full_module_name)
                        except (ImportError, ModuleNotFoundError):
                            # 回退到物理路径加载
                            spec = importlib.util.spec_from_file_location(module_name, file_path)
                            module = importlib.util.module_from_spec(spec)
                            module.__package__ = package_name
                            spec.loader.exec_module(module)
                    else:
                        spec = importlib.util.spec_from_file_location(module_name, file_path)
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)

                    for name, obj in inspect.getmembers(module):
                        if inspect.isclass(obj) and issubclass(obj, base_class) and obj is not base_class:
                            plugins.append(obj)
                            tlog.info(f"✅ [插件发现] 已加载模块 {module_name} 中的插件类: {name}")
                except Exception as e:
                    tlog.error(f"❌ [插件加载失败] {filename}: {e}")

        return plugins

def discover_and_register(paths: List[str], package_name: str, base_class: Type, register_fn: callable):
    """
    📉 [兼容性垫片] 模拟旧版插件发现逻辑，确保核心组件平滑过渡。
    """
    for path in paths:
        found = PluginLoader.load_plugins(path, base_class, package_name=package_name)
        for cls in found:
            try:
                # 尝试标准注册
                register_fn(cls)
            except TypeError:
                # 兼容需要 (name, cls) 的注册函数
                name = getattr(cls, "PLUGIN_ID", cls.__name__.lower())
                register_fn(name, cls)
            except Exception as e:
                tlog.error(f"❌ [兼容层] 注册插件 {cls.__name__} 失败: {e}")
