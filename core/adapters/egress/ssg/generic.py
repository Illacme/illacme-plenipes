#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Generic SSG Adapter
模块职责：通用模板渲染器，作为兜底或标准 Markdown 转换使用。
🛡️ [AEL-Iter-v5.3]：基于模板驱动的柔性处理器。
"""

from .base import BaseSSGAdapter

class GenericSSGAdapter(BaseSSGAdapter):
    PLUGIN_ID = "generic"
    DISPLAY_NAME = "Generic Markdown"
    VERSION = "V1.0"
    DESCRIPTION = "通用模板渲染器，作为兜底或标准 Markdown 转换使用，支持双相分发逻辑。"
    def get_output_schema(self) -> list:
        """🚀 [V11.2] 通用适配器默认开启双相分发 (源码 + 静态渲染)"""
        return ["source", "static"]

    def get_feature_slots(self) -> dict:
        """🚀 通用 / Universal 现代清晰路由槽协议 (修复多语言下 docs/blog/showcase 路径隔离)"""
        return {
            "docs": {"label": "📚 文档中心 (docs)", "single": "docs", "multi": "{lang}/docs"},
            "blog": {"label": "📰 博客文章 (blog)", "single": "blog", "multi": "{lang}/blog"},
            "showcase": {"label": "🎨 展示中心 (show)", "single": "showcase", "multi": "{lang}/showcase"},
            "pages": {"label": "📄 独立页面 (page)", "single": "", "multi": "{lang}"},
            "static": {"label": "📦 静态资源 (static)", "single": "static", "multi": "static"}
        }

    def render(self, body: str, fm: dict, seo_data: dict = None, target_lang: str = "en", sub_path: str = "") -> tuple:
        """通用渲染逻辑：完整解析 Markdown 方言（WikiLinks/Callouts/Mermaid）并注入现代自适应 HTML 页面外壳"""
        import re
        import markdown
        from .generic_templates import resolve_wikilinks, resolve_callouts, resolve_mermaids, render_html_page
        
        if seo_data:
            fm = self.inject_seo(fm, seo_data)

        # 1. 剥离可能存在的 Frontmatter
        clean_body = re.sub(r'^\s*---.*?---\s*', '', body, flags=re.DOTALL)

        # 2. 推导当前页面的相对根路径 (root_path)
        sub_clean = sub_path.replace('\\', '/').strip('/')
        parts = [p for p in sub_clean.split('/') if p and not p.endswith('.html')]
        depth = len(parts)
        root_path = "../" * depth if depth > 0 else "./"

        # 3. 预解析 Callouts 提示块与 Mermaid 图表
        processed_body, callouts = resolve_callouts(clean_body)
        processed_body, mermaids = resolve_mermaids(processed_body)

        # 4. 解析 Obsidian 双向链接 [[target|alias]]
        processed_body = resolve_wikilinks(processed_body, root_path=root_path, sub_path=sub_clean, engine=self.engine)

        # 5. Markdown 核心方言与扩展编译
        try:
            html_fragment = markdown.markdown(processed_body, extensions=['extra', 'codehilite', 'toc', 'nl2br'])
        except Exception:
            html_fragment = processed_body

        # 6. 还原 Callout 与 Mermaid HTML 容器
        for i, callout_h in enumerate(callouts):
            html_fragment = re.sub(rf'<p>@@CALLOUT:{i}@@(?:<br\s*/?>)?\s*</p>|@@CALLOUT:{i}@@', callout_h, html_fragment)
        for i, mermaid_h in enumerate(mermaids):
            html_fragment = re.sub(rf'<p>@@MERMAID:{i}@@(?:<br\s*/?>)?\s*</p>|@@MERMAID:{i}@@', mermaid_h, html_fragment)

        # 7. 组装全功能现代 Universal HTML 页面骨架
        site_name = "Illacme Press"
        i18n_cfg = None
        if self.engine and hasattr(self.engine, 'config'):
            if getattr(self.engine.config, 'site_name', None):
                site_name = self.engine.config.site_name
            i18n_cfg = getattr(self.engine.config, 'i18n_settings', None)

        full_html = render_html_page(
            html_content=html_fragment,
            fm=fm,
            target_lang=target_lang,
            sub_path=sub_path,
            root_path=root_path,
            site_name=site_name,
            i18n_cfg=i18n_cfg,
            engine=self.engine
        )

        # 🚀 [V120.0] 如果当前正在渲染博客归档首页，自动触发多语种三视图交互博客中心动态装配
        if sub_clean.endswith('blog/index.html') and self.engine:
            from .generic_templates import generate_dynamic_blog_archive
            generate_dynamic_blog_archive(self.engine)

        return full_html, fm

    def render_callout(self, g_type: str, title: str, body: str) -> str:
        icon_map = {"note": "ℹ️", "tip": "💡", "important": "📌", "warning": "⚠️", "caution": "🛑"}
        icon = icon_map.get(g_type.lower(), "💡")
        return f"""<div class="universal-callout callout-{g_type.lower()}">
    <div class="callout-header"><span class="callout-icon">{icon}</span> <strong class="callout-title">{title}</strong></div>
    <div class="callout-body"><p>{body}</p></div>
</div>"""

    def adapt_metadata(self, fm: dict, date_obj, author_name) -> dict:
        return fm
