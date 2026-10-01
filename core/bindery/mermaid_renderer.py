# -*- coding: utf-8 -*-
"""
Illacme Plenipes - Sovereign Mermaid Headless Renderer
模块职责：将文稿中的 Mermaid 文本图表离线编译为高清 PNG 图像。
适用场景：Word 审校印本 (.docx) 导出时将流程图/架构图转换为原生图片嵌入。
🛡️ [SOP-01 规范]：单文件严格 <= 300 行。
"""

import os
import hashlib
from typing import Optional, Dict
from core.utils.tracing import tlog

# 进程内图表渲染缓存，避免重复渲染耗时
_RENDER_CACHE: Dict[str, bytes] = {}
_VENDOR_JS_CACHE: Optional[str] = None


class MermaidRenderer:
    """基于本地脱机引擎的高清 Mermaid 图片渲染器"""

    @classmethod
    def get_vendor_js(cls) -> Optional[str]:
        """获取本地脱机 mermaid.min.js 内容"""
        global _VENDOR_JS_CACHE
        if _VENDOR_JS_CACHE is not None:
            return _VENDOR_JS_CACHE

        candidates = [
            os.path.abspath("web/dashboard/vendor/mermaid.min.js"),
            os.path.abspath("themes/sovereign/static/vendor/mermaid/mermaid.min.js"),
        ]
        for path in candidates:
            if os.path.isfile(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        _VENDOR_JS_CACHE = f.read()
                        return _VENDOR_JS_CACHE
                except Exception as e:
                    tlog.warning(f"⚠️ 读取本地 mermaid.min.js 失败 ({path}): {e}")

        tlog.error("❌ 未能在本地找到 mermaid.min.js 脱机依赖")
        return None

    @classmethod
    def _execute_headless_render(cls, clean_code: str, vendor_js: str, scale: int, timeout_ms: int) -> Optional[bytes]:
        """在纯净独立线程中执行 Playwright 页面渲染与截图"""
        from playwright.sync_api import sync_playwright

        html_tpl = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ background: #ffffff; display: inline-block; padding: 18px 24px; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
    .mermaid {{ font-size: 14px; line-height: 1.5; }}
  </style>
  <script>{vendor_js}</script>
</head>
<body>
  <div class="mermaid" id="diagram-container">
{clean_code}
  </div>
  <script>
    mermaid.initialize({{
      startOnLoad: true,
      theme: 'default',
      securityLevel: 'loose',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
    }});
  </script>
</body>
</html>"""

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(device_scale_factor=scale)
            page.set_content(html_tpl)
            page.wait_for_selector(".mermaid svg", timeout=timeout_ms)
            elem = page.query_selector(".mermaid")
            if not elem:
                browser.close()
                return None
            png_bytes = elem.screenshot()
            browser.close()
            return png_bytes

    @classmethod
    def render_to_png(cls, mermaid_code: str, scale: int = 2, timeout_ms: int = 6000) -> Optional[bytes]:
        """将 Mermaid 代码渲染为高清晰度 PNG 图片字节流（自动隔离在独立线程中，规避 asyncio 事件循环冲突）"""
        clean_code = (mermaid_code or "").strip()
        if not clean_code:
            return None

        cache_key = hashlib.sha256(f"{clean_code}::{scale}".encode("utf-8")).hexdigest()
        if cache_key in _RENDER_CACHE:
            return _RENDER_CACHE[cache_key]

        vendor_js = cls.get_vendor_js()
        if not vendor_js:
            return None

        try:
            from concurrent.futures import ThreadPoolExecutor
            with ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(cls._execute_headless_render, clean_code, vendor_js, scale, timeout_ms)
                png_bytes = future.result(timeout=(timeout_ms / 1000.0) + 10.0)

            if png_bytes:
                _RENDER_CACHE[cache_key] = png_bytes
                tlog.info(f"✨ [Mermaid 渲染] 成功生成高清图表 (字节数: {len(png_bytes)})")
                return png_bytes

        except Exception as e:
            tlog.warning(f"⚠️ [Mermaid 渲染] 无法渲染图表为图片 (将平滑降级为代码卡片): {e}")

        return None
