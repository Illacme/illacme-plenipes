#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Theme Hook Manager
模块职责：负责驱动主题层级的生命周期钩子，实现引擎与主题业务逻辑的彻底解耦。
🛡️ [AEL-Iter-v1.0]：主权解耦钩子引擎。
"""

import os
import importlib.util
import logging

from core.utils.tracing import tlog

class ThemeHookManager:
    def __init__(self, engine):
        self.engine = engine
        self.theme_path = os.path.join("themes", engine.active_theme)
        self.hooks_file = os.path.join(self.theme_path, "hooks.py")
        self._hook_module = None

    def _load_hooks(self):
        """动态加载主题目录下的 hooks.py"""
        if self._hook_module is not None:
            return self._hook_module

        if not os.path.exists(self.hooks_file):
            return None

        try:
            spec = importlib.util.spec_from_file_location("theme_hooks", self.hooks_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            self._hook_module = module
            tlog.debug(f"🪝 [钩子引擎] 已成功装载主题钩子: {self.hooks_file}")
            return module
        except Exception as e:
            tlog.error(f"❌ [钩子引擎] 加载主题钩子失败 {self.hooks_file}: {e}")
            return None

    def trigger(self, hook_name, *args, **kwargs):
        """触发特定的生命周期钩子"""
        module = self._load_hooks()
        if not module:
            return

        func_name = f"on_{hook_name}"
        if hasattr(module, func_name):
            try:
                func = getattr(module, func_name)
                tlog.info(f"⚡ [钩子点火] 触发主题钩子: {func_name}")
                func(self.engine, *args, **kwargs)
            except Exception as e:
                tlog.error(f"🚨 [钩子异常] 执行 {func_name} 时发生故障: {e}")
