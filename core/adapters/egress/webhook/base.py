#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Webhook Driver Base
模块职责：定义全域 Webhook 驱动的标准化协议。
🛡️ [AEL-Iter-v14.5]：实现高度解耦的生态破壁层插件化。
"""

from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseWebhookDriver(ABC):
    """
    🚀 Webhook 驱动抽象基座
    负责将引擎的标准文章元数据转换为特定平台的 Payload 格式。
    """
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}

    @abstractmethod
    def match(self, url: str) -> bool:
        """根据 URL 判断是否由本驱动处理"""
        pass

    @abstractmethod
    def build_payload(self, title: str, url_path: str, lang_code: str, ael_tag: str) -> Dict[str, Any]:
        """构建平台特定的 JSON Payload"""
        pass

class WebhookRegistry:
    """
    🏗️ Webhook 驱动注册中心
    """
    _drivers = []

    @classmethod
    def register(cls, name, driver_cls):
        cls._drivers.append(driver_cls())
        return driver_cls

    @classmethod
    def get_drivers(cls):
        return cls._drivers
