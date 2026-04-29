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
        [Bootstrap] 全自动发现并注册插件
        """
        # 1. 扫描内置与外部适配器目录
        # 我们扫描 core.ingress.dialect, core.ingress.source 以及项目根目录下的 adapters.ingress
        search_paths = [
            ("core.ingress.dialect", os.path.join(os.path.dirname(__file__), "dialect")),
            ("core.ingress.source", os.path.join(os.path.dirname(__file__), "source")),
            ("adapters.ingress", os.path.abspath("adapters/ingress"))
        ]

        for package_name, folder in search_paths:
            if not os.path.exists(folder):
                continue
                
            for _, name, is_pkg in pkgutil.iter_modules([folder]):
                if is_pkg: continue
                
                try:
                    module_path = f"{package_name}.{name}"
                    module = importlib.import_module(module_path)
                    
                    # 自动探测并注册类
                    for _, obj in inspect.getmembers(module):
                        if inspect.isclass(obj) and not inspect.isabstract(obj):
                            # 注册方言
                            if issubclass(obj, BaseDialect):
                                reg_name = name.lower()
                                ingress_registry.register_dialect(reg_name, obj)
                                
                            # 注册物理来源
                            elif issubclass(obj, BaseSource):
                                reg_name = name.lower()
                                ingress_registry.register_source(reg_name, obj)
                except Exception as e:
                    # 在此处由于尚未初始化 Logger，使用 print 或静默
                    pass

# 初始化触发
IngressManager.initialize()

