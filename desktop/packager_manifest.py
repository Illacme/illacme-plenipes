# -*- coding: utf-8 -*-
"""
Illacme Plenipes - Desktop Application Packager Manifest
模块职责：定义桌面独立单体客户端编译清单，确保全部核心运行依赖与装订引擎 100% 自闭环打包。
🛡️ [SOP-01 规范]：单文件行数严格 ≤ 300 行。
"""

import os
import platform
from typing import List, Tuple

# 🚀 基础 Web API 网关与异步协议依赖
BASE_CORE_IMPORTS: List[str] = [
    "uvicorn.logging",
    "uvicorn.loops",
    "uvicorn.loops.auto",
    "uvicorn.protocols",
    "uvicorn.protocols.http",
    "uvicorn.protocols.http.auto",
    "uvicorn.protocols.websockets",
    "uvicorn.protocols.websockets.auto",
    "uvicorn.lifespan.on",
    "fastapi",
    "python_multipart",
    "multipart",
    "websockets",
    "orjson",
    "yaml",
    "jinja2",
    "watchdog",
    "watchdog.observers",
    "watchdog.events",
    "cryptography",
    "requests",
    "requests.adapters",
    "urllib3",
    "qrcode",
    "tiktoken",
    "sqlite3",
]

# 📚 原生装帧排版与多格式出版导出引擎 (Word/PDF/EPUB/Markdown)
BINDERY_PUBLISHING_IMPORTS: List[str] = [
    "markdown",
    "markdown.extensions",
    "markdown.extensions.extra",
    "markdown.extensions.tables",
    "markdown.extensions.fenced_code",
    "markdown.extensions.toc",
    "latex2mathml",
    "docx",
    "docx.oxml",
    "docx.oxml.ns",
    "docx.opc.constants",
    "docx.shared",
    "reportlab",
    "reportlab.pdfgen",
    "reportlab.pdfgen.canvas",
    "reportlab.platypus",
    "reportlab.lib",
    "reportlab.lib.pagesizes",
    "reportlab.lib.colors",
    "reportlab.lib.styles",
    "pypdf",
    "pypdf.generic",
    "fitz",
    "pymupdf",
    "mathml2omml",
    "PIL",
    "PIL.Image",
    "PIL.ImageDraw",
    "PIL.ImageFont",
]

# 🧬 动态加载插件与主权原生装帧适配器
DYNAMIC_PLUGIN_IMPORTS: List[str] = [
    "themes.sovereign.adapters.sovereign",
    "core.adapters.egress.ebook.docx",
    "core.adapters.egress.ebook.pdf",
    "core.adapters.egress.ebook.epub",
    "core.bindery.bindery_writer",
    "core.bindery.bindery_dispatcher",
    "adapters.egress.publishers.netlify_utils",
    "adapters.egress.publishers.vercel_utils",
    "adapters.egress.publishers.cloudflare_utils",
    "core.utils.network_sniffer",
    "services.api.routes.gov.context_shards.social_shards.cookie_prober",
]


def get_hidden_imports(cur_sys: str = None) -> List[str]:
    """
    🧬 汇集并返回全量 PyInstaller 隐藏导入列表。
    涵盖基础基座、电子书装订、图像引擎及系统托盘原生库。
    """
    if cur_sys is None:
        cur_sys = platform.system()

    imports: List[str] = []
    imports.extend(BASE_CORE_IMPORTS)
    imports.extend(BINDERY_PUBLISHING_IMPORTS)
    imports.extend(DYNAMIC_PLUGIN_IMPORTS)

    # 动态系统托盘与原生 Webview 嗅探
    try:
        import importlib.util
        if importlib.util.find_spec("pystray") is not None:
            imports.append("pystray")
            sub_pkg = {
                "Darwin": "pystray._darwin",
                "Windows": "pystray._win32",
                "Linux": "pystray._xorg"
            }.get(cur_sys)
            if sub_pkg:
                imports.append(sub_pkg)
    except Exception:
        pass

    try:
        import importlib.util
        if importlib.util.find_spec("webview") is not None:
            imports.append("webview")
    except Exception:
        pass

    # 数组去重并保持拓扑相对稳定
    seen = set()
    deduped: List[str] = []
    for item in imports:
        if item not in seen:
            seen.add(item)
            deduped.append(item)

    return deduped


def get_data_mappings(themes_src: str = "themes") -> List[Tuple[str, str]]:
    """
    📦 返回打包所需的静态资源与配置资产物理映射关系。
    """
    mappings: List[Tuple[str, str]] = [
        ("web/dashboard", "web/dashboard"),
        (themes_src, "themes"),
        ("configs", "configs"),
    ]
    return mappings

