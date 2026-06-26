#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Sovereign Theme Adapter
模块职责：主权原生主题渲染适配器。
🛡️ [AEL-Iter-v11.6]：实现零依赖、直出型的 Markdown to HTML 渲染逻辑。
"""

import os
import logging
# import markdown  <-- 移至方法内部延迟导入，防止扫描时报错
import threading
from typing import Tuple, Dict, Any
from core.adapters.egress.ssg.base import BaseSSGAdapter

from core.utils.tracing import tlog
logger = logging.getLogger("Illacme.plenipes")

class SovereignSSGAdapter(BaseSSGAdapter):
    """
    🚀 默认原生适配器：将 Markdown 直接渲染为具有高级感视觉系统的静态 HTML。
    """
    PLUGIN_ID = 'sovereign'
    DISPLAY_NAME = 'Sovereign HTML'
    DESCRIPTION = '主权原生渲染引擎：零外部技术栈依赖，直出具有极致霓虹玻璃拟态美学的高级静态 HTML 知识库。'
    VERSION = 'V11.6'
    
    @classmethod
    def get_default_path_mappings(cls) -> Dict[str, str]:
        """🚀 [V76.0] 声明 Sovereign 适配器推荐的原生默认物理寻址映射"""
        return {
            'source_dir': "src/content",
            'site_dir': "dist",
            'assets_dir': "public/assets",
            'graph_json_dir': "public"
        }
    
    @classmethod
    def get_build_command(cls) -> str:
        """🚀 [V78.0] Sovereign 零依赖直出，无需 npm 构建，使用 echo 绕过"""
        return 'echo "Sovereign build completed"'
    
    def __init__(self, theme_settings: Any = None, engine=None):
        super().__init__(theme_settings, engine=engine)
        theme_name = getattr(theme_settings, 'name', 'default')
        self.template_path = f"themes/{theme_name}/templates/layout.html"
    def get_feature_slots(self) -> dict:
        """🚀 [V56.0] Sovereign 标准布局声明"""
        return {
            "docs": {
                "label": "文档中心",
                "single": "docs",
                "multi": "docs/{lang}"
            },
            "blog": {
                "label": "博客文章",
                "single": "blog",
                "multi": "blog/{lang}"
            },
            "pages": {
                "label": "独立页面",
                "single": "pages",
                "multi": "pages/{lang}"
            },
            "static": {
                "label": "静态资源",
                "single": "static",
                "multi": "static"
            }
        }

    def get_output_schema(self) -> list:
        """🚀 [V11.2] 主权适配器强制开启双相分发 (源码 + 静态渲染)"""
        return ["source", "static"]

    @property
    def output_extension(self) -> str:
        return ".html" # 强制 HTML 输出

    _assets_copied = False # 🚀 类级标志位，防止并发搬运冲突
    _assets_lock = threading.Lock() # 🛡️ [V16.5] 资产搬运专属物理锁
    _sidebar_cache = {} # 🚀 [V16.5] 侧边栏缓存，避免 O(N^2) 重复扫描

    def render(self, body: str, fm: Dict[str, Any], seo_data: Dict[str, Any] = None, target_lang: str = "en", sub_path: str = "") -> Tuple[str, Dict[str, Any]]:
        """
        [Sovereign] 执行 Markdown 到 HTML 的全量渲染与模版注入。
        """
        import re
        # 1. 物理剥离 Frontmatter
        body = re.sub(r'^\s*---.*?---\s*', '', body, flags=re.DOTALL)

        # 2. 基础 SEO 处理
        if seo_data:
            fm = self.inject_seo(fm, seo_data.get('description', ''), seo_data.get('keywords', []))
        
        # 3. 🚀 [V15.7] 物理主权对齐：深度探测自适应
        # 如果是默认语种，物理路径不包含语言前缀，深度减 1
        sub_dir = sub_path.strip('/')
        is_default = (target_lang == getattr(self, 'default_lang', 'zh'))
        depth = 0 if is_default else 1 
        
        if sub_dir:
            depth += len(sub_dir.split('/'))
        root_path = "../" * depth if depth > 0 else "./"

        # 4. 核心 Markdown 转换 (带 GFM 扩展)
        import markdown
        # 5. 🚀 方言预处理：隔离 Callouts
        callouts = []
        callout_pattern = re.compile(r'^>\s*\[!(\w+)\]\s*(.*)?\n((?:^>.*\n?)*)', re.MULTILINE)
        
        def _callout_collect(match):
            c_type = match.group(1)
            raw_title = match.group(2).strip().lstrip('> ').strip()
            content_lines = match.group(3).split('\n')
            clean_content = "\n".join([line.lstrip('> ').strip() for line in content_lines])
            
            rendered_title = markdown.markdown(raw_title) if raw_title else c_type.capitalize()
            rendered_title = re.sub(r'^<p>(.*)</p>$', r'\1', rendered_title)
            rendered_body = markdown.markdown(clean_content, extensions=['extra', 'nl2br'])
            
            html = self.render_callout(c_type, rendered_title, rendered_body)
            idx = len(callouts)
            callouts.append(html)
            return f"@@CALLOUT:{idx}@@\n"
        
        body = callout_pattern.sub(_callout_collect, body)
        html_fragment = markdown.markdown(body, extensions=['extra', 'codehilite', 'toc', 'nl2br'])
        
        # 7. 还原 Callout HTML 容器
        for i, html in enumerate(callouts):
            html_fragment = html_fragment.replace(f"<p>@@CALLOUT:{i}@@</p>", html)
            html_fragment = html_fragment.replace(f"@@CALLOUT:{i}@@", html)

        # 8. 加载物理模版 (layout.html)
        full_html = self._apply_template(html_fragment, fm, target_lang, sub_path, is_default=is_default)

        # 9. 🚀 [V11.8] 资产原子搬运 (Singleton Copy)
        if not SovereignSSGAdapter._assets_copied:
            with SovereignSSGAdapter._assets_lock:
                # 双重检查锁定 (DCL)
                if not SovereignSSGAdapter._assets_copied:
                    import shutil
                    theme_root = os.path.dirname(os.path.dirname(self.template_path))
                    static_src = os.path.join(theme_root, "static")
                    # 🚀 [V85.0] 支持动态 site_dir 配置，对准真正出盘的目标位置
                    dist_root = None
                    if self.engine and hasattr(self.engine, "paths"):
                        dist_root = self.engine.paths.get("site_dir")
                    if not dist_root:
                        dist_root = os.path.join(theme_root, "dist")
                    
                    static_dest = os.path.join(dist_root, "static")
                    
                    if os.path.exists(static_src):
                        try:
                            shutil.copytree(static_src, static_dest, dirs_exist_ok=True)
                            favicon_src = os.path.join(theme_root, "favicon.png")
                            if os.path.exists(favicon_src):
                                shutil.copy2(favicon_src, dist_root)
                            SovereignSSGAdapter._assets_copied = True
                            tlog.info(f"✨ [Sovereign] 全局资产单次同步完成: {static_dest}")
                        except Exception as e:
                            tlog.error(f"🛑 [Sovereign] 资产同步失败: {e}")

        return full_html, fm

    def _apply_template(self, content_html: str, fm: Dict[str, Any], lang: str, sub_path: str, is_default: bool = False) -> str:
        """物理模版注入系统 - [V15.0] 支持 Docusaurus 风格形态分发"""
        from .sovereign_helpers import apply_template
        return apply_template(self, content_html, fm, lang, sub_path, is_default)

    def _get_layout_type(self, prefix: str, sub_path: str, fm: Dict[str, Any] = None) -> str:
        """识别页面形态意图"""
        from .sovereign_helpers import get_layout_type
        return get_layout_type(self, prefix, sub_path, fm)

    def _build_sidebar(self, lang: str, prefix: str, current_sub: str, root_path: str) -> str:
        """🚀 [V15.0] 树状侧边栏自动测绘引擎"""
        from .sovereign_helpers import build_sidebar
        return build_sidebar(self, lang, prefix, current_sub, root_path)

    def render_callout(self, c_type: str, title: str, body: str) -> str:
        """[Sovereign] 呼号语法渲染：将 Obsidian 风格 Callouts 转化为美观的 HTML 容器"""
        from .sovereign_helpers import render_callout
        return render_callout(c_type, title, body)

    def adapt_metadata(self, fm: dict, date_obj, author_name) -> dict:
        """[Sovereignty] 元数据清洗"""
        fm['author'] = author_name
        if date_obj:
            fm['date_formatted'] = date_obj.strftime("%Y-%m-%d")
        return fm

    def get_i18n_path_template(self, source_type: str = "docs") -> str:
        """主权路径模版：直接将语种作为根目录"""
        return "{lang}/{sub_dir}"
