#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omni-Hub Plugin System - Base Publisher
定义外部插件的稳定接口，确保核心引擎与外部扩展的解耦。
"""

from abc import ABC, abstractmethod
from typing import Dict, Any

class BasePublisher(ABC):
    """
    🚀 外部发布器基座 (V17.0)
    所有放置在 plugins/publishers/ 目录下的插件必须继承此类。
    """
    def __init__(self, config: Dict[str, Any], sys_config: Dict[str, Any] = None):
        self.config = config
        self.sys_config = sys_config or {}
        self.enabled = config.get("enabled", False)

    @abstractmethod
    def push(self, bundle_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        🚀 执行物理发布
        :param bundle_path: 待发布的本地资产包路径
        :param metadata: 任务元数据
        :return: 发布结果
        """
        pass

    def is_healthy(self) -> bool:
        """检查发布通道连通性"""
        return True
