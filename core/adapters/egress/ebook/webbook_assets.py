# -*- coding: utf-8 -*-
"""
Illacme Plenipes - WebBook Embedded Assets & Runtime Driver
模块职责：提供单文件离线网页书 (WebBook) 的高质感 CSS 样式、多语言全局无缝切换与移动端沉浸式运行时。
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""

from core.adapters.egress.ebook.webbook_css import get_webbook_css
from core.adapters.egress.ebook.webbook_js import get_webbook_js


class WebBookAssets:
    """🎨 WebBook 离线内联资产构建器 (门面)"""

    @staticmethod
    def get_embedded_css() -> str:
        """获取嵌入式 CSS 样式表"""
        return get_webbook_css()

    @staticmethod
    def get_embedded_js() -> str:
        """获取嵌入式运行时 JS 脚本"""
        return get_webbook_js()
