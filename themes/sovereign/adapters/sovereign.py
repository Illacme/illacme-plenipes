#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Sovereign Theme Adapter
模块职责：主权原生主题渲染适配器。
🛡️ [AEL-Iter-v11.6]：实现零依赖、直出型的 Markdown to HTML 渲染逻辑。
🛡️ [SOP-01 & SOP-02]：自底向上物理拆分重构版本，单文件物理行数严格 ≤300 行。
"""

import os
import re
import logging
import threading
import markdown
from typing import Tuple, Dict, Any
from core.adapters.egress.ssg.base import BaseSSGAdapter
from core.utils.tracing import tlog
from .sovereign_compiler import (
    preprocess_markdown,
    rewrite_markdown_links,
    restore_containers,
)

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
        theme_name = getattr(theme_settings, 'name', 'sovereign')
        if theme_name == 'default':
            theme_name = 'sovereign'
        self.template_path = f"themes/{theme_name}/templates/layout.html"

    def has_autonomous_blog_engine(self) -> bool:
        """🚀 Sovereign 主题具备独立全息博客与展示流合成器"""
        return True

    def get_feature_slots(self) -> dict:
        """🚀 [V56.0] Sovereign 标准布局声明"""
        return {
            "docs": {
                "label": "📚 文档中心 (docs)",
                "single": "docs",
                "multi": "{lang}/docs"
            },
            "blog": {
                "label": "📰 博客文章 (blog)",
                "single": "blog",
                "multi": "{lang}/blog"
            },
            "showcase": {
                "label": "🎨 展示中心 (show)",
                "single": "showcase",
                "multi": "{lang}/showcase"
            },
            "pages": {
                "label": "📄 独立页面 (page)",
                "single": "",
                "multi": "{lang}"
            },
            "static": {
                "label": "📦 静态资源 (static)",
                "single": "static",
                "multi": "static"
            }
        }

    def get_output_schema(self) -> list:
        """🚀 [V11.2] 主权适配器强制开启双相分发 (源码 + 静态渲染)"""
        return ["source", "static"]

    @property
    def output_extension(self) -> str:
        return ".html"

    _assets_copied = False
    _assets_lock = threading.Lock()
    _sidebar_cache = {}

    def render(self, body: str, fm: Dict[str, Any], seo_data: Dict[str, Any] = None, target_lang: str = "en", sub_path: str = "") -> Tuple[str, Dict[str, Any]]:
        """[Sovereign] 执行 Markdown 到 HTML 的全量渲染与模版注入。"""
        # 1. 物理剥离 Frontmatter
        body = re.sub(r'^\s*---.*?---\s*', '', body, flags=re.DOTALL)

        # 2. 基础 SEO 处理
        if seo_data:
            fm = self.inject_seo(fm, seo_data.get('description', ''), seo_data.get('keywords', []))
        
        is_default = (target_lang == getattr(self, 'default_lang', 'zh'))

        # 3. Callouts 与 Mermaid 隔离预处理
        body, callouts, mermaids = preprocess_markdown(body, self)

        # 4. 双向链接与相对链接动态解析重写
        body = rewrite_markdown_links(body, self.engine, sub_path)

        # 5. Markdown 核心编译
        html_fragment = markdown.markdown(body, extensions=['extra', 'codehilite', 'toc', 'nl2br'])
        
        # 6. 还原 Callout 与 Mermaid HTML 容器
        html_fragment = restore_containers(html_fragment, callouts, mermaids)

        # 7. 加载物理模版 (layout.html)
        full_html = self._apply_template(html_fragment, fm, target_lang, sub_path, is_default=is_default)

        # 8. 资产原子搬运 (Singleton Copy) - 严禁污染 themes/ 母本目录
        self._sync_static_assets_once()

        return full_html, fm

    def _sync_static_assets_once(self):
        """🚀 [V11.8] 资产原子搬运 (Singleton Copy) - 严禁污染 themes/ 母本目录"""
        if not SovereignSSGAdapter._assets_copied:
            with SovereignSSGAdapter._assets_lock:
                if not SovereignSSGAdapter._assets_copied:
                    import shutil
                    theme_root = os.path.dirname(os.path.dirname(self.template_path))
                    static_src = os.path.join(theme_root, "static")
                    
                    dist_root = None
                    if self.engine and hasattr(self.engine, "paths"):
                        dist_root = self.engine.paths.get("site_dir")
                    
                    # 🛡️ [Rule 13] 若未配置输出路径（如纯内存单测），严禁回退至母本目录创建 dist/
                    if dist_root:
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

    def _apply_template(self, content_html: str, fm: Dict[str, Any], lang: str, sub_path: str, is_default: bool = False) -> str:
        """物理模版注入系统"""
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
        """[Sovereign] 呼号语法渲染"""
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
