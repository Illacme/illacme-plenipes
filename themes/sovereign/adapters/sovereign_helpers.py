# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Sovereign Theme Adapter Helpers (Hub)
模块职责：主权原生主题渲染适配器的核心协调中枢，承接模版注入、页面形态推导及子模块统一路由导出。
遵循 SOP-02 模块化物理拆分规范，物理行数严格约束于 300 行红线以内。
"""

import os
import logging
from typing import Dict, Any
from core.runtime.cli_bootstrap import get_global_engine
from .sovereign_i18n import get_ui_i18n
from .sovereign_ui import (
    calculate_reading_meta,
    build_breadcrumbs,
    build_article_meta,
    build_doc_pagination  # noqa: F401 re-export if needed
)
from .sovereign_sidebar import build_sidebar
from .sovereign_showcase import transform_showcase_multi_view
from .sovereign_switcher import build_language_switcher
from .sovereign_nav_builder import (
    build_prev_next_pagination,
    build_custom_styles,
    build_footer_copyright,
    build_main_nav,
    build_canonical_url
)

# 🚀 对外统一符号导出契约（确保外部调用方零破坏）
__all__ = [
    "apply_template",
    "get_layout_type",
    "build_sidebar",
    "render_callout",
    "transform_showcase_multi_view"
]

logger = logging.getLogger("Illacme.plenipes")


def apply_template(adapter, content_html: str, fm: Dict[str, Any], lang: str, sub_path: str, is_default: bool = False) -> str:
    """物理模版注入系统"""
    # 智能频道前缀推导：优先读取 Frontmatter 显式配置，缺省时根据 sub_path 物理路径自动识别
    if 'route_prefix' in fm:
        prefix = fm.get('route_prefix') or ""
    else:
        _clean_parts = [p for p in sub_path.replace('\\', '/').strip('/').split('/') if p and not p.endswith('.html')]
        if _clean_parts and len(_clean_parts[0]) <= 3 and _clean_parts[0].isalpha() and _clean_parts[0].islower():
            _clean_parts = _clean_parts[1:]
        prefix = _clean_parts[0] if _clean_parts else ""

    # 🛡️ [V16.1] 路由前缀防御清洗：若 route_prefix 被错误写入了含语种段（如 zh/docs, en/blog），
    # 则过滤掉 2 字母语种前缀，只保留最后一个有效功能段（如 docs, blog, showcase）。
    _prefix_parts = [p for p in prefix.replace('\\', '/').split('/') if p]
    if len(_prefix_parts) > 1:
        _lead = _prefix_parts[0]
        if len(_lead) <= 3 and _lead.isalpha() and _lead.islower():
            prefix = '/'.join(_prefix_parts[1:])

    layout_type = fm.get('layout', get_layout_type(adapter, prefix, sub_path, fm))

    theme_dir = os.path.dirname(os.path.dirname(adapter.template_path))
    specific_tpl = os.path.join(theme_dir, "templates", f"{layout_type}.html")
    tpl_to_use = specific_tpl if os.path.exists(specific_tpl) else adapter.template_path

    if not os.path.exists(tpl_to_use):
        logger.warning(f"⚠️ [Sovereign] 模版不存在: {tpl_to_use}，回退至原始片段。")
        return content_html

    try:
        with open(tpl_to_use, 'r', encoding='utf-8') as f:
            template = f.read()

        parts = [p for p in sub_path.replace('\\', '/').split('/') if p and not p.endswith('.html')]
        depth = len(parts)
        root_path = "../" * depth if depth > 0 else "./"

        # 📂 侧边栏构建 (仅文档页)
        sidebar_container = ""
        if layout_type == "docs":
            sidebar_html = build_sidebar(adapter, lang, prefix, sub_path, root_path, fm=fm)
            sidebar_container = f"""
    <aside class="sidebar-pioneer">
        <div class="sidebar-content">
            <div class="nav-tree">
                {sidebar_html}
            </div>
        </div>
    </aside>
            """

        # 🌐 语种主权对齐 (将 "auto" 解析为真实的默认母语，杜绝虚假语种泄露至 URL 与 UI)
        default_code = getattr(adapter, 'default_lang', 'zh')
        if not default_code or default_code == "auto":
            default_code = "zh"
        effective_lang = default_code if lang in ("auto", "", None) else lang

        # 🚀 [语种自愈感知] 若 sub_path 显式以目标语种开头 (如 en/docs/..., ja/blog/...)，强制对齐 effective_lang 为该语种
        _clean_sub_parts = sub_path.replace('\\', '/').strip('/').split('/')
        if _clean_sub_parts and len(_clean_sub_parts[0]) <= 3 and _clean_sub_parts[0].isalpha() and _clean_sub_parts[0].islower():
            if _clean_sub_parts[0] != default_code:
                effective_lang = _clean_sub_parts[0]

        # 🌐 全息多语言 UI 字典
        t = get_ui_i18n(effective_lang)
        options = adapter.get_custom_options() if hasattr(adapter, 'get_custom_options') else {}
        if not isinstance(options, dict):
            options = {}
        site_name_val = str(options.get('site_name', 'Illacme Sovereign'))
        accent_color_val = str(options.get('accent_color', '#00f5ff'))
        enable_glass = bool(options.get('enable_glassmorphism', True))
        github_repo_val = str(options.get('github_repo', ''))
        logo_path_val = str(options.get('logo_path', '') or '')

        # 🚀 [V105.1] 读取网址组织形态 (flat/prefix/nested)
        sv_dir_mode = 'nested'
        sv_engine = getattr(adapter, 'engine', None) or get_global_engine()
        if sv_engine and hasattr(sv_engine, 'config'):
            sv_trans_cfg = getattr(sv_engine.config, 'translation', None)
            sv_dir_mode = getattr(sv_trans_cfg, 'slug_dir_mode', 'nested') if sv_trans_cfg else 'nested'

        slug = fm.get('slug', '')
        sub_dir = fm.get('sub_dir', '').strip('/')

        # 🌐 动态语种切换器构建
        current_lang_name, lang_switcher_html = build_language_switcher(
            adapter=adapter,
            effective_lang=effective_lang,
            default_code=default_code,
            fm=fm,
            prefix=prefix,
            sub_dir=sub_dir,
            slug=slug,
            layout_type=layout_type,
            root_path=root_path,
            sv_dir_mode=sv_dir_mode
        )

        # 📊 阅读时间与文章元数据
        reading_meta = calculate_reading_meta(content_html)
        doc_title = fm.get('title', 'Untitled')

        # 🧭 顶部导航合成
        nav_links_data = options.get('nav_links_i18n', {}).get(effective_lang) or options.get('nav_links', [])
        nav_lang_prefix = f"{effective_lang}/" if (effective_lang != default_code or getattr(adapter, 'force_source_prefix', False)) else ""

        breadcrumbs_html = ""
        article_meta_html = ""
        # 🛡️ 仅文档 (docs) 与博客单篇详情页 (blog) 渲染面包屑与阅读元数据，关于页 (page/about) 与案例页 (showcase) 保持纯净单页
        if slug and slug != "index" and layout_type not in ("page", "showcase", "home") and slug != "about":
            breadcrumbs_html = build_breadcrumbs(effective_lang, prefix, sub_path, doc_title, root_path, nav_lang_prefix=nav_lang_prefix)
            article_meta_html = build_article_meta(fm, effective_lang, reading_meta)

        # 🎨 案例页多视图自适应包装 (排除博客聚合中心)
        if (layout_type == "showcase" or "card-pioneer" in content_html) and "card-pioneer" in content_html and "blog-app" not in content_html and layout_type != "blog":
            content_html = transform_showcase_multi_view(content_html, effective_lang)

        # 📖 上一篇/下一篇导航
        doc_pagination_html = build_prev_next_pagination(
            adapter=adapter,
            layout_type=layout_type,
            slug=slug,
            fm=fm,
            effective_lang=effective_lang,
            default_code=default_code,
            root_path=root_path,
            nav_lang_prefix=nav_lang_prefix,
            sv_dir_mode=sv_dir_mode
        )

        # 🎨 Logo 与社交元素
        if logo_path_val:
            clean_logo_p = logo_path_val.lstrip("/")
            if logo_path_val.startswith("http"):
                logo_html_val = f'<img src="{logo_path_val}" alt="{site_name_val}" class="logo-img" height="36">'
            else:
                logo_html_val = f'<img src="{root_path}{clean_logo_p}" alt="{site_name_val}" class="logo-img" height="36">'
        else:
            logo_html_val = '<span class="logo-icon">🧬</span>'

        github_html = f'<a href="{github_repo_val}" target="_blank" rel="noopener noreferrer" class="social-icon-link github-btn" title="GitHub">🐙</a>' if github_repo_val else ''
        custom_styles_html = build_custom_styles(accent_color_val, enable_glass)
        footer_copyright_val = build_footer_copyright(options, site_name_val)

        # 🧭 主导航容器注入
        main_nav_container = build_main_nav(
            nav_links_data=nav_links_data,
            effective_lang=effective_lang,
            default_code=default_code,
            adapter=adapter,
            sub_path=sub_path,
            prefix=prefix,
            slug=slug,
            layout_type=layout_type,
            root_path=root_path,
            nav_lang_prefix=nav_lang_prefix,
            sv_dir_mode=sv_dir_mode,
            t=t
        )

        canonical_url = build_canonical_url(
            effective_lang=effective_lang,
            default_code=default_code,
            adapter=adapter,
            prefix=prefix,
            sub_dir=sub_dir,
            slug=slug,
            layout_type=layout_type,
            sv_dir_mode=sv_dir_mode
        )

        replacements = {
            "{{ title }}": doc_title,
            "{{ site_name }}": site_name_val,
            "{{ current_lang_name }}": current_lang_name,
            "{{ description }}": fm.get('description', options.get('site_description', '')),
            "{{ keywords }}": ", ".join(fm.get('keywords', [])) if isinstance(fm.get('keywords'), list) else (fm.get('keywords') or ''),
            "{{ content }}": content_html,
            "{{ sidebar_container }}": sidebar_container,
            "{{ language_switcher }}": lang_switcher_html,
            "{{ root_path }}": root_path,
            "{{ lang_code | default('zh') }}": effective_lang,
            "{{ layout_class }}": f"layout-{layout_type}",
            "{{ canonical_url }}": canonical_url,
            "{{ custom_theme_styles }}": custom_styles_html,
            "{{ github_link_container }}": github_html,
            "{{ main_nav_container }}": main_nav_container,
            "{{ footer_copyright }}": footer_copyright_val,
            "{{ logo_html }}": logo_html_val,
            "{{ nav_home_url }}": f"{root_path}{nav_lang_prefix}index.html".replace('//', '/'),
            "{{ breadcrumbs }}": breadcrumbs_html,
            "{{ article_meta }}": article_meta_html,
            "{{ doc_pagination }}": doc_pagination_html,
            "{{ t_nav_home }}": t["nav_home"],
            "{{ t_nav_docs }}": t["nav_docs"],
            "{{ t_nav_blog }}": t["nav_blog"],
            "{{ t_nav_showcase }}": t["nav_showcase"],
            "{{ t_nav_about }}": t["nav_about"],
            "{{ t_search_placeholder }}": t["search_placeholder"],
            "{{ t_footer_motto }}": t["footer_motto"],
            "{{ t_footer_slogan }}": t["footer_slogan"],
            "{{ t_toc_title }}": t["toc_title"]
        }

        for key, val in replacements.items():
            template = template.replace(key, str(val))
        return template
    except Exception as e:
        logger.error(f"🛑 [Sovereign] 渲染模版失败: {e}")
        return content_html


def get_layout_type(adapter, prefix: str, sub_path: str, fm: Dict[str, Any] = None) -> str:
    """识别页面形态意图"""
    p_low = prefix.lower() if prefix else ""
    slug_raw = fm.get('slug', '') if fm else ''
    slug = slug_raw.lower() if slug_raw else ""

    if p_low == "blog" or "blog" in slug:
        return "blog"
    if p_low == "showcase" or "showcase" in slug or (sub_path and "showcase" in sub_path.lower()):
        return "showcase"
    if p_low == "about" or "about" in slug or (sub_path and "about" in sub_path.lower()):
        return "about"
    if not sub_path or sub_path == "Index" or slug in ("index", "home", ""):
        return "page"
    return "docs"


def render_callout(c_type: str, title: str, body: str) -> str:
    """呼号语法渲染"""
    icon_map = {"info": "ℹ️", "warning": "⚠️", "error": "🚫", "tip": "💡", "note": "📝"}
    icon = icon_map.get(c_type.lower(), "📝")
    return f"""
    <div class="callout callout-{c_type.lower()}">
        <div class="callout-header">
            <span class="callout-icon">{icon}</span>
            <span class="callout-title">{title or c_type.capitalize()}</span>
        </div>
        <div class="callout-body">{body}</div>
    </div>
    """
