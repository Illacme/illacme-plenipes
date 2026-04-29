#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Base Publisher Interface
模块职责：定义全球分发渠道的统一工业接口。
🛡️ [AEL-Iter-v11.0]：闭环发布架构基座。
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List

from core.utils.tracing import tlog

class BasePublisher(ABC):
    """
    🚀 抽象发布器基座
    所有分发渠道（Cloudflare, Git, S3 等）必须继承此类并实现核心方法。
    """
    def __init__(self, config: Dict[str, Any], sys_config: Dict[str, Any] = None):
        self.config = config
        self.sys_config = sys_config or {}
        self.enabled = config.get("enabled", False)

    @abstractmethod
    def push(self, bundle_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        🚀 执行物理发布
        :param bundle_path: 待发布的本地资产包/目录路径
        :param metadata: 包含 ael_iter_id, lang_code, slug 等元数据的矩阵
        :return: 包含部署状态和访问 URL 的响应报文
        """
        pass

    def is_healthy(self) -> bool:
        """检查发布通道连通性"""
        return True

class PublisherRegistry:
    """
    🏗️ 发布器注册中心
    负责管理和发现所有可用的发布插件。
    """
    _targets = {}

    @classmethod
    def register(cls, name: str):
        def wrapper(publisher_cls):
            cls._targets[name] = publisher_cls
            return publisher_cls
        return wrapper

    @classmethod
    def get_publisher(cls, name: str):
        return cls._targets.get(name)

    @classmethod
    def list_active_targets(cls) -> List[str]:
        return list(cls._targets.keys())
