#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Pipeline Step Registry
模块职责：管理处理管线中的原子化步骤，支持 Zero-Touch 自发现。
🛡️ [AEL-Iter-v5.3]：全透明流水线注册机。
"""

import logging
from typing import Dict, Type
from .runner import PipelineStep
from core.utils.plugin_loader import discover_and_register

logger = logging.getLogger("Illacme.plenipes")

class StepRegistry:
    """🚀 流水线步骤注册中心"""
    _steps: Dict[str, Type[PipelineStep]] = {}

    @classmethod
    def register(cls, name: str, step_class: Type[PipelineStep]):
        cls._steps[name] = step_class
        logger.debug(f"⛓️ [管线插件] 已注册步骤: {name}")

    @classmethod
    def get_step(cls, name: str) -> Type[PipelineStep]:
        return cls._steps.get(name)

    @classmethod
    def get_all_names(cls) -> list:
        return list(cls._steps.keys())

# 🚀 [Zero-Touch] 自动扫描并注册当前包下的所有 PipelineStep
# 注意：package_path 为当前文件所在目录
import os
package_path = [os.path.dirname(__file__)]
discover_and_register(package_path, __name__.rsplit('.', 1)[0], PipelineStep, StepRegistry.register)
