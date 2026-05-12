"""
📥 收稿部经理 — 多源内容采集与生命周期管理。
协调各方言适配器完成稿件的发现、解析、验证与入库流程。
"""
import os
import importlib
import inspect
import pkgutil
from typing import List
from .base import BaseDialect, BaseSource
from .registry import ingress_registry

class IngressManager:
    """🚀 [V25.0] 输入层总控中心 (全动态发现版)"""
    
    @staticmethod
    def initialize(settings=None):
        """
        [Bootstrap] 全自动发现并注册插件 (Zero-Touch 版)
        """
        from core.utils.plugin_loader import discover_and_register
        
        # 定义扫描路径
        search_configs = [
            # 1. 核心内置 (Dialects)
            {"path": os.path.join(os.path.dirname(__file__), "dialect"), "pkg": "core.ingress.dialect", "base": BaseDialect, "reg": ingress_registry.register_dialect},
            # 2. 核心内置 (Sources)
            {"path": os.path.join(os.path.dirname(__file__), "source"), "pkg": "core.ingress.source", "base": BaseSource, "reg": ingress_registry.register_source},
            # 3. 🚀 全局扩展 (Adapters)
            {"path": os.path.abspath("adapters/ingress"), "pkg": "adapters.ingress", "base": (BaseDialect, BaseSource), "reg": None} # 混合注册逻辑
        ]

        for config in search_configs:
            path = config["path"]
            if not os.path.exists(path): continue
            
            if config["reg"]:
                discover_and_register([path], config["pkg"], config["base"], config["reg"])
            else:
                # 处理混合目录 (adapters/ingress)
                def hybrid_register(cls):
                    name = getattr(cls, "PLUGIN_ID", cls.__name__.lower())
                    if issubclass(cls, BaseDialect):
                        ingress_registry.register_dialect(name, cls)
                    elif issubclass(cls, BaseSource):
                        ingress_registry.register_source(name, cls)
                
                discover_and_register([path], config["pkg"], config["base"], hybrid_register)

# 初始化触发
IngressManager.initialize()

