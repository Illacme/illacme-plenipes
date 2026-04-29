#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Pipeline Step Registry
模块职责：管理处理管线中的原子化步骤，支持 Zero-Touch 自发现。
🛡️ [AEL-Iter-v5.3]：全透明流水线注册机。
"""

import logging
from typing import Dict, Type
from core.editorial.runner import PipelineStep
from core.utils.plugin_loader import discover_and_register

from core.utils.tracing import tlog

class StepRegistry:
    """🚀 流水线步骤注册中心"""
    _steps: Dict[str, Type[PipelineStep]] = {}

    @classmethod
    def register(cls, name_or_cls):
        """🚀 增强型注册器：支持 @register("name") 和 discover_and_register(cls)"""
        if isinstance(name_or_cls, str):
            # 模式 A: 装饰器工厂
            def wrapper(step_class: Type[PipelineStep]):
                cls._steps[name_or_cls] = step_class
                tlog.debug(f"⛓️ [管线插件] 已注册步骤: {name_or_cls}")
                return step_class
            return wrapper
        else:
            # 模式 B: 直接类注册 (兼容 discover_and_register)
            step_class = name_or_cls
            name = getattr(step_class, "PLUGIN_ID", step_class.__name__.lower())
            cls._steps[name] = step_class
            tlog.debug(f"⛓️ [管线插件] 已兼容注册步骤: {name}")
            return step_class

    @classmethod
    def get_step(cls, name: str) -> Type[PipelineStep]:
        return cls._steps.get(name)

    @classmethod
    def get_all_names(cls) -> list:
        return list(cls._steps.keys())

# 🚀 [Zero-Touch] 自动扫描并注册管线步骤
import os
root_dir = os.path.dirname(__file__)
base_package = __name__.rsplit('.', 1)[0]

# 1. 扫描当前目录 (core.editorial)
discover_and_register([root_dir], base_package, PipelineStep, StepRegistry.register)

# 2. 扫描 steps 子目录 (core.editorial.steps)
steps_dir = os.path.join(root_dir, "steps")
if os.path.exists(steps_dir):
    discover_and_register([steps_dir], f"{base_package}.steps", PipelineStep, StepRegistry.register)
