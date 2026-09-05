# -*- coding: utf-8 -*-
"""
🎨 Sovereign 主题导航与外壳装配构建器分片 (Nav & Shell Builder Shard)

物理职责：
- 负责主导航菜单、上下篇分页、自定义样式及规范网址 (Canonical URL) 的结构装配。
- 严格遵循 SOP-02 架构演进规约与 SOP-01 核心工程标准，物理行数保持在 300 行以内。
"""

import os
import datetime
from typing import Dict, Any
from core.runtime.cli_bootstrap import get_global_engine
from .sovereign_ui import build_doc_pagination


def build_prev_next_pagination(
    adapter,
    layout_type: str,
    slug: str,
    fm: Dict[str, Any],
    effective_lang: str,
    default_code: str,
    root_path: str,
    nav_lang_prefix: str,
    sv_dir_mode: str
) -> str:
    """📖 上一篇/下一篇导航 (针对 docs 文档与 blog 博客详情页)"""
    if layout_type not in ("docs", "blog") or not slug or slug == "index":
        return ""

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
                            if t_t:
                                d_title = t_t

                        d_date = str(d_info.get('persistent_date') or d_info.get('date') or '')
                        # 上下篇导航链接统一路由解析
                        if sv_dir_mode == 'flat':
                            d_nav_url = f"{root_path}{nav_lang_prefix}{d_slug}.html".replace('//', '/')
                        elif sv_dir_mode == 'prefix':
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

    return build_doc_pagination(prev_d, next_d, effective_lang)


def build_custom_styles(accent_color_val: str, enable_glass: bool) -> str:
    """🎨 构建自定义主题色彩与毛玻璃样式标签"""
    glow_color = f"{accent_color_val}40" if (accent_color_val.startswith("#") and len(accent_color_val) == 7) else "rgba(0, 245, 255, 0.25)"
    custom_styles = f"""<style>
    :root {{
        --accent-color: {accent_color_val};
        --accent-cyan: {accent_color_val};
        --accent-glow: {glow_color};
    }}
"""
    if not enable_glass:
        custom_styles += """
    .glass-header, .layout-showcase .card-pioneer, .search-dropdown {
        backdrop-filter: none !important;
        -webkit-backdrop-filter: none !important;
    }
    """
    custom_styles += "\n</style>"
    return custom_styles


def build_footer_copyright(options: Dict[str, Any], site_name_val: str) -> str:
    """🎨 页脚与版权信息构建"""
    footer_copyright_raw = str(options.get('footer_copyright', f"&copy; {site_name_val}."))
    if "Illacme Sovereign" in footer_copyright_raw and site_name_val != "Illacme Sovereign":
        footer_copyright_raw = footer_copyright_raw.replace("Illacme Sovereign", site_name_val)
    current_year = datetime.datetime.now().year
    return footer_copyright_raw.replace("{year}", str(current_year)).replace("{site_name}", site_name_val)


def build_main_nav(
    nav_links_data: list,
    effective_lang: str,
    default_code: str,
    adapter,
    sub_path: str,
    prefix: str,
    slug: str,
    layout_type: str,
    root_path: str,
    nav_lang_prefix: str,
    sv_dir_mode: str,
    t: Dict[str, str]
) -> str:
    """🧭 主导航容器注入 (兼容自定义导航项与默认三模态三合一回退)"""
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
                    if sv_dir_mode == 'flat':
                        full_u = f"{root_path}{nav_lang_prefix}{u_slug}.html".replace('//', '/')
                    elif sv_dir_mode == 'prefix':
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
        return "\n                    ".join(main_nav_html_items)

    # fallback 导航统一遵循三模态设计原则
    if sv_dir_mode == 'flat':
        _blog_p = f"{nav_lang_prefix}blog.html".replace('//', '/')
        _docs_p = f"{nav_lang_prefix}docs.html".replace('//', '/')
        _showcase_p = f"{nav_lang_prefix}showcase.html".replace('//', '/')
    elif sv_dir_mode == 'prefix':
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

    return f"""<a href="{root_path}{_docs_p}"{is_docs_active}>{t["nav_docs"]}</a>
                    <a href="{root_path}{_blog_p}"{is_blog_active}>{t["nav_blog"]}</a>
                    <a href="{root_path}{_showcase_p}"{is_showcase_active}>{t["nav_showcase"]}</a>
                    <a href="{root_path}{nav_lang_prefix}about.html"{is_about_active}>{t["nav_about"]}</a>"""


def build_canonical_url(
    effective_lang: str,
    default_code: str,
    adapter,
    prefix: str,
    sub_dir: str,
    slug: str,
    layout_type: str,
    sv_dir_mode: str
) -> str:
    """🚀 Canonical URL 感知网址组织形态与频道首页收敛规则 (遵循 RouteManager 三模态)"""
    is_source_lang = (effective_lang == default_code)
    force_src_prefix = getattr(adapter, 'force_source_prefix', False)
    need_lang_prefix = not is_source_lang or force_src_prefix
    lang_prefix_seg = f"{effective_lang}/" if need_lang_prefix else ""

    clean_p = (prefix or "").strip("/\\").lower()
    is_global_home = (slug in ('', 'index', 'home') and not clean_p and not sub_dir and layout_type not in ('docs', 'blog', 'showcase'))
    is_channel_home = (slug in ('', 'index', 'home') and not is_global_home)
    channel_name = clean_p or (layout_type if layout_type in ('docs', 'blog', 'showcase') else 'docs')

    if is_global_home:
        return f"/{lang_prefix_seg}index.html".replace('//', '/')
    elif is_channel_home:
        if sv_dir_mode == 'flat':
            return f"/{lang_prefix_seg}{channel_name}.html".replace('//', '/')
        elif sv_dir_mode == 'prefix':
            return f"/{lang_prefix_seg}{channel_name}-index.html".replace('//', '/')
        else:
            return f"/{lang_prefix_seg}{channel_name}/index.html".replace('//', '/')
    else:
        if sv_dir_mode == 'flat':
            return f"/{lang_prefix_seg}{slug}.html".replace('//', '/')
        elif sv_dir_mode == 'prefix':
            p_slug = slug if slug.startswith(f"{channel_name}-") else f"{channel_name}-{slug}"
            return f"/{lang_prefix_seg}{p_slug}.html".replace('//', '/')
        else:
            sub_seg = f"{sub_dir}/" if sub_dir else ""
            return f"/{lang_prefix_seg}{clean_p}/{sub_seg}{slug}.html".replace('//', '/')
