#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - SSG Rendering Base
模块职责：定义 SSG 输出端渲染器的基类协议。
🛡️ [AEL-Iter-v5.3]：全链路解耦的渲染基座。
"""

from typing import Tuple, Dict, Any

class BaseSSGAdapter:
    """所有 SSG 渲染插件的抽象基类"""
    def __init__(self, theme_settings: Any = None):
        self.theme_settings = theme_settings

    def render(self, body: str, fm: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """
        [Contract] 执行特定 SSG 的语法转换与元数据增强。
        由子类实现。
        """
        return body, fm
