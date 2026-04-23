#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Syndication Base
模块职责：定义第三方平台分发器的基类协议。
🛡️ [AEL-Iter-v5.3]：解耦的分发协议基座（支持自治组装逻辑）。
"""

import logging
from typing import Dict, Any

logger = logging.getLogger("Illacme.plenipes")

class BaseSyndicator:
    """所有分发平台插件的抽象基类"""
    def __init__(self, config: Any, timeout: int = 10):
        self.config = config
        self.timeout = timeout

    def is_enabled(self) -> bool:
        """检查插件是否激活"""
        return getattr(self.config, 'enabled', False)

    def format_payload(self, title: str, body: str, tags: list, url: str, desc: str = "") -> Dict[str, Any]:
        """
        [Contract] 组装平台特定的 Payload 数据结构。
        由子类实现。
        """
        return {}

    def push(self, payload: Dict[str, Any]):
        """
        [Contract] 执行具体的推流逻辑。
        由子类实现。
        """
        pass
