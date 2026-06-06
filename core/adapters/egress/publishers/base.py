#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Base Publisher Interface
模块职责：定义全球分发渠道的统一工业接口。
🛡️ [AEL-Iter-v11.0]：闭环发布架构基座。
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Type

from core.utils.tracing import tlog

class BasePublisher(ABC):
    """
    🚀 抽象发布器基座
    所有分发渠道（Cloudflare, Git, S3 等）必须继承此类并实现核心方法。
    """
    PLUGIN_ID: str = "generic_publisher"
    DISPLAY_NAME: str = "Publisher"
    DESCRIPTION: str = "分发适配器插件"

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

    def validate_config(self) -> List[str]:
        """
        🛡️ 校验配置完整性。
        子类可覆写此方法，返回错误信息列表。空列表表示配置合法。
        """
        return []

    def get_deploy_url(self):
        """
        🔗 返回预期的部署 URL。
        子类可覆写此方法，基于当前配置推导出站点 URL。
        """
        return None

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

    @classmethod
    def list_active(cls) -> List[str]:
        return cls.list_active_targets()

    @classmethod
    def get_publisher_class(cls, name: str):
        return cls._targets.get(name)

    @classmethod
    def get_all_publishers(cls) -> Dict[str, Type['BasePublisher']]:
        return cls._targets
