# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Sovereign Theme Adapter Helpers
模块职责：主权原生主题渲染适配器的辅助函数集合（解耦逻辑以符合 300 行红线）。
"""

import os
import logging
from typing import Dict, Any
from core.runtime.cli_bootstrap import get_global_engine
from .sovereign_i18n import get_ui_i18n, get_language_display_names
from .sovereign_ui import (
    calculate_reading_meta,
    build_breadcrumbs,
    build_article_meta,
    build_doc_pagination
)

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
        _sv_dir_mode = 'nested'
        _sv_engine = getattr(adapter, 'engine', None) or get_global_engine()
        if _sv_engine and hasattr(_sv_engine, 'config'):
            _sv_trans_cfg = getattr(_sv_engine.config, 'translation', None)
            _sv_dir_mode = getattr(_sv_trans_cfg, 'slug_dir_mode', 'nested') if _sv_trans_cfg else 'nested'
        
        # 🌐 动态语种切换器构建 (仅展示当前治理中心配置的活跃语种)
        lang_names = get_language_display_names()
        switcher_items = []
        hreflangs = {item.get('lang'): item.get('url', '') for item in fm.get('hreflangs', []) if isinstance(item, dict)}
        
        # 收集系统激活的有效语种
        active_langs = set()
        if hreflangs:
            for h_l in hreflangs.keys():
                active_langs.add(default_code if h_l == "auto" else h_l)
        if adapter.engine and hasattr(adapter.engine, 'i18n') and adapter.engine.i18n:
            if getattr(adapter.engine.i18n, 'source', None):
                src_c = adapter.engine.i18n.source.lang_code
                active_langs.add(default_code if src_c == "auto" else src_c)
            if getattr(adapter.engine.i18n, 'targets', None):
                for t_item in adapter.engine.i18n.targets:
                    if getattr(t_item, 'lang_code', None):
                        active_langs.add(t_item.lang_code)
        if not active_langs:
            active_langs = {default_code, 'en', effective_lang}
        
        active_langs.discard("auto")
        active_langs.add(default_code)

        slug = fm.get('slug', '')
        sub_dir = fm.get('sub_dir', '').strip('/')
        
        # 按照默认语言在前、目标语言在后的顺序排序
        sorted_active_langs = sorted(list(active_langs), key=lambda c: (0 if c == default_code else 1, c))

        current_lang_name = lang_names.get(effective_lang, effective_lang.upper())

        for l_code in sorted_active_langs:
            l_name = lang_names.get(l_code, f"🌐 {l_code}")
            is_active = (l_code == effective_lang)
            active_cls = " active" if is_active else ""
            active_check = '<span class="lang-check">✓</span>' if is_active else ""
            if l_code in hreflangs and hreflangs[l_code]:
                target_url = hreflangs[l_code].lstrip('/')
                # 🛡️ 清洗 hreflangs 中可能残留的 page/ 虚假段
                if target_url.startswith("page/"):
                    target_url = target_url[len("page/"):]
                elif "/page/" in target_url:
                    target_url = target_url.replace('/page/', '/')
                if l_code == default_code and not getattr(adapter, 'force_source_prefix', False):
                    # 🛡️ 默认语言根目录对齐：剥离错误的 zh/ 等前缀
                    if target_url.startswith(f"{default_code}/"):
                        target_url = target_url[len(f"{default_code}/"):]
                if not target_url.endswith('.html'):
                    target_url += '.html'
                full_dest = f"{root_path}{target_url}".replace('//', '/')
            elif l_code == default_code and "auto" in hreflangs and hreflangs["auto"]:
                target_url = hreflangs["auto"].lstrip('/')
                if target_url.startswith("page/"):
                    target_url = target_url[len("page/"):]
                elif "/page/" in target_url:
                    target_url = target_url.replace('/page/', '/')
                if not getattr(adapter, 'force_source_prefix', False):
                    if target_url.startswith(f"{default_code}/"):
                        target_url = target_url[len(f"{default_code}/"):]
                if not target_url.endswith('.html'):
                    target_url += '.html'
                full_dest = f"{root_path}{target_url}".replace('//', '/')
            else:
                # 智能计算对等相对路径 (遵循通用路由前缀契约：无前缀则为根目录页面，有前缀则为频道子目录)
                clean_p = (prefix or "").strip("/\\").lower()
                sub_segment = f"{sub_dir}/" if sub_dir else ""
                is_global_h = (slug in ("index", "home", "") and not clean_p and not sub_segment and layout_type not in ('docs', 'blog', 'showcase'))
                is_channel_h = (slug in ("index", "home", "") and not is_global_h)
                channel_n = clean_p or (layout_type if layout_type in ('docs', 'blog', 'showcase') else 'docs')
                
                lang_seg = f"{l_code}/" if l_code != default_code else ""
                if is_global_h:
                    dest = f"{lang_seg}index.html"
                elif is_channel_h:
                    if _sv_dir_mode == 'flat':
                        dest = f"{lang_seg}{channel_n}.html"
                    elif _sv_dir_mode == 'prefix':
                        dest = f"{lang_seg}{channel_n}-index.html"
                    else:
                        dest = f"{lang_seg}{channel_n}/index.html"
                elif slug:
                    if _sv_dir_mode == 'flat':
                        dest = f"{lang_seg}{slug}.html"
                    elif _sv_dir_mode == 'prefix':
                        _p_slug = slug if slug.startswith(f"{channel_n}-") else f"{channel_n}-{slug}"
                        dest = f"{lang_seg}{_p_slug}.html"
                    else:
                        dest = f"{lang_seg}{clean_p}/{sub_segment}{slug}.html" if clean_p else f"{lang_seg}{sub_segment}{slug}.html"
                else:
                    dest = f"{lang_seg}index.html"
                
                full_dest = f"{root_path}{dest}".replace('//', '/')
            
            switcher_items.append(f"""<a href="{full_dest}" class="lang-menu-item{active_cls}">
                <span class="lang-code-badge">{l_code.upper()}</span>
                <span class="lang-name-text">{l_name}</span>
                {active_check}
            </a>""")

        lang_switcher_html = "\n".join(switcher_items)

        # 📊 阅读时间与文章元数据
        reading_meta = calculate_reading_meta(content_html)
        doc_title = fm.get('title', 'Untitled')
        
        # 🧭 顶部导航合成
        nav_links_data = options.get('nav_links_i18n', {}).get(effective_lang) or options.get('nav_links', [])
        nav_lang_prefix = f"{effective_lang}/" if (effective_lang != default_code or getattr(adapter, 'force_source_prefix', False)) else ""
        
        breadcrumbs_html = ""
        article_meta_html = ""
        doc_pagination_html = ""
        # 🛡️ 仅文档 (docs) 与博客单篇详情页 (blog) 渲染面包屑与阅读元数据，关于页 (page/about) 与案例页 (showcase) 保持纯净单页
        if slug and slug != "index" and layout_type not in ("page", "showcase", "home") and slug != "about":
            breadcrumbs_html = build_breadcrumbs(effective_lang, prefix, sub_path, doc_title, root_path, nav_lang_prefix=nav_lang_prefix)
            article_meta_html = build_article_meta(fm, effective_lang, reading_meta)

        # 🎨 案例页多视图自适应包装 (排除博客聚合中心)
        if (layout_type == "showcase" or "card-pioneer" in content_html) and "card-pioneer" in content_html and "blog-app" not in content_html and layout_type != "blog":
            content_html = transform_showcase_multi_view(content_html, effective_lang)

        # 📖 上一篇/下一篇导航 (针对 docs 文档与 blog 博客详情页)
        if layout_type in ("docs", "blog") and slug and slug != "index":
            prev_d = fm.get('prev_doc')
            next_d = fm.get('next_doc')
            if not prev_d and not next_d:
                engine = getattr(adapter, 'engine', None) or get_global_engine()
                if engine and hasattr(engine, 'meta'):
                    channel_docs = []
                    db = engine.meta.get_documents_snapshot() if hasattr(engine.meta, 'get_documents_snapshot') else (getattr(engine.meta, 'data', {}).get("documents", {}))
                    for r_p, d_info in db.items():
                        r_p_clean = r_p.replace('\\', '/')
                        is_match = False
                        if layout_type == "docs":
                            is_match = (d_info.get('target_slot') == 'docs' or d_info.get('route_prefix') == 'docs' or r_p_clean.lower().startswith('docs/'))
                        elif layout_type == "blog":
                            is_match = (d_info.get('target_slot') == 'blog' or d_info.get('route_prefix') == 'blog' or r_p_clean.lower().startswith('blog/'))
                        
                        if is_match:
                            d_slug = d_info.get('slug') or os.path.splitext(os.path.basename(r_p_clean))[0]
                            if d_slug and d_slug not in ("index", "home"):
                                d_title = d_info.get('title') or d_slug
                                if effective_lang != default_code and isinstance(d_info.get('translations'), dict):
                                    t_t = d_info.get('translations', {}).get(effective_lang, {}).get('seo', {}).get('og_title')
                                    if t_t: d_title = t_t
                                
                                d_date = str(d_info.get('persistent_date') or d_info.get('date') or '')
                                # 🚀 [V105.1] 上下篇导航链接统一路由解析
                                if _sv_dir_mode == 'flat':
                                    d_nav_url = f"{root_path}{nav_lang_prefix}{d_slug}.html".replace('//', '/')
                                elif _sv_dir_mode == 'prefix':
                                    _d_p_slug = d_slug if d_slug.startswith(f"{layout_type}-") else f"{layout_type}-{d_slug}"
                                    d_nav_url = f"{root_path}{nav_lang_prefix}{_d_p_slug}.html".replace('//', '/')
                                else:
                                    d_nav_url = f"{root_path}{nav_lang_prefix}{layout_type}/{d_slug}.html".replace('//', '/')
                                channel_docs.append({
                                    "slug": d_slug,
                                    "title": d_title,
                                    "date": d_date,
                                    "url": d_nav_url
                                })
                    
                    if layout_type == "blog":
                        channel_docs.sort(key=lambda x: str(x.get('date', '')), reverse=True)
                    else:
                        channel_docs.sort(key=lambda x: (x.get('slug', ''), x.get('title', '')))
                    
                    curr_idx = -1
                    for idx, c_d in enumerate(channel_docs):
                        if c_d['slug'] == slug:
                            curr_idx = idx
                            break
                    if curr_idx != -1:
                        if curr_idx > 0:
                            prev_d = {"title": channel_docs[curr_idx - 1]['title'], "url": channel_docs[curr_idx - 1]['url']}
                        if curr_idx < len(channel_docs) - 1:
                            next_d = {"title": channel_docs[curr_idx + 1]['title'], "url": channel_docs[curr_idx + 1]['url']}
            
            doc_pagination_html = build_doc_pagination(prev_d, next_d, effective_lang)

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
        glow_color = f"{accent_color_val}40" if (accent_color_val.startswith("#") and len(accent_color_val) == 7) else "rgba(0, 245, 255, 0.25)"
        custom_styles_html = f"""<style>
    :root {{
        --accent-color: {accent_color_val};
        --accent-cyan: {accent_color_val};
        --accent-glow: {glow_color};
    }}
"""
        if not enable_glass:
            custom_styles_html += """
    .glass-header, .layout-showcase .card-pioneer, .search-dropdown {
        backdrop-filter: none !important;
        -webkit-backdrop-filter: none !important;
    }
    """
        custom_styles_html += "\n</style>"

        # 🎨 页脚与版权信息构建
        footer_copyright_raw = str(options.get('footer_copyright', f"&copy; {site_name_val}."))
        if "Illacme Sovereign" in footer_copyright_raw and site_name_val != "Illacme Sovereign":
            footer_copyright_raw = footer_copyright_raw.replace("Illacme Sovereign", site_name_val)
        import datetime
        current_year = datetime.datetime.now().year
        footer_copyright_val = footer_copyright_raw.replace("{year}", str(current_year)).replace("{site_name}", site_name_val)

        # 🧭 主导航容器注入 (兼容直接指定 / 自定义 route_matrix / fallback)
        clean_sub_path = sub_path.replace('\\', '/').strip('/')
        clean_prefix = (prefix or "").strip('/\\')
        curr_slug = (slug or "").lower()

        if nav_links_data:
            main_nav_html_items = []
            for item in nav_links_data:
                u = item.get('url', '#')
                text = item.get('text') or item.get('label') or ''
                is_ext = item.get('external', False) or u.startswith("http://") or u.startswith("https://")
                item_slot = item.get('slot', '')
                
                # 🎯 智能判定当前项是否处于 Active 激活状态
                is_active = False
                if not is_ext:
                    u_clean = u.strip('/')
                    if item_slot == "docs" or u_clean in ("docs", "docs.html", "docs-index.html", "docs/index.html"):
                        is_active = (clean_prefix == "docs" or layout_type == "docs" or "docs/" in clean_sub_path or clean_sub_path in ("docs.html", "docs-index.html", "docs/index.html"))
                    elif item_slot == "blog" or u_clean in ("blog", "blog.html", "blog-index.html", "blog/index.html"):
                        is_active = (clean_prefix == "blog" or layout_type == "blog" or "blog/" in clean_sub_path or clean_sub_path in ("blog.html", "blog-index.html", "blog/index.html"))
                    elif item_slot == "showcase" or u_clean in ("showcase", "showcase.html", "showcase-index.html", "showcase/index.html"):
                        is_active = (clean_prefix == "showcase" or layout_type == "showcase" or "showcase/" in clean_sub_path or clean_sub_path in ("showcase.html", "showcase-index.html", "showcase/index.html"))
                    elif u_clean in ("about", "about.html"):
                        is_active = (curr_slug == "about" or clean_sub_path.endswith("about.html"))
                    else:
                        if u_clean.endswith('.html'):
                            target_slug = os.path.splitext(os.path.basename(u_clean))[0]
                            if curr_slug == target_slug or clean_sub_path.endswith(u_clean):
                                is_active = True
                        elif curr_slug == u_clean or clean_sub_path.endswith(f"{u_clean}.html"):
                            is_active = True
                
                # 🚀 构造相对链接
                if not is_ext and not u.startswith("#"):
                    u_clean = u.lstrip('/')
                    if u_clean.startswith(f"{effective_lang}/"):
                        u_clean = u_clean[len(f"{effective_lang}/"):]
                    
                    u_slug = u_clean.rstrip('/')
                    is_page_slot = (item_slot in ("pages", "page") or u_slug in ("about", "terms", "privacy", "disclaimer", "contact"))

                    if u_clean.endswith('.html') or u_clean == "index.html":
                        full_u = f"{root_path}{nav_lang_prefix}{u_clean}".replace('//', '/')
                    elif is_page_slot:
                        full_u = f"{root_path}{nav_lang_prefix}{u_slug}.html".replace('//', '/')
                    elif u.endswith('/') or (item_slot and item_slot not in ("pages", "page")) or u_slug in ("docs", "blog", "showcase", "tutorials"):
                        if _sv_dir_mode == 'flat':
                            full_u = f"{root_path}{nav_lang_prefix}{u_slug}.html".replace('//', '/')
                        elif _sv_dir_mode == 'prefix':
                            full_u = f"{root_path}{nav_lang_prefix}{u_slug}-index.html".replace('//', '/')
                        else:
                            full_u = f"{root_path}{nav_lang_prefix}{u_slug}/index.html".replace('//', '/')
                    else:
                        full_u = f"{root_path}{nav_lang_prefix}{u_slug}.html".replace('//', '/')
                else:
                    full_u = u
                
                target_attr = ' target="_blank" rel="noopener noreferrer"' if is_ext else ''
                active_class = ' class="active"' if is_active else ''
                main_nav_html_items.append(f'<a href="{full_u}"{active_class}{target_attr}>{text}</a>')
            main_nav_container = "\n                    ".join(main_nav_html_items)
        else:
            # 🚀 [V105.1] fallback 导航统一遵循三模态设计原则
            if _sv_dir_mode == 'flat':
                _blog_p = f"{nav_lang_prefix}blog.html".replace('//', '/')
                _docs_p = f"{nav_lang_prefix}docs.html".replace('//', '/')
                _showcase_p = f"{nav_lang_prefix}showcase.html".replace('//', '/')
            elif _sv_dir_mode == 'prefix':
                _blog_p = f"{nav_lang_prefix}blog-index.html".replace('//', '/')
                _docs_p = f"{nav_lang_prefix}docs-index.html".replace('//', '/')
                _showcase_p = f"{nav_lang_prefix}showcase-index.html".replace('//', '/')
            else:
                _blog_p = f"{nav_lang_prefix}blog/index.html".replace('//', '/')
                _docs_p = f"{nav_lang_prefix}docs/index.html".replace('//', '/')
                _showcase_p = f"{nav_lang_prefix}showcase/index.html".replace('//', '/')

            is_docs_active = ' class="active"' if (clean_prefix == "docs" or layout_type == "docs" or "docs/" in clean_sub_path or clean_sub_path in ("docs.html", "docs-index.html", "docs/index.html")) else ''
            is_blog_active = ' class="active"' if (clean_prefix == "blog" or layout_type == "blog" or "blog/" in clean_sub_path or clean_sub_path in ("blog.html", "blog-index.html", "blog/index.html")) else ''
            is_showcase_active = ' class="active"' if (clean_prefix == "showcase" or layout_type == "showcase" or "showcase/" in clean_sub_path or clean_sub_path in ("showcase.html", "showcase-index.html", "showcase/index.html")) else ''
            is_about_active = ' class="active"' if (curr_slug == "about" or "about.html" in clean_sub_path) else ''
            
            main_nav_container = f"""<a href="{root_path}{_docs_p}"{is_docs_active}>{t["nav_docs"]}</a>
                    <a href="{root_path}{_blog_p}"{is_blog_active}>{t["nav_blog"]}</a>
                    <a href="{root_path}{_showcase_p}"{is_showcase_active}>{t["nav_showcase"]}</a>
                    <a href="{root_path}{nav_lang_prefix}about.html"{is_about_active}>{t["nav_about"]}</a>"""

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
        }
        # 🚀 [V105.1] Canonical URL 感知网址组织形态与频道首页收敛规则 (遵循 RouteManager 三模态)
        _is_source_lang = (effective_lang == default_code)
        _force_src_prefix = getattr(adapter, 'force_source_prefix', False)
        _need_lang_prefix = not _is_source_lang or _force_src_prefix
        _lang_prefix_seg = f"{effective_lang}/" if _need_lang_prefix else ""

        clean_p = (prefix or "").strip("/\\").lower()
        is_global_home = (slug in ('', 'index', 'home') and not clean_p and not sub_dir and layout_type not in ('docs', 'blog', 'showcase'))
        is_channel_home = (slug in ('', 'index', 'home') and not is_global_home)
        channel_name = clean_p or (layout_type if layout_type in ('docs', 'blog', 'showcase') else 'docs')

        if is_global_home:
            _canonical = f"/{_lang_prefix_seg}index.html".replace('//', '/')
        elif is_channel_home:
            if _sv_dir_mode == 'flat':
                _canonical = f"/{_lang_prefix_seg}{channel_name}.html".replace('//', '/')
            elif _sv_dir_mode == 'prefix':
                _canonical = f"/{_lang_prefix_seg}{channel_name}-index.html".replace('//', '/')
            else:
                _canonical = f"/{_lang_prefix_seg}{channel_name}/index.html".replace('//', '/')
        else:
            if _sv_dir_mode == 'flat':
                _canonical = f"/{_lang_prefix_seg}{slug}.html".replace('//', '/')
            elif _sv_dir_mode == 'prefix':
                _p_slug = slug if slug.startswith(f"{channel_name}-") else f"{channel_name}-{slug}"
                _canonical = f"/{_lang_prefix_seg}{_p_slug}.html".replace('//', '/')
            else:
                _sub_seg = f"{sub_dir}/" if sub_dir else ""
                _canonical = f"/{_lang_prefix_seg}{clean_p}/{_sub_seg}{slug}.html".replace('//', '/')
        replacements["{{ canonical_url }}"] = _canonical
        replacements.update({
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
        })

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
    
    if p_low == "blog" or "blog" in slug: return "blog"
    if p_low == "showcase" or "showcase" in slug or (sub_path and "showcase" in sub_path.lower()): return "showcase"
    if p_low == "about" or "about" in slug or (sub_path and "about" in sub_path.lower()): return "about"
    if not sub_path or sub_path == "Index" or slug in ("index", "home", ""): return "page"
    return "docs"


def build_sidebar(adapter, lang: str, prefix: str, current_sub: str, root_path: str, fm: Dict[str, Any] = None) -> str:
    """树状侧边栏自动测绘引擎"""
    from core.runtime.cli_bootstrap import get_global_engine
    from core.utils.language_hub import LanguageHub
    engine = getattr(adapter, 'engine', None) or get_global_engine()
    if not engine: return ""
    
    default_lang_code = getattr(engine.route_manager, 'default_lang', 'zh') if hasattr(engine, 'route_manager') else 'zh'
    force_prefix = getattr(engine.route_manager, 'force_source_prefix', False) if hasattr(engine, 'route_manager') else False

    iso_curr = LanguageHub.resolve_to_iso(lang)
    iso_default = LanguageHub.resolve_to_iso(default_lang_code)
    sidebar_lang_prefix = f"{lang}/" if (iso_curr != iso_default or force_prefix) else ""

    db = {}
    if hasattr(engine, 'meta'):
        if hasattr(engine.meta, 'get_documents_snapshot'):
            db = engine.meta.get_documents_snapshot()
        elif hasattr(engine.meta, 'sqlite') and hasattr(engine.meta.sqlite, 'get_all_documents'):
            db = engine.meta.sqlite.get_all_documents()
        elif hasattr(engine.meta, 'data'):
            db = engine.meta.data.get("documents", {})

    target_channel = prefix.strip("/\\").lower() if prefix else "docs"
    curr_clean = current_sub.replace('\\', '/').strip('/')
    curr_slug = (fm or {}).get('slug', '')
    
    docs_list = []
    for rel, info in db.items():
        rel_clean = rel.replace('\\', '/')
        
        # 🛡️ 严格频道隔离：防止根目录独立单页 (如 about.md, index.md, welcome-to-illacme-plenipes.md) 或其他栏目渗透
        doc_slot = (info.get('target_slot') or '').lower()
        doc_prefix = (info.get('route_prefix') or '').lower()
        
        if doc_slot in ('blog', 'showcase', 'page', 'about', 'external', 'home'):
            is_in_channel = (doc_slot == target_channel)
        elif target_channel == "docs":
            is_in_channel = (
                doc_slot == "docs" or
                doc_prefix == "docs" or
                rel_clean.lower().startswith("docs/")
            )
        else:
            is_in_channel = (
                doc_slot == target_channel or
                doc_prefix == target_channel or
                rel_clean.lower().startswith(f"{target_channel}/")
            )
        
        if not is_in_channel:
            continue
        
        stem = os.path.splitext(os.path.basename(rel_clean))[0]
        slug = info.get('slug') or stem
        if not slug or slug in ("index", "home") or stem in ("index", "home"):
            continue
        
        sub = info.get('sub_dir', '').strip('/')
        
        # 🛡️ 标题提取自愈：优先使用已有 title，若为空或纯文件名/slug，则从物理原稿 frontmatter 读取
        doc_title = info.get('title')
        if not doc_title or doc_title in (slug, stem):
            vault_root = getattr(engine, 'vault_root', '')
            if vault_root:
                phys_p = os.path.join(vault_root, rel)
                if os.path.exists(phys_p):
                    try:
                        with open(phys_p, 'r', encoding='utf-8') as pf:
                            from core.utils import extract_frontmatter
                            p_fm, _ = extract_frontmatter(pf.read())
                            if p_fm.get('title'):
                                doc_title = p_fm.get('title')
                    except Exception:
                        pass
        if not doc_title:
            doc_title = slug

        if lang != default_lang_code and isinstance(info.get('translations'), dict):
            trans_info = info.get('translations', {}).get(lang, {})
            t_title = trans_info.get('seo', {}).get('og_title') or trans_info.get('title')
            if t_title:
                doc_title = t_title

        if hasattr(engine, 'route_manager'):
            rel_p = engine.route_manager.resolve_physical_path("", lang, target_channel, sub, slug, ".html", source_type=target_channel)
            clean_rel = rel_p.replace('\\', '/').lstrip('/')
            doc_url = f"{root_path}{clean_rel}".replace('//', '/')
        else:
            sub_part = f"{sub}/" if sub else ""
            doc_url = f"{root_path}{sidebar_lang_prefix}{target_channel}/{sub_part}{slug}.html".replace('//', '/')

        
        # 🎯 激活项高精度命中：支持 slug 精准比对与路径匹配
        is_active = bool(
            (curr_slug and slug == curr_slug) or
            curr_clean.endswith(f"{slug}.html") or 
            curr_clean.endswith(f"/{slug}") or 
            curr_clean == slug or
            curr_clean == f"{target_channel}/{slug}"
        )
        
        doc_order = info.get('order') or info.get('weight') or 999
        
        docs_list.append({
            "title": doc_title,
            "slug": slug,
            "sub": sub,
            "url": doc_url,
            "order": doc_order,
            "is_active": is_active
        })

    if not docs_list:
        return ""

    docs_list.sort(key=lambda x: (x.get('order', 999), x.get('slug', '')))

    tree = {"_dirs": {}, "_files": []}
    for doc in docs_list:
        sub = doc["sub"]
        path_parts = sub.split('/') if sub else []
        curr = tree
        for part in path_parts:
            if part not in curr["_dirs"]:
                curr["_dirs"][part] = {"_dirs": {}, "_files": []}
            curr = curr["_dirs"][part]
        curr["_files"].append(doc)

    def _render_tree(node, level=0):
        html = '<ul class="nav-list">'
        for dirname, contents in node.get("_dirs", {}).items():
            html += f'<li class="nav-group"><div class="group-title"><span>📁 {dirname}</span><span class="group-toggle">▼</span></div>'
            html += _render_tree(contents, level + 1)
            html += '</li>'
        for f_info in node.get("_files", []):
            title = f_info['title']
            url = f_info['url']
            active_cls = ' active' if f_info.get('is_active') else ''
            html += f'<li class="nav-item"><a href="{url}" class="nav-link{active_cls}">{title}</a></li>'
        html += '</ul>'
        return html

    return _render_tree(tree)


def transform_showcase_multi_view(content_html: str, lang: str) -> str:
    """🎨 为案例页注入网格与紧凑列表双视图切换器"""
    import re
    
    # 1. 提取全页所有 card-pioneer
    cards = re.findall(r'<a\s+[^>]*href="([^"]+)"[^>]*class="[^"]*card-pioneer[^"]*"[^>]*>(.*?)</a>|<a\s+[^>]*class="[^"]*card-pioneer[^"]*"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', content_html, re.DOTALL)
    
    compact_rows = []
    card_count = 0
    for match in cards:
        href = match[0] or match[2]
        inner = match[1] or match[3]
        if not href or not inner:
            continue
        card_count += 1
        tag_match = re.search(r'<span\s+[^>]*class="[^"]*card-tag[^"]*"[^>]*>([^<]+)</span>', inner)
        tag = tag_match.group(1).strip() if tag_match else "生态"
        title_match = re.search(r'<h3[^>]*>([^<]+)</h3>', inner)
        title = title_match.group(1).strip() if title_match else "Showcase"
        desc_match = re.search(r'<p[^>]*>([^<]+)</p>', inner)
        desc = desc_match.group(1).strip() if desc_match else ""
        
        compact_rows.append(f"""<a href="{href}" class="compact-row showcase-row">
<span class="compact-tags"><span class="tag-pill">{tag}</span></span>
<span class="compact-title">{title}</span>
<span class="compact-desc">{desc}</span>
</a>""")

    if card_count == 0:
        return content_html

    from themes.sovereign.adapters.sovereign_i18n import get_ui_i18n
    ui = get_ui_i18n(lang)
    t_grid = ui.get("view_cards", "Cards")
    t_compact = ui.get("view_list", "List")

    toolbar_html = f"""<div class="showcase-toolbar">
<div class="showcase-view-switcher" role="tablist" aria-label="Showcase layout views">
<button class="view-switch-btn active" data-view="grid" role="tab" aria-selected="true">
<span class="view-btn-icon">🎛️</span>
<span class="view-btn-text">{t_grid}</span>
<span class="view-btn-badge">{card_count}</span>
</button>
<button class="view-switch-btn" data-view="compact" role="tab" aria-selected="false">
<span class="view-btn-icon">📑</span>
<span class="view-btn-text">{t_compact}</span>
</button>
</div>
</div>"""

    # 包装：网格视图包含原页面全部 HTML 内容；紧凑视图展示平铺列表
    grid_view = f'<div class="showcase-view-container showcase-grid-view active" id="showcase-view-grid">\n{content_html}\n</div>'
    compact_view = f'<div class="showcase-view-container showcase-compact-view" id="showcase-view-compact">\n<div class="compact-table">{"".join(compact_rows)}</div>\n</div>'

    # 将切换栏插入到第一个标题/描述之后或内容最前部
    first_hr = content_html.find('<hr')
    if first_hr != -1:
        hr_end = content_html.find('>', first_hr) + 1
        head_part = content_html[:hr_end]
        rest_part = content_html[hr_end:]
        grid_view_rest = f'<div class="showcase-view-container showcase-grid-view active" id="showcase-view-grid">\n{rest_part}\n</div>'
        return f"{head_part}\n{toolbar_html}\n{grid_view_rest}\n{compact_view}"

    return f"{toolbar_html}\n{grid_view}\n{compact_view}"


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
