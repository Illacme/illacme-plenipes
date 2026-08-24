# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Generic SSG Adapter Page Renderer Shard
模块职责：提供 Universal 主题与通用 SSG 的标准 HTML 页面骨架装配器。
负责页面元数据提取、文档布局模式判定、本地化文案注入与完整 HTML5 文档渲染。
"""

import os
from typing import Dict, Any

from .navigation_builder import build_docs_sidebar, build_language_switcher
from .assets_bundle import get_universal_css, get_universal_client_js


def render_html_page(
    html_content: str,
    fm: Dict[str, Any],
    target_lang: str,
    sub_path: str,
    root_path: str,
    site_name: str = "Illacme Press",
    i18n_cfg: Any = None,
    engine: Any = None
) -> str:
    """组装全功能现代 Universal HTML 页面骨架 (包含 Showcase 卡片流与 Blog 交互系统)"""
    title = (fm.get('title') if isinstance(fm, dict) else None) or 'Document'
    description = (fm.get('description') if isinstance(fm, dict) else None) or ''

    # 判定页面类型与 Slug
    sub_clean = sub_path.replace('\\', '/').strip('/')
    doc_slug = (fm.get('slug') if isinstance(fm, dict) else '') or os.path.splitext(os.path.basename(sub_clean))[0]
    doc_prefix = (fm.get('route_prefix') if isinstance(fm, dict) else '') or ''
    doc_layout = (fm.get('layout') if isinstance(fm, dict) else '') or ''

    is_about = (doc_slug == 'about' or doc_prefix == 'about' or 'about' in sub_clean.lower())
    is_docs = (doc_layout == 'docs' or doc_prefix == 'docs' or 'docs' in sub_clean.lower()) and not is_about
    is_blog = (doc_layout == 'blog' or doc_prefix == 'blog' or 'blog' in sub_clean.lower()) and not is_about
    is_showcase = (doc_layout == 'showcase' or doc_prefix == 'showcase' or 'showcase' in sub_clean.lower()) and not is_about
    is_home = (doc_slug in ('', 'index', 'home') and not is_about and not is_docs and not is_blog and not is_showcase)

    # 导航高亮
    nav_home_cls = ' active' if is_home else ''
    nav_docs_cls = ' active' if is_docs else ''
    nav_blog_cls = ' active' if is_blog else ''
    nav_showcase_cls = ' active' if is_showcase else ''
    nav_about_cls = ' active' if is_about else ''

    # 语种前缀推导 (如 "en/", "ja/", "")
    lang_nav_prefix = ""
    parts = sub_clean.split('/')
    if parts and len(parts[0]) <= 4 and parts[0].isalpha() and parts[0] not in ("docs", "blog", "showcase", "about"):
        lang_nav_prefix = f"{parts[0]}/"
    elif target_lang and target_lang.lower() not in ('zh', 'zh-hans', 'zh-cn', 'auto'):
        lang_nav_prefix = f"{target_lang}/"

    # 多语种导航与页脚文案本地化
    t_low = (target_lang or 'zh').lower()
    if t_low.startswith('en'):
        t_nav_home = "🏠 Home"
        t_nav_docs = "📚 Docs"
        t_nav_blog = "📰 Blog"
        t_nav_showcase = "🎨 Showcase"
        t_nav_about = "🌐 About Us"
        theme_btn_text = "🌓 Theme"
        powered_by_text = "Powered by <b>Illacme Plenipes</b> · Sovereign Private Press Operating System"
    elif t_low.startswith('ja'):
        t_nav_home = "🏠 ホーム"
        t_nav_docs = "📚 ドキュメント"
        t_nav_blog = "📰 ブログ"
        t_nav_showcase = "🎨 ショーケース"
        t_nav_about = "🌐 私たちについて"
        theme_btn_text = "🌓 テーマ"
        powered_by_text = "Powered by <b>Illacme Plenipes</b> · 主権プライベート出版OS"
    else:
        t_nav_home = "🏠 首页"
        t_nav_docs = "📚 官方文档"
        t_nav_blog = "📰 官方博客"
        t_nav_showcase = "🎨 案例展示"
        t_nav_about = "🌐 关于我们"
        theme_btn_text = "🌓 主题"
        powered_by_text = "Powered by <b>Illacme Plenipes</b> · 主权出版操作系统"

    # 文档侧边栏
    sidebar_html = ""
    layout_cls = "layout-standard"
    if is_docs:
        sidebar_html = build_docs_sidebar(doc_slug, root_path, lang_prefix=lang_nav_prefix, engine=engine, target_lang=target_lang)
        layout_cls = "layout-docs"
    elif is_showcase:
        layout_cls = "layout-showcase"
    elif is_blog:
        layout_cls = "layout-blog"

    # 多语言切换器
    lang_switcher_html = build_language_switcher(target_lang, sub_clean, root_path, i18n_cfg=i18n_cfg)
    css_content = get_universal_css()
    js_content = get_universal_client_js()

    return f"""<!DOCTYPE html>
<html lang="{target_lang}" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | {site_name}</title>
    <meta name="description" content="{description}">
    <link rel="icon" type="image/svg+xml" href="{root_path}favicon.svg">
    <script>
        (function() {{
            var saved = localStorage.getItem('universal-theme');
            if (saved) document.documentElement.setAttribute('data-theme', saved);
            else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {{
                document.documentElement.setAttribute('data-theme', 'light');
            }}
        }})();
    </script>
    <style>
{css_content}
    </style>
    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
        mermaid.initialize({{ startOnLoad: true, theme: document.documentElement.getAttribute('data-theme') === 'light' ? 'default' : 'dark' }});
    </script>
</head>
<body class="{layout_cls}">
    <header class="universal-header">
        <div class="header-container">
            <a href="{root_path}{lang_nav_prefix}index.html" class="header-logo">
                <span>🏛️</span>
                <span>{site_name}</span>
            </a>
            <nav>
                <ul class="header-nav">
                    <li><a href="{root_path}{lang_nav_prefix}index.html" class="header-nav-link{nav_home_cls}">{t_nav_home}</a></li>
                    <li><a href="{root_path}{lang_nav_prefix}docs/index.html" class="header-nav-link{nav_docs_cls}">{t_nav_docs}</a></li>
                    <li><a href="{root_path}{lang_nav_prefix}blog/index.html" class="header-nav-link{nav_blog_cls}">{t_nav_blog}</a></li>
                    <li><a href="{root_path}{lang_nav_prefix}showcase/index.html" class="header-nav-link{nav_showcase_cls}">{t_nav_showcase}</a></li>
                    <li><a href="{root_path}{lang_nav_prefix}about.html" class="header-nav-link{nav_about_cls}">{t_nav_about}</a></li>
                </ul>
            </nav>
            <div style="display: flex; align-items: center; gap: 10px;">
                <button class="theme-toggle-btn" id="theme-btn" onclick="toggleUniversalTheme()">{theme_btn_text}</button>
                {lang_switcher_html}
            </div>
        </div>
    </header>

    <div class="page-container">
        {sidebar_html}
        <main class="universal-article">
            {html_content}
        </main>
    </div>

    <footer class="universal-footer">
        <div>{powered_by_text}</div>
    </footer>

    <script>
{js_content}
    </script>
</body>
</html>"""
