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
        """
        return body, fm

    def adapt_metadata(self, fm: dict, date_obj, author_name) -> dict:
        """[Sovereignty] 物理元数据方言适配"""
        return fm

    def inject_seo(self, fm: dict, description: str, keywords: list) -> dict:
        """[SEO] 框架感知的 SEO 字段映射协议"""
        # 默认回退逻辑：标准的顶层注入
        if description: fm['description'] = description
        if keywords: fm['keywords'] = keywords
        return fm
