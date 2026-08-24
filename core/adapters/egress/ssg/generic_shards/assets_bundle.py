# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Generic SSG Adapter Assets Bundle Facade
模块职责：整合 Universal 主题核心 CSS 与客户端 JS 资产引擎分片。
"""

from core.adapters.egress.ssg.generic_shards.assets_css import get_universal_css
from core.adapters.egress.ssg.generic_shards.assets_js import get_universal_client_js

__all__ = ["get_universal_css", "get_universal_client_js"]
