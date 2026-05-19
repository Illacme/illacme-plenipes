#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Syndication Base
模块职责：定义第三方平台分发器的基类协议。
🛡️ [AEL-Iter-v5.3]：解耦的分发协议基座。
"""
import abc
import logging
from typing import Dict, Any

from core.utils.tracing import tlog

class BaseSyndicator(abc.ABC):
    """所有分发平台插件的抽象基类"""
    def __init__(self, config: Any, *args, **kwargs):
        self.config = config
        
        # 🚀 [V75.1] 弹性参数提取：支持多种历史调用格式的自动对准与自愈
        timeout = 10
        site_url = ""
        
        # 优先提取 kwargs
        if "timeout" in kwargs:
            timeout = kwargs["timeout"]
        if "site_url" in kwargs:
            site_url = kwargs["site_url"]
            
        # 如果有 positional arguments
        if args:
            second_arg = args[0]
            if isinstance(second_arg, dict):
                timeout = second_arg.get("timeout", 10)
                site_url = second_arg.get("site_url", "")
            elif isinstance(second_arg, (int, float)):
                timeout = int(second_arg)
            elif isinstance(second_arg, str):
                site_url = second_arg
                
            if len(args) > 1:
                third_arg = args[1]
                if isinstance(third_arg, str):
                    site_url = third_arg
                elif isinstance(third_arg, (int, float)):
                    timeout = int(third_arg)

        self.timeout = timeout
        self.site_url = site_url


    def is_enabled(self, rel_path: str = None, lang_code: str = None) -> bool:
        """检查插件是否激活"""
        return getattr(self.config, 'enabled', False)

    @abc.abstractmethod
    def format_payload(self, title: str, slug: str, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        [Contract] 组装平台特定的 Payload 数据结构。
        """
        pass

    @abc.abstractmethod
    def push(self, payload: Dict[str, Any]):
        """
        [Contract] 执行具体的推流逻辑。
        """
        pass
