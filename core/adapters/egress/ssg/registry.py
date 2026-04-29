#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - SSG Registry
模块职责：管理所有 SSG 渲染插件的注册与发现。
🛡️ [AEL-Iter-v5.3]：全链路透明化的渲染注册机。
"""

import logging
from typing import Dict, Type
from .base import BaseSSGAdapter

from core.utils.tracing import tlog

class SSGRegistry:
    """🚀 SSG 渲染插件注册中心"""
    _renderers: Dict[str, Type[BaseSSGAdapter]] = {}

    @classmethod
    def register(cls, name: str, renderer_class: Type[BaseSSGAdapter]):
        cls._renderers[name] = renderer_class
        tlog.debug(f"🎨 [渲染插件] 已注册 SSG 适配器: {name}")

    @classmethod
    def get_renderer(cls, name: str) -> Type[BaseSSGAdapter]:
        return cls._renderers.get(name)

    @classmethod
    def get_all_names(cls) -> list:
        return list(cls._renderers.keys())
