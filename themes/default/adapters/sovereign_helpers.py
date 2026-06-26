# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Sovereign Theme Adapter Helpers
模块职责：主权原生主题渲染适配器的辅助函数集合（解耦逻辑以符合 300 行红线）。
"""

import os
import logging
from typing import Dict, Any

logger = logging.getLogger("Illacme.plenipes")


def apply_template(adapter, content_html: str, fm: Dict[str, Any], lang: str, sub_path: str, is_default: bool = False) -> str:
    """物理模版注入系统"""
    # 🚀 [V15.0] 布局形态探测
    prefix = fm.get('route_prefix', 'docs')
    # 🚀 [V15.8] 布局控制权回传：用户显式指定优先，引擎自动推断兜底
    layout_type = fm.get('layout', get_layout_type(adapter, prefix, sub_path, fm))
    
    # 尝试寻找专用模版，如 docs.html, blog.html
    theme_dir = os.path.dirname(os.path.dirname(adapter.template_path))
    specific_tpl = os.path.join(theme_dir, "templates", f"{layout_type}.html")
    tpl_to_use = specific_tpl if os.path.exists(specific_tpl) else adapter.template_path
    
    if not os.path.exists(tpl_to_use):
        logger.warning(f"⚠️ [Sovereign] 模版不存在: {tpl_to_use}，回退至原始片段。")
        return content_html

    try:
        with open(tpl_to_use, 'r', encoding='utf-8') as f:
            template = f.read()
        
        # 🚀 [V15.9] 物理主权对齐：精准深度探测
        parts = [p for p in sub_path.split('/') if p and not p.endswith('.html')]
        depth = len(parts)
        root_path = "../" * depth if depth > 0 else "./"
        
        # 🚀 [V15.7] 布局形态感知注入：仅在文档页显示侧边栏
        sidebar_container = ""
        if layout_type == "docs":
            sidebar_html = build_sidebar(adapter, lang, prefix, sub_path, root_path)
            sidebar_container = f"""
    <!-- 📂 侧边栏导航 -->
    <aside class="sidebar-pioneer">
        <div class="sidebar-content">
            <div class="nav-tree">
                {sidebar_html}
            </div>
        </div>
    </aside>
            """

        # 🚀 [V11.7] 动态语种路由对齐
        lang_names = {"zh": "🇨🇳 简体中文", "en": "🇺🇸 English", "ja": "🇯🇵 日本語", "fr": "🇫🇷 Français", "de": "🇩🇪 Deutsch", "es": "🇪🇸 Español"}
        switcher_items = []
        hreflangs = fm.get('hreflangs', [])
        
        if not hreflangs:
            for l_code, l_name in lang_names.items():
                is_active = "selected" if l_code == lang else ""
                switcher_items.append(f'<option value="{root_path}{l_code}/index.html" {is_active}>{l_name}</option>')
        else:
            for item in hreflangs:
                l_code = item.get('lang')
                l_url = item.get('url', '').lstrip('/')
                if l_url and not l_url.endswith('.html'):
                    l_url += '.html'
                l_name = lang_names.get(l_code, l_code.upper())
                is_active = "selected" if l_code == lang else ""
                switcher_items.append(f'<option value="{root_path}{l_url}" {is_active}>{l_name}</option>')

        lang_switcher_html = "\n".join(switcher_items)
        
        # 🌐 [V15.9] 全息 UI 国际化矩阵
        ui_i18n = {
            "zh-Hans": {
                "nav_home": "门户", "nav_docs": "文档", "nav_blog": "博客", "nav_showcase": "案例", "nav_about": "关于",
                "search_placeholder": "搜索主权资产...", "footer_motto": "物理主权数字花园", "footer_slogan": "物理主权，自洽生长〫", "toc_title": "目录导航"
            },
            "en": {
                "nav_home": "Home", "nav_docs": "Docs", "nav_blog": "Blog", "nav_showcase": "Showcase", "nav_about": "About",
                "search_placeholder": "Search Assets...", "footer_motto": "Physical Sovereignty Digital Garden", "footer_slogan": "Physical Sovereignty, Self-Consistent Growth.", "toc_title": "Table of Contents"
            },
            "ja": {
                "nav_home": "ホーム", "nav_docs": "ドキュメント", "nav_blog": "ブログ", "nav_showcase": "ショーケース", "nav_about": "アバウト",
                "search_placeholder": "資産を検索...", "footer_motto": "物理的主権デジタルガーデン", "footer_slogan": "物理的主権、自己完結型の成長。", "toc_title": "目次"
            },
            "fr": {
                "nav_home": "Accueil", "nav_docs": "Documentation", "nav_blog": "Blog", "nav_showcase": "Vitrine", "nav_about": "À propos",
                "search_placeholder": "Rechercher...", "footer_motto": "Jardin numérique souverain", "footer_slogan": "Souveraineté physique, croissance cohérente.", "toc_title": "Table des matières"
            },
            "de": {
                "nav_home": "Startseite", "nav_docs": "Dokumentation", "nav_blog": "Blog", "nav_showcase": "Galerie", "nav_about": "Über uns",
                "search_placeholder": "Suchen...", "footer_motto": "Souveräner digitaler Garten", "footer_slogan": "Physische Souveränität, kohärentes Wachstum.", "toc_title": "Inhaltsverzeichnis"
            },
            "es": {
                "nav_home": "Inicio", "nav_docs": "Documentación", "nav_blog": "Blog", "nav_showcase": "Portafolio", "nav_about": "Acerca de",
                "search_placeholder": "Buscar...", "footer_motto": "Jardín digital soberano", "footer_slogan": "Soberanía física, crecimiento coherente.", "toc_title": "Tabla de contenidos"
            }
        }
        t = ui_i18n.get(lang, ui_i18n["en"])

        options = adapter.get_custom_options()
        site_name_val = options.get('site_name', 'Illacme Sovereign')
        accent_color_val = options.get('accent_color', '#00f5ff')
        enable_glass = options.get('enable_glassmorphism', True)
        github_repo_val = options.get('github_repo', '')
        logo_path_val = options.get('logo_path', '') or ''

        # 📷 [V12.0] 社交分享图暴光构建 (og:image / twitter:image)
        og_image_url = ""
        if adapter.engine and hasattr(adapter.engine, 'config') and adapter.engine.config.site_url:
            _base = adapter.engine.config.site_url.rstrip('/')
            og_image_url = f"{_base}/{logo_path_val.lstrip('/')}" if logo_path_val else f"{_base}/favicon.png"
        elif logo_path_val:
            og_image_url = logo_path_val if logo_path_val.startswith('http') else f"{root_path}{logo_path_val.lstrip('/')}"

        # © [V12.0] 版权信息自愈对齐
        import datetime as _dt
        _year = _dt.date.today().year
        _raw_cr = options.get('footer_copyright', '')
        footer_copyright_val = _raw_cr if _raw_cr else f"\u00a9 {_year} {site_name_val}. All Rights Reserved."

        # 🎨 [V12.0] Logo 智能渲染：有图片路径则渲染 <img>，否则保持默认 emoji
        if logo_path_val:
            logo_html_val = f'<img src="{root_path}{logo_path_val.lstrip("/")}" alt="{site_name_val}" class="logo-img" height="32">'
        else:
            logo_html_val = '<span class="logo-icon">🧬</span>'

        # 智能推导并渲染 CSS 霓虹发光与玻璃拟态降级
        glow_color = f"{accent_color_val}40" if (accent_color_val.startswith("#") and len(accent_color_val) == 7) else "rgba(0, 245, 255, 0.25)"
        custom_styles_html = f"""<style>
    :root {{
        --accent-color: {accent_color_val};
        --accent-glow: {glow_color};
    }}
"""
        if not enable_glass:
            custom_styles_html += """
    .glass-header {
        backdrop-filter: none !important;
        -webkit-backdrop-filter: none !important;
        background-color: var(--bg-color) !important;
    }
    .layout-showcase .card-pioneer, .search-dropdown {
        backdrop-filter: none !important;
        -webkit-backdrop-filter: none !important;
    }
    """

        from core.config.models.governance import PublishingMode
        is_global = True
        if adapter.engine and hasattr(adapter.engine, 'config') and hasattr(adapter.engine.config, 'governance'):
            is_global = (adapter.engine.config.governance.publishing_mode == PublishingMode.GLOBAL)

        if not is_global:
            custom_styles_html += """
    .lang-selector {
        display: none !important;
    }
    """

        custom_styles_html += "\n</style>"

        # 智能渲染 GitHub 社交挂载
        if github_repo_val:
            github_html = f"""<a href="{github_repo_val}" class="control-btn theme-btn github-btn" target="_blank" title="GitHub">
                    <span class="btn-icon">🐙</span>
                    <span class="btn-label">GitHub</span>
                </a>"""
        else:
            github_html = ""

        replacements = {
            "{{ title }}": fm.get('title', 'Untitled'),
            "{{ site_name }}": site_name_val,
            "{{ description }}": fm.get('description', ''),
            "{{ keywords }}": ", ".join(fm.get('keywords', [])) if isinstance(fm.get('keywords'), list) else fm.get('keywords', ''),
            "{{ content }}": content_html,
            "{{ sidebar_container }}": sidebar_container,
            "{{ language_switcher }}": lang_switcher_html,
            "{{ root_path }}": root_path,
            "{{ lang_code | default('zh') }}": lang,
            "{{ layout_class }}": f"layout-{layout_type}",
            "{{ canonical_url }}": f"/{lang if not is_default else ''}/{prefix}/{fm.get('slug', '')}.html".replace('//', '/'),
            "{{ custom_theme_styles }}": custom_styles_html,
            "{{ github_link_container }}": github_html,
            "{{ og_image_url }}": og_image_url,
            "{{ footer_copyright }}": footer_copyright_val,
            "{{ logo_html }}": logo_html_val,
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
    p_low = prefix.lower()
    slug_raw = fm.get('slug', '') if fm else ''
    slug = slug_raw.lower() if slug_raw else ""
    
    if p_low == "blog" or "blog" in slug: return "blog"
    if p_low == "showcase" or "showcase" in slug or (sub_path and "Showcase" in sub_path): return "showcase"
    if not sub_path or sub_path == "Index": return "page"
    return "docs"


def build_sidebar(adapter, lang: str, prefix: str, current_sub: str, root_path: str) -> str:
    """树状侧边栏自动测绘引擎"""
    cache_key = f"{lang}_{prefix}"
    # 访问 adapter 上的类级缓存
    if cache_key in adapter._sidebar_cache:
        return adapter._sidebar_cache[cache_key]

    from core.runtime.cli_bootstrap import get_global_engine
    engine = get_global_engine()
    if not engine: return ""
    
    db = engine.meta.data.get("documents", {})
    tree = {"_dirs": {}, "_files": []}
    
    for rel, info in db.items():
        doc_lang = info.get('language') or info.get('lang')
        if doc_lang and doc_lang != lang:
            continue
        
        doc_prefix = info.get('route_prefix')
        if doc_prefix != prefix and prefix != "docs": 
            continue
        
        slug = info.get('slug')
        if not slug: continue
        
        sub = info.get('sub_dir', '').strip('/')
        path_parts = sub.split('/') if sub else []
        
        curr = tree
        for part in path_parts:
            if part not in curr["_dirs"]: 
                curr["_dirs"][part] = {"_dirs": {}, "_files": []}
            curr = curr["_dirs"][part]
        
        curr["_files"].append({
            "title": info.get('title', slug),
            "url": f"{root_path}{prefix}/{sub}/{slug}.html".replace('//', '/')
        })

    def _render_tree(node, level=0):
        html = '<ul class="nav-list">'
        for dirname, contents in node.get("_dirs", {}).items():
            html += f'<li class="nav-group"><div class="group-title"><span>{dirname}</span><span class="group-toggle">▼</span></div>'
            html += _render_tree(contents, level + 1)
            html += '</li>'
        for f_info in node.get("_files", []):
            title = f_info['title']
            url = f_info['url']
            html += f'<li class="nav-item"><a href="{url}" class="nav-link">{title}</a></li>'
        html += '</ul>'
        return html

    result = _render_tree(tree)
    adapter._sidebar_cache[cache_key] = result
    return result


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
