# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Generic SSG Adapter Templates & UI Engine
模块职责：提供 Universal 主题与兜底渲染器的标准 HTML5 骨架、导航栏、Docs 侧边栏、多语言切换、Showcase 栅格与 Blog 交互引擎。
"""

import os
import re
from typing import Dict, Any, List

def build_docs_sidebar(current_slug: str, root_path: str, lang_prefix: str = "", engine: Any = None, target_lang: str = "zh") -> str:
    """构建文档中心左侧导航目录树 (支持从引擎元数据动态解析与多语言国际化对齐)"""
    t_low = (target_lang or 'zh').lower()
    if t_low.startswith('en'):
        default_groups = [
            {
                "group": "⚡ 1. Core Onboarding Guide",
                "items": [
                    {"title": "📚 Documentation Index", "slug": "index", "stems": ["index"]},
                    {"title": "⚡ 5-Minute Quick Start", "slug": "quick-start", "stems": ["quick-start"]},
                    {"title": "✍️ Manuscript Library Guide", "slug": "authoring-and-vault-guide", "stems": ["authoring-and-vault-guide"]},
                    {"title": "🏷️ Multi-Brand Management", "slug": "brand-management", "stems": ["brand-management"]},
                ]
            },
            {
                "group": "🎛️ 2. Governance & Operations",
                "items": [
                    {"title": "🎛️ Governance Center Guide", "slug": "dashboard-guide", "stems": ["dashboard-guide", "dashboard-operation-guide"]},
                    {"title": "🏛️ Physical Sovereignty Architecture", "slug": "architecture", "stems": ["architecture"]},
                ]
            },
            {
                "group": "⚙️ 3. Compute, Themes & I18n",
                "items": [
                    {"title": "🧠 Compute Center & AI Translation", "slug": "compute-and-ai", "stems": ["compute-and-ai", "compute-center-ai-translation-setup-guide"]},
                    {"title": "🌍 Multilingual Content Governance", "slug": "i18n-guide", "stems": ["i18n-guide"]},
                    {"title": "🎨 Themes & Visual Customization", "slug": "themes-and-binding", "stems": ["themes-and-binding", "binding-themes-visual-customization"]},
                ]
            },
            {
                "group": "🛰️ 4. Global Distribution & Troubleshooting",
                "items": [
                    {"title": "🛰️ Channels & Configuration", "slug": "distribution-channels", "stems": ["distribution-channels", "matrix-channel-configuration"]},
                    {"title": "❓ FAQ & Troubleshooting", "slug": "faq", "stems": ["faq", "common-issues-and-troubleshooting-manual-faq"]},
                ]
            }
        ]
    elif t_low.startswith('ja'):
        default_groups = [
            {
                "group": "⚡ 1. コア入門ガイド",
                "items": [
                    {"title": "📚 ドキュメントセンター案内", "slug": "index", "stems": ["index"]},
                    {"title": "⚡ 5分でサクッと始める", "slug": "quick-start", "stems": ["quick-start"]},
                    {"title": "✍️ 原稿ライブラリ編成ガイド", "slug": "authoring-and-vault-guide", "stems": ["authoring-and-vault-guide"]},
                    {"title": "🏷️ ブランド版図とマルチサイト管理", "slug": "brand-management", "stems": ["brand-management"]},
                ]
            },
            {
                "group": "🎛️ 2. ガバナンスセンターと運用",
                "items": [
                    {"title": "🎛️ ガバナンスセンター操作完全ガイド", "slug": "dashboard-guide", "stems": ["dashboard-guide", "dashboard-operation-guide"]},
                    {"title": "🏛️ 物理的主権アーキテクチャの原理", "slug": "architecture", "stems": ["architecture"]},
                ]
            },
            {
                "group": "⚙️ 3. 計算リソース・テーマ・多言語",
                "items": [
                    {"title": "🧠 計算センターとAI自動翻訳", "slug": "compute-and-ai", "stems": ["compute-and-ai", "compute-center-ai-translation-setup-guide"]},
                    {"title": "🌍 多言語マトリックスと内容ガバナンス", "slug": "i18n-guide", "stems": ["i18n-guide"]},
                    {"title": "🎨 装丁テーマとビジュアルカスタマイズ", "slug": "themes-and-binding", "stems": ["themes-and-binding", "binding-themes-visual-customization"]},
                ]
            },
            {
                "group": "🛰️ 4. 全域配信とトラブルシューティング",
                "items": [
                    {"title": "🛰️ 配信マトリックスとチャネル設定", "slug": "distribution-channels", "stems": ["distribution-channels", "matrix-channel-configuration"]},
                    {"title": "❓ よくある質問とトラブルシューティング", "slug": "faq", "stems": ["faq", "common-issues-and-troubleshooting-manual-faq"]},
                ]
            }
        ]
    else:
        default_groups = [
            {
                "group": "⚡ 1. 核心入门",
                "items": [
                    {"title": "📚 文档中心首页", "slug": "index", "stems": ["index"]},
                    {"title": "⚡ 5 分钟上手指南", "slug": "quick-start", "stems": ["quick-start"]},
                    {"title": "✍️ 原稿文库组织指引", "slug": "authoring-and-vault-guide", "stems": ["authoring-and-vault-guide"]},
                    {"title": "🏷️ 品牌版图多站点管理", "slug": "brand-management", "stems": ["brand-management"]},
                ]
            },
            {
                "group": "🎛️ 2. 治理中心与运维",
                "items": [
                    {"title": "🎛️ 治理中心操作全解", "slug": "dashboard-guide", "stems": ["dashboard-guide", "dashboard-operation-guide"]},
                    {"title": "🏛️ 物理隔离架构原理", "slug": "architecture", "stems": ["architecture"]},
                ]
            },
            {
                "group": "⚙️ 3. 算力、装帧与多语言",
                "items": [
                    {"title": "🧠 算力中心与 AI 翻译", "slug": "compute-and-ai", "stems": ["compute-and-ai", "compute-center-ai-translation-setup-guide"]},
                    {"title": "🌍 多语言矩阵与内容治理", "slug": "i18n-guide", "stems": ["i18n-guide"]},
                    {"title": "🎨 装帧主题与视觉定制", "slug": "themes-and-binding", "stems": ["themes-and-binding", "binding-themes-visual-customization"]},
                ]
            },
            {
                "group": "🛰️ 4. 全域分发与排错",
                "items": [
                    {"title": "🛰️ 发行矩阵与渠道配置", "slug": "distribution-channels", "stems": ["distribution-channels", "matrix-channel-configuration"]},
                    {"title": "❓ 常见问题与排错手册", "slug": "faq", "stems": ["faq", "common-issues-and-troubleshooting-manual-faq"]},
                ]
            }
        ]

    # 获取动态 Slug 映射表
    slug_map = get_doc_slug_map(engine)

    html_parts = ['<nav class="universal-docs-sidebar"><div class="sidebar-inner">']
    for group in default_groups:
        html_parts.append(f'<div class="sidebar-group"><div class="sidebar-group-title">{group["group"]}</div><ul class="sidebar-nav-list">')
        for item in group["items"]:
            # 优先从映射表中寻找实际生成的 slug
            actual_slug = item["slug"]
            for stem in item.get("stems", [item["slug"]]):
                if stem in slug_map:
                    actual_slug = slug_map[stem]["slug"]
                    break
            
            target_url = f"{root_path}{lang_prefix}docs/{actual_slug}.html" if actual_slug != "index" else f"{root_path}{lang_prefix}docs/index.html"
            
            is_active = (
                current_slug == actual_slug or 
                current_slug in item.get("stems", []) or
                (current_slug in ("", "index") and actual_slug == "index") or 
                current_slug.endswith(f"/{actual_slug}")
            )
            active_cls = ' active' if is_active else ''
            html_parts.append(f'<li class="sidebar-nav-item"><a href="{target_url}" class="sidebar-nav-link{active_cls}">{item["title"]}</a></li>')
        html_parts.append('</ul></div>')
    html_parts.append('</div></nav>')
    return '\n'.join(html_parts)

def get_doc_slug_map(engine: Any = None) -> Dict[str, Dict[str, str]]:
    """从引擎元数据中提取所有原稿文件名/stem 到最终 slug 与 channel 的映射"""
    mapping = {}
    if not engine or not hasattr(engine, 'meta'):
        return mapping
        
    docs = {}
    if hasattr(engine.meta, 'get_documents_snapshot'):
        docs = engine.meta.get_documents_snapshot()
    elif hasattr(engine.meta, 'sqlite') and hasattr(engine.meta.sqlite, 'get_all_documents'):
        docs = engine.meta.sqlite.get_all_documents()
    elif hasattr(engine.meta, 'data'):
        docs = engine.meta.data.get("documents", {})
        
    for rel_path, info in docs.items():
        stem = os.path.splitext(os.path.basename(rel_path))[0]
        slug = info.get('slug') or stem
        slot = info.get('target_slot') or info.get('route_prefix') or 'docs'
        
        entry = {"slug": slug, "channel": slot, "title": info.get('title') or stem}
        mapping[stem.lower()] = entry
        mapping[slug.lower()] = entry
        mapping[rel_path.replace('\\', '/').lower()] = entry
        
    return mapping

def build_language_switcher(current_lang: str, sub_path: str, root_path: str, i18n_cfg: Any = None) -> str:
    """构建多语言切换下拉菜单"""
    if i18n_cfg is not None and hasattr(i18n_cfg, 'enabled') and not i18n_cfg.enabled:
        return ""
        
    src_code = getattr(getattr(i18n_cfg, 'source', None), 'lang_code', 'zh') if i18n_cfg else 'zh'
    src_name = getattr(getattr(i18n_cfg, 'source', None), 'name', '简体中文') if i18n_cfg else '简体中文'
    targets = getattr(i18n_cfg, 'targets', []) if i18n_cfg else []
    
    if not targets:
        class _LangItem:
            def __init__(self, code, name):
                self.lang_code = code
                self.name = name
        targets = [_LangItem('en', 'English'), _LangItem('ja', '日本語')]
    
    # 提取纯净的相对页面路径 (去除已有语言前缀)
    sub_clean = sub_path.replace('\\', '/').strip('/')
    target_codes = [getattr(t, 'lang_code', '') for t in targets if getattr(t, 'lang_code', None)]
    parts = sub_clean.split('/')
    if parts and (parts[0] in target_codes or parts[0] == src_code):
        clean_page_path = '/'.join(parts[1:])
    else:
        clean_page_path = sub_clean
        
    if not clean_page_path.endswith('.html') and not clean_page_path.endswith('.md'):
        clean_page_path += "/index.html" if clean_page_path else "index.html"
    elif clean_page_path.endswith('.md'):
        clean_page_path = os.path.splitext(clean_page_path)[0] + '.html'
        
    lang_flags = {
        "zh": "🇨🇳", "zh-hans": "🇨🇳", "zh-hant": "🇭🇰", "en": "🇺🇸", "ja": "🇯🇵",
        "ko": "🇰🇷", "fr": "🇫🇷", "de": "🇩🇪", "es": "🇪🇸", "ru": "🇷🇺", "ar": "🇸🇦"
    }
    
    all_langs = [{"code": src_code, "name": src_name, "is_source": True}]
    for t in targets:
        if getattr(t, 'lang_code', None):
            all_langs.append({"code": t.lang_code, "name": getattr(t, 'name', t.lang_code), "is_source": False})
            
    current_code = (current_lang.lower() if current_lang else src_code.lower())
    current_flag = lang_flags.get(current_code, "🌐")
    current_display = next((l["name"] for l in all_langs if l["code"].lower() == current_code), current_code.upper())
    
    menu_items = []
    for l in all_langs:
        code = l["code"]
        name = l["name"]
        flag = lang_flags.get(code.lower(), "🌐")
        is_active = (code.lower() == current_code)
        active_cls = ' active' if is_active else ''
        
        if l["is_source"]:
            url = f"{root_path}{clean_page_path}"
        else:
            url = f"{root_path}{code}/{clean_page_path}"
            
        menu_items.append(f'<a href="{url}" class="lang-menu-item{active_cls}"><span class="lang-flag">{flag}</span> <span>{name}</span></a>')
        
    menu_html = '\n'.join(menu_items)
    
    return f"""
    <div class="lang-dropdown-wrapper" id="lang-dropdown">
        <button class="theme-toggle-btn lang-dropdown-btn" type="button" title="切换语种">
            <span>{current_flag}</span>
            <span>{current_display}</span>
            <span class="caret">▾</span>
        </button>
        <div class="lang-dropdown-menu">
            {menu_html}
        </div>
    </div>
    """

def resolve_wikilinks(body: str, root_path: str, sub_path: str = "", engine: Any = None) -> str:
    """将 Obsidian 双链 [[target|alias]] 智能解析为真实目标文件的相对超链接 (防 404)"""
    slug_map = get_doc_slug_map(engine)

    def _repl(match):
        target = match.group(1).strip()
        alias = (match.group(2) or target).strip()
        clean_target = target.replace('\\', '/').strip('/')
        if not clean_target:
            return alias
            
        anchor = ""
        if '#' in clean_target:
            parts = clean_target.split('#', 1)
            clean_target = parts[0]
            anchor = f"#{parts[1]}"
            
        if clean_target.startswith(('http://', 'https://', 'mailto:', '/')):
            return f'<a href="{clean_target}{anchor}" class="universal-link external">{alias}</a>'
            
        target_stem = os.path.splitext(os.path.basename(clean_target))[0].lower()
        
        # 命中元数据精确 Slug 查找
        if target_stem in slug_map:
            mapped_entry = slug_map[target_stem]
            final_slug = mapped_entry["slug"]
            channel = mapped_entry["channel"] or "docs"
            if "docs" in sub_path and channel == "docs":
                href = f"./{final_slug}.html{anchor}"
            else:
                href = f"{root_path}{channel}/{final_slug}.html{anchor}"
        else:
            if not clean_target.endswith('.html'):
                clean_target = f"{clean_target}.html"
            if "docs" in sub_path and "/" not in clean_target:
                href = f"./{clean_target}{anchor}"
            elif "docs" not in sub_path and "/" not in clean_target:
                href = f"{root_path}docs/{clean_target}{anchor}"
            else:
                href = f"{root_path}{clean_target}{anchor}"
            
        return f'<a href="{href}" class="universal-link wikilink">{alias}</a>'

    wiki_pattern = re.compile(r'(?<!\!)\[\[([^\]|]+)(?:\|([^\]]+))?\]\]')
    return wiki_pattern.sub(_repl, body)

def resolve_callouts(body: str) -> tuple:
    """提取并预解析 Markdown Callouts 提示块"""
    import markdown
    callouts = []
    callout_pattern = re.compile(r'^>\s*\[!(\w+)\]\s*(.*)?\n((?:^>.*\n?)*)', re.MULTILINE)
    
    icon_map = {
        "note": "ℹ️", "tip": "💡", "important": "📌", "warning": "⚠️",
        "caution": "🛑", "danger": "🔥", "info": "📘", "success": "✅"
    }

    def _collect(match):
        c_type = match.group(1).lower()
        raw_title = (match.group(2) or "").strip().lstrip('> ').strip()
        content_lines = match.group(3).split('\n')
        clean_content = "\n".join([line.lstrip('> ').strip() for line in content_lines if line.strip()])
        
        icon = icon_map.get(c_type, "💡")
        title = raw_title if raw_title else c_type.capitalize()
        rendered_body = markdown.markdown(clean_content, extensions=['extra', 'nl2br'])
        
        callout_html = f"""<div class="universal-callout callout-{c_type}">
    <div class="callout-header"><span class="callout-icon">{icon}</span> <strong class="callout-title">{title}</strong></div>
    <div class="callout-body">{rendered_body}</div>
</div>"""
        idx = len(callouts)
        callouts.append(callout_html)
        return f"\n@@CALLOUT:{idx}@@\n"

    processed = callout_pattern.sub(_collect, body)
    return processed, callouts

def resolve_mermaids(body: str) -> tuple:
    """提取并保护 Mermaid 图表代码块"""
    import html as _html
    mermaids = []
    mermaid_pattern = re.compile(r'```(?:mermaid|flowchart)\s*\n(.*?)\n```', re.DOTALL)

    def _collect(match):
        raw_code = match.group(1).strip()
        idx = len(mermaids)
        html_code = _html.escape(raw_code)
        h = f'<div class="universal-mermaid"><pre class="mermaid">{html_code}</pre></div>'
        mermaids.append(h)
        return f"\n@@MERMAID:{idx}@@\n"

    processed = mermaid_pattern.sub(_collect, body)
    return processed, mermaids

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
        :root {{
            --bg-base: #0d1117;
            --bg-surface: #161b22;
            --bg-elevated: #21262d;
            --text-primary: #f0f6fc;
            --text-secondary: #8b949e;
            --text-muted: #6e7681;
            --accent: #58a6ff;
            --accent-color: #58a6ff;
            --accent-glow: rgba(88, 166, 255, 0.25);
            --border-subtle: #30363d;
            --border-strong: #484f58;
            --border-color: #30363d;
            --card-bg: rgba(22, 27, 34, 0.85);
            --header-bg: rgba(13, 17, 23, 0.85);
            --callout-note: #388bfd;
            --callout-tip: #3fb950;
            --callout-warn: #d29922;
            --callout-danger: #f85149;
        }}
        [data-theme="light"] {{
            --bg-base: #ffffff;
            --bg-surface: #f6f8fa;
            --bg-elevated: #eaeef2;
            --text-primary: #1f2328;
            --text-secondary: #57606a;
            --text-muted: #8c959f;
            --accent: #0969da;
            --accent-color: #0969da;
            --accent-glow: rgba(9, 105, 218, 0.2);
            --border-subtle: #d0d7de;
            --border-strong: #afb8c1;
            --border-color: #d0d7de;
            --card-bg: rgba(246, 248, 250, 0.9);
            --header-bg: rgba(255, 255, 255, 0.9);
            --callout-note: #0969da;
            --callout-tip: #1a7f37;
            --callout-warn: #9a6700;
            --callout-danger: #cf222e;
        }}
        * {{ box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", Helvetica, Arial, sans-serif;
            background-color: var(--bg-base);
            color: var(--text-primary);
            margin: 0;
            padding: 0;
            line-height: 1.65;
            -webkit-font-smoothing: antialiased;
        }}
        /* 🚀 首页 Hero 与 CTA 高清按钮兼容 */
        .home-hero-container .control-btn.theme-btn,
        .hero-cta-group a,
        .hero-cta-group a.control-btn {{
            display: inline-flex !important;
            align-items: center !important;
            gap: 8px !important;
            padding: 12px 28px !important;
            font-size: 1rem !important;
            font-weight: 700 !important;
            border-radius: 12px !important;
            text-decoration: none !important;
            transition: all 0.2s ease !important;
        }}
        .hero-cta-group a:first-child,
        .hero-cta-group a.control-btn:first-child {{
            background: #58a6ff !important;
            color: #ffffff !important;
            box-shadow: 0 0 20px rgba(88, 166, 255, 0.35) !important;
            border: 1px solid rgba(88, 166, 255, 0.5) !important;
        }}
        .hero-cta-group a:first-child:hover,
        .hero-cta-group a.control-btn:first-child:hover {{
            background: #79b8ff !important;
            color: #ffffff !important;
            transform: translateY(-2px);
            box-shadow: 0 0 25px rgba(88, 166, 255, 0.5) !important;
        }}
        .hero-cta-group a:not(:first-child),
        .hero-cta-group a.control-btn:not(:first-child) {{
            background: var(--bg-surface) !important;
            color: var(--text-primary) !important;
            border: 1px solid var(--border-subtle) !important;
        }}
        .hero-cta-group a:not(:first-child):hover,
        .hero-cta-group a.control-btn:not(:first-child):hover {{
            background: var(--bg-elevated) !important;
            color: var(--accent) !important;
            border-color: var(--accent) !important;
            transform: translateY(-2px);
        }}
        /* 🌐 顶部毛玻璃导航 */
        .universal-header {{
            position: sticky;
            top: 0;
            z-index: 100;
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            background: var(--header-bg);
            border-bottom: 1px solid var(--border-subtle);
            height: 60px;
            display: flex;
            align-items: center;
        }}
        .header-container {{
            max-width: 1280px;
            width: 100%;
            margin: 0 auto;
            padding: 0 1.5rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        .header-logo {{
            display: flex;
            align-items: center;
            gap: 10px;
            text-decoration: none;
            color: var(--text-primary);
            font-weight: 700;
            font-size: 1.1rem;
        }}
        .header-logo:hover {{ color: var(--accent); }}
        .header-nav {{
            display: flex;
            align-items: center;
            gap: 1.25rem;
            list-style: none;
            margin: 0;
            padding: 0;
        }}
        .header-nav-link {{
            color: var(--text-secondary);
            text-decoration: none;
            font-size: 0.92rem;
            font-weight: 500;
            padding: 6px 12px;
            border-radius: 6px;
            transition: all 0.2s;
        }}
        .header-nav-link:hover, .header-nav-link.active {{
            color: var(--text-primary);
            background: var(--bg-elevated);
        }}
        .header-nav-link.active {{
            color: var(--accent);
            font-weight: 600;
        }}
        .theme-toggle-btn {{
            background: var(--bg-surface);
            border: 1px solid var(--border-subtle);
            color: var(--text-primary);
            padding: 6px 12px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.85rem;
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .theme-toggle-btn:hover {{ border-color: var(--accent); }}

        /* 🌐 多语言下拉组件 */
        .lang-dropdown-wrapper {{
            position: relative;
            display: inline-block;
        }}
        .lang-dropdown-btn {{
            display: flex;
            align-items: center;
            gap: 6px;
            cursor: pointer;
        }}
        .lang-dropdown-menu {{
            display: none;
            position: absolute;
            top: 100%;
            right: 0;
            margin-top: 4px;
            background: var(--bg-surface);
            border: 1px solid var(--border-subtle);
            border-radius: 8px;
            padding: 6px;
            min-width: 150px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.3);
            z-index: 1000;
        }}
        /* 🚀 关键修复：无缝防断连悬停桥接垫片 (Hover Bridge)，彻底根除鼠标向下方列表移动时菜单闪退的死穴 */
        .lang-dropdown-menu::before {{
            content: '';
            position: absolute;
            top: -12px;
            left: 0;
            right: 0;
            height: 12px;
            background: transparent;
        }}
        .lang-dropdown-wrapper:hover .lang-dropdown-menu,
        .lang-dropdown-wrapper:focus-within .lang-dropdown-menu {{
            display: block;
        }}
        .lang-menu-item {{
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 12px;
            color: var(--text-secondary);
            text-decoration: none;
            font-size: 0.88rem;
            border-radius: 6px;
            transition: all 0.15s;
        }}
        .lang-menu-item:hover {{
            color: var(--text-primary);
            background: var(--bg-elevated);
            text-decoration: none;
        }}
        .lang-menu-item.active {{
            color: var(--accent);
            background: var(--accent-glow);
            font-weight: 600;
        }}

        /* 布局容器 */
        .page-container {{
            max-width: 1280px;
            margin: 0 auto;
            padding: 2.5rem 1.5rem;
            min-height: calc(100vh - 140px);
        }}
        .layout-docs .page-container {{
            display: grid;
            grid-template-columns: 260px minmax(0, 1fr);
            gap: 2.5rem;
        }}
        .layout-standard .page-container {{ max-width: 980px; }}
        .layout-showcase .page-container {{ max-width: 1180px; }}
        .layout-blog .page-container {{ max-width: 1080px; }}

        /* 📂 文档侧边栏 */
        .universal-docs-sidebar {{
            position: sticky;
            top: 80px;
            max-height: calc(100vh - 100px);
            overflow-y: auto;
            border-right: 1px solid var(--border-subtle);
            padding-right: 1.5rem;
        }}
        .sidebar-group {{ margin-bottom: 1.5rem; }}
        .sidebar-group-title {{
            font-size: 0.82rem;
            font-weight: 700;
            text-transform: uppercase;
            color: var(--text-muted);
            margin-bottom: 0.6rem;
            letter-spacing: 0.5px;
        }}
        .sidebar-nav-list {{
            list-style: none;
            padding: 0;
            margin: 0;
        }}
        .sidebar-nav-link {{
            display: block;
            color: var(--text-secondary);
            text-decoration: none;
            font-size: 0.9rem;
            padding: 6px 10px;
            border-radius: 6px;
            transition: all 0.15s;
            line-height: 1.4;
        }}
        .sidebar-nav-link:hover {{
            color: var(--text-primary);
            background: var(--bg-surface);
        }}
        .sidebar-nav-link.active {{
            color: var(--accent);
            background: var(--accent-glow);
            font-weight: 600;
        }}

        /* 📝 正文排版 */
        .universal-article {{ min-width: 0; }}
        .universal-article h1 {{
            font-size: 2.2rem;
            font-weight: 800;
            border-bottom: 1px solid var(--border-subtle);
            padding-bottom: 0.5rem;
            margin-top: 0;
            margin-bottom: 1.5rem;
            line-height: 1.25;
        }}
        .universal-article h2 {{
            font-size: 1.6rem;
            font-weight: 700;
            border-bottom: 1px solid var(--border-subtle);
            padding-bottom: 0.4rem;
            margin-top: 2.2rem;
            margin-bottom: 1rem;
        }}
        .universal-article h3 {{ font-size: 1.25rem; font-weight: 600; margin-top: 1.5rem; }}
        .universal-article hr {{
            border: 0;
            border-top: 1px solid var(--border-subtle);
            margin: 2.5rem 0;
        }}
        .universal-article p {{ margin: 1rem 0; }}
        .universal-article ul, .universal-article ol {{ padding-left: 1.5rem; margin: 1rem 0; }}
        .universal-article li {{ margin-bottom: 0.4rem; }}
        .universal-link {{
            color: var(--accent);
            text-decoration: none;
            font-weight: 500;
        }}
        .universal-link:hover {{ text-decoration: underline; }}
        .universal-link.wikilink {{ border-bottom: 1px dashed var(--accent); }}

        /* 🎨 Showcase & Blog 卡片栅格系统 */
        article, .blog-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 1.5rem;
            margin-top: 2rem;
        }}
        .card-pioneer {{
            display: flex;
            flex-direction: column;
            padding: 1.5rem;
            background: var(--bg-surface);
            border: 1px solid var(--border-subtle);
            border-radius: 12px;
            text-decoration: none;
            color: var(--text-primary);
            transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
            position: relative;
            overflow: hidden;
        }}
        .card-pioneer:hover {{
            transform: translateY(-4px);
            border-color: var(--accent);
            box-shadow: 0 12px 30px rgba(0,0,0,0.25);
            text-decoration: none;
        }}
        .card-tag {{
            align-self: flex-start;
            display: inline-block;
            padding: 4px 10px;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border-radius: 20px;
            background: var(--accent-glow);
            color: var(--accent);
            margin-bottom: 0.8rem;
        }}
        .card-pioneer h3 {{
            font-size: 1.25rem;
            font-weight: 700;
            margin: 0 0 0.6rem 0;
            color: var(--text-primary);
            line-height: 1.35;
        }}
        .card-pioneer p {{
            font-size: 0.9rem;
            color: var(--text-secondary);
            line-height: 1.55;
            margin: 0 0 1rem 0;
            flex-grow: 1;
        }}
        .card-meta {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 0.8rem;
            font-size: 0.82rem;
            color: var(--text-muted);
        }}
        .card-tags {{ display: flex; gap: 6px; flex-wrap: wrap; }}
        .card-footer {{
            display: flex;
            align-items: center;
            justify-content: flex-end;
            font-size: 0.85rem;
            font-weight: 600;
            color: var(--accent);
            margin-top: auto;
        }}

        /* ✍️ 博客时间轴与工具栏 */
        .blog-hero-section {{
            margin-bottom: 2rem;
            border-bottom: 1px solid var(--border-subtle);
            padding-bottom: 1.5rem;
        }}
        .list-hero-title {{ font-size: 2.2rem; font-weight: 800; margin: 0 0 0.5rem 0; }}
        .list-hero-desc {{ font-size: 1.05rem; color: var(--text-secondary); margin: 0 0 1.5rem 0; }}
        .blog-toolbar {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            flex-wrap: wrap;
        }}
        .blog-tag-scroller {{
            display: flex;
            align-items: center;
            gap: 8px;
            overflow-x: auto;
            padding-bottom: 4px;
            max-width: 70%;
        }}
        .blog-tag-filter {{
            background: var(--bg-surface);
            border: 1px solid var(--border-subtle);
            color: var(--text-secondary);
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.82rem;
            cursor: pointer;
            transition: all 0.2s;
            white-space: nowrap;
        }}
        .blog-tag-filter:hover, .blog-tag-filter.active {{
            color: var(--text-primary);
            background: var(--accent-glow);
            border-color: var(--accent);
        }}
        .blog-view-switcher {{
            display: flex;
            align-items: center;
            background: var(--bg-surface);
            border: 1px solid var(--border-subtle);
            border-radius: 8px;
            padding: 3px;
            gap: 2px;
        }}
        .view-switch-btn {{
            background: transparent;
            border: none;
            color: var(--text-secondary);
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 0.84rem;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 5px;
            transition: all 0.15s;
        }}
        .view-switch-btn.active {{
            background: var(--bg-elevated);
            color: var(--accent);
            font-weight: 600;
        }}
        .view-btn-badge {{
            background: var(--accent-glow);
            color: var(--accent);
            padding: 1px 6px;
            border-radius: 10px;
            font-size: 0.72rem;
        }}

        /* 时间轴与网格卡片视图控制 */
        .blog-timeline-view {{ display: none !important; margin-top: 2rem; }}
        .blog-timeline-view.active {{ display: block !important; }}
        .blog-grid-view {{ display: none !important; margin-top: 2rem; }}
        .blog-grid-view.active {{
            display: grid !important;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 1.5rem;
        }}
        .blog-compact-view {{ display: none !important; margin-top: 2rem; }}
        .blog-compact-view.active {{ display: block !important; }}

        .timeline-tree {{
            position: relative;
            padding-left: 2rem;
            border-left: 2px solid var(--border-subtle);
            margin-left: 1rem;
        }}
        .timeline-year-group {{ margin-bottom: 2.5rem; }}
        .timeline-year-badge {{
            font-size: 1.4rem;
            font-weight: 800;
            color: var(--accent);
            margin-bottom: 1.25rem;
        }}
        .timeline-item {{
            position: relative;
            margin-bottom: 1.75rem;
            background: var(--bg-surface);
            border: 1px solid var(--border-subtle);
            border-radius: 10px;
            padding: 1.25rem 1.5rem;
            transition: all 0.2s;
        }}
        .timeline-item:hover {{
            border-color: var(--accent);
            transform: translateX(4px);
        }}
        .timeline-node {{
            position: absolute;
            left: -2.45rem;
            top: 1.5rem;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: var(--accent);
            box-shadow: 0 0 0 4px var(--bg-base);
        }}
        .timeline-meta {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 6px;
            font-size: 0.82rem;
            color: var(--text-muted);
        }}
        .timeline-tags {{ display: flex; gap: 6px; }}
        .timeline-tag {{
            background: var(--accent-glow);
            color: var(--accent);
            padding: 1px 8px;
            border-radius: 12px;
            font-size: 0.75rem;
        }}
        .timeline-title {{
            font-size: 1.15rem;
            font-weight: 700;
            color: var(--text-primary);
            text-decoration: none;
            display: inline-block;
            margin-bottom: 6px;
        }}
        .timeline-title:hover {{ color: var(--accent); }}
        .timeline-desc {{
            font-size: 0.9rem;
            color: var(--text-secondary);
            margin: 0;
            line-height: 1.5;
        }}

        /* 💡 Callouts */
        .universal-callout {{
            border-radius: 8px;
            padding: 12px 16px;
            margin: 1.25rem 0;
            border-left: 4px solid var(--accent);
            background: var(--bg-surface);
        }}
        .callout-note {{ border-color: var(--callout-note); background: rgba(56, 139, 253, 0.08); }}
        .callout-tip {{ border-color: var(--callout-tip); background: rgba(63, 185, 80, 0.08); }}
        .callout-warning {{ border-color: var(--callout-warn); background: rgba(210, 153, 34, 0.08); }}
        .callout-caution, .callout-danger {{ border-color: var(--callout-danger); background: rgba(248, 81, 73, 0.08); }}
        .callout-header {{ display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }}
        .callout-body p {{ margin: 0; }}

        /* 代码高亮与 Mermaid */
        pre, code {{
            font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace;
            background: var(--bg-surface);
            border-radius: 6px;
        }}
        code {{ padding: 0.2em 0.4em; font-size: 85%; }}
        pre {{ padding: 1rem; overflow-x: auto; border: 1px solid var(--border-subtle); }}
        pre code {{ padding: 0; background: transparent; }}
        .universal-mermaid {{
            background: var(--bg-surface);
            border: 1px solid var(--border-subtle);
            border-radius: 8px;
            padding: 1.5rem;
            margin: 1.5rem 0;
            overflow-x: auto;
            text-align: center;
        }}

        /* 底部版权 */
        .universal-footer {{
            border-top: 1px solid var(--border-subtle);
            padding: 2rem 1.5rem;
            text-align: center;
            color: var(--text-muted);
            font-size: 0.85rem;
            margin-top: 3rem;
        }}

        @media (max-width: 768px) {{
            .layout-docs .page-container {{ grid-template-columns: 1fr; }}
            .universal-docs-sidebar {{ display: none; }}
            .header-nav {{ display: none; }}
            .blog-tag-scroller {{ max-width: 100%; }}
        }}
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
        function toggleUniversalTheme() {{
            var current = document.documentElement.getAttribute('data-theme') || 'dark';
            var next = current === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', next);
            localStorage.setItem('universal-theme', next);
        }}

        // 🌐 多语言下拉交互支持 (支持点击展开/常驻与外部点击收起)
        document.addEventListener('DOMContentLoaded', function() {{
            var dropdown = document.getElementById('lang-dropdown');
            if (dropdown) {{
                var btn = dropdown.querySelector('.lang-dropdown-btn');
                var menu = dropdown.querySelector('.lang-dropdown-menu');
                if (btn && menu) {{
                    btn.addEventListener('click', function(e) {{
                        e.stopPropagation();
                        var isShown = menu.style.display === 'block';
                        menu.style.display = isShown ? '' : 'block';
                    }});
                    document.addEventListener('click', function(e) {{
                        if (!dropdown.contains(e.target)) {{
                            menu.style.display = '';
                        }}
                    }});
                }}
            }}
        }});

        // 博客交互：视图切换与标签过滤
        document.addEventListener('DOMContentLoaded', function() {{
            var blogApp = document.getElementById('blog-app');
            if (!blogApp) return;

            var switchBtns = blogApp.querySelectorAll('.view-switch-btn');
            var views = {{
                timeline: document.getElementById('view-timeline'),
                grid: document.getElementById('view-grid'),
                compact: document.getElementById('view-compact')
            }};

            switchBtns.forEach(function(btn) {{
                btn.addEventListener('click', function() {{
                    var targetView = btn.dataset.view;
                    switchBtns.forEach(function(b) {{ b.classList.remove('active'); }});
                    btn.classList.add('active');
                    Object.keys(views).forEach(function(k) {{
                        if (views[k]) views[k].classList.remove('active');
                    }});
                    if (views[targetView]) views[targetView].classList.add('active');
                }});
            }});

            var tagBtns = blogApp.querySelectorAll('.blog-tag-filter');
            tagBtns.forEach(function(tBtn) {{
                tBtn.addEventListener('click', function() {{
                    var tag = tBtn.dataset.tag;
                    tagBtns.forEach(function(tb) {{ tb.classList.remove('active'); }});
                    tBtn.classList.add('active');

                    var items = blogApp.querySelectorAll('.timeline-item, .blog-card');
                    items.forEach(function(it) {{
                        var tags = (it.dataset.tags || '').split(',');
                        if (tag === 'all' || tags.indexOf(tag) !== -1) {{
                            it.style.display = '';
                        }} else {{
                            it.style.display = 'none';
                        }}
                    }});
                }});
            }});
        }});
    </script>
</body>
</html>"""


def generate_dynamic_blog_archive(engine: Any, snapshot: Dict[str, Any] = None) -> None:
    """⚡ 全自动扫描文库所有博文，并动态生成支持三视图切换与标签过滤的博客归档中心 (Zero-Vault-Pollution)"""
    if not engine:
        return

    # 1. 获取所有文档快照
    docs = snapshot
    if not docs:
        if hasattr(engine, 'meta') and hasattr(engine.meta, 'get_documents_snapshot'):
            docs = engine.meta.get_documents_snapshot()
        elif hasattr(engine, 'meta') and hasattr(engine.meta, 'data'):
            docs = engine.meta.data.get("documents", {})
    if not docs:
        return

    # 2. 提取所有博客类别的文章
    blog_posts = []
    all_tags = set()
    for rel_path, info in docs.items():
        rel_clean = rel_path.replace('\\', '/').lower()
        slot = (info.get('target_slot') or info.get('route_prefix') or '').lower()
        if slot != 'blog' and not rel_clean.startswith('blog/'):
            continue

        stem = os.path.splitext(os.path.basename(rel_path))[0]
        if stem in ('index', 'readme'):
            continue

        slug = info.get('slug') or stem
        title = info.get('title') or stem
        date_str = str(info.get('date') or '2026-08-20')[:10]
        desc = info.get('description') or ''
        raw_tags = info.get('tags') or ['Blog']
        if isinstance(raw_tags, str):
            tags = [t.strip() for t in raw_tags.split(',') if t.strip()]
        else:
            tags = [str(t).strip() for t in raw_tags if str(t).strip()]
        if not tags:
            tags = ['Blog']
        for t in tags:
            all_tags.add(t)

        blog_posts.append({
            "rel_path": rel_path,
            "stem": stem,
            "slug": slug,
            "title": title,
            "date": date_str,
            "desc": desc,
            "tags": tags,
            "translations": info.get('translations', {})
        })

    if not blog_posts:
        return

    # 按发布日期倒序排序
    blog_posts.sort(key=lambda x: str(x.get('date', '')), reverse=True)

    # 3. 确定目标输出目录 (如 imprints/default/themes/universal/dist 或 paths.site_dir)
    site_dir = None
    if hasattr(engine, 'paths') and isinstance(engine.paths, dict):
        site_dir = engine.paths.get('site_dir')
    if not site_dir:
        theme = getattr(engine, 'active_theme', 'universal') or 'universal'
        site_dir = os.path.join(os.getcwd(), 'imprints', getattr(engine, 'imprint_id', 'default'), 'themes', theme, 'dist')

    i18n_cfg = getattr(engine.config, 'i18n_settings', None) if hasattr(engine, 'config') else None
    src_code = getattr(getattr(i18n_cfg, 'source', None), 'lang_code', 'zh') or 'zh'
    targets = getattr(i18n_cfg, 'targets', []) if i18n_cfg else []
    all_target_codes = [src_code] + [getattr(t, 'lang_code', '') for t in targets if getattr(t, 'lang_code', None)]

    site_name = getattr(engine.config, 'site_name', 'Illacme Press') if hasattr(engine, 'config') else 'Illacme Press'

    for lang in all_target_codes:
        is_source = (lang == src_code)
        lang_site_dir = site_dir if is_source else os.path.join(site_dir, lang)
        out_blog_dir = os.path.join(lang_site_dir, 'blog')
        os.makedirs(out_blog_dir, exist_ok=True)
        out_html_file = os.path.join(out_blog_dir, 'index.html')

        root_path = "../" if is_source else "../../"

        # 构建各视图内容
        l_low = lang.lower()
        if l_low.startswith('zh') or l_low == 'auto' or is_source:
            hero_title = "✍️ 博文存档与前沿洞察"
            hero_desc = "探索技术洞察、出版手记与前沿数字工程。从段落级缓存架构到 AI 原生出版哲学。"
            view_timeline_label = "时间轴"
            view_grid_label = "网格卡片"
            all_tag_label = "全部"
            read_more_label = "阅读全文 →"
        elif l_low.startswith('en'):
            hero_title = "✍️ Blog Archive & Insights"
            hero_desc = "Explore technical insights, publishing notes, and digital sovereignty engineering."
            view_timeline_label = "Timeline"
            view_grid_label = "Grid Cards"
            all_tag_label = "All"
            read_more_label = "Read More →"
        elif l_low.startswith('ja'):
            hero_title = "✍️ ブログアーカイブ"
            hero_desc = "技術的洞察、出版ノート、デジタル主権エンジニアリングを探求します。"
            view_timeline_label = "タイムライン"
            view_grid_label = "グリッド"
            all_tag_label = "すべて"
            read_more_label = "続きを読む →"
        else:
            hero_title = "✍️ Blog Archive"
            hero_desc = "Explore technical insights and publishing notes."
            view_timeline_label = "Timeline"
            view_grid_label = "Grid"
            all_tag_label = "All"
            read_more_label = "Read More →"

        # A. 标签筛选栏
        tag_chips = [f'<button class="blog-tag-filter active" data-tag="all">{all_tag_label} ({len(blog_posts)})</button>']
        for t in sorted(all_tags):
            tag_chips.append(f'<button class="blog-tag-filter" data-tag="{t}">{t}</button>')
        tag_chips_html = '\n'.join(tag_chips)

        # B. 网格卡片 (Grid Cards)
        cards_html = []
        for post in blog_posts:
            p_title = post['title']
            p_desc = post['desc']
            if not is_source and post.get('translations', {}).get(lang):
                t_info = post['translations'][lang]
                p_title = t_info.get('title') or (t_info.get('seo', {}) or {}).get('og_title') or p_title
                p_desc = (t_info.get('seo', {}) or {}).get('description') or p_desc

            tags_str = ','.join(post['tags'])
            first_tag = post['tags'][0] if post['tags'] else 'Blog'
            href = f"./{post['slug']}.html"

            cards_html.append(f"""
            <a href="{href}" class="card-pioneer blog-card" data-tags="{tags_str}">
                <span class="card-tag">{first_tag}</span>
                <h3>{p_title}</h3>
                <p>{p_desc}</p>
                <div class="card-meta">
                    <span>📅 {post['date']}</span>
                </div>
                <div class="card-footer">
                    <span class="read-more">{read_more_label}</span>
                </div>
            </a>""")
        grid_view_html = f'<div class="blog-grid-view blog-grid" id="view-grid">{"".join(cards_html)}</div>'

        # C. 时间轴视图 (Timeline)
        timeline_items = []
        for post in blog_posts:
            p_title = post['title']
            p_desc = post['desc']
            if not is_source and post.get('translations', {}).get(lang):
                t_info = post['translations'][lang]
                p_title = t_info.get('title') or (t_info.get('seo', {}) or {}).get('og_title') or p_title
                p_desc = (t_info.get('seo', {}) or {}).get('description') or p_desc

            tags_str = ','.join(post['tags'])
            tags_badges = ''.join([f'<span class="timeline-tag">{t}</span>' for t in post['tags']])
            href = f"./{post['slug']}.html"

            timeline_items.append(f"""
            <div class="timeline-item" data-tags="{tags_str}">
                <div class="timeline-node"></div>
                <div class="timeline-meta">
                    <span>📅 {post['date']}</span>
                    <div class="timeline-tags">{tags_badges}</div>
                </div>
                <a href="{href}" class="timeline-title">{p_title}</a>
                <p class="timeline-desc">{p_desc}</p>
            </div>""")
        timeline_view_html = f"""
        <div class="blog-timeline-view active" id="view-timeline">
            <div class="timeline-tree">
                {"".join(timeline_items)}
            </div>
        </div>"""

        body_html = f"""
        <div id="blog-app">
            <section class="blog-hero-section">
                <h1 class="list-hero-title">{hero_title}</h1>
                <p class="list-hero-desc">{hero_desc}</p>
                <div class="blog-toolbar">
                    <div class="blog-tag-scroller">
                        {tag_chips_html}
                    </div>
                    <div class="blog-view-switcher">
                        <button class="view-switch-btn active" data-view="timeline">
                            <span>🕒</span> <span>{view_timeline_label}</span>
                        </button>
                        <button class="view-switch-btn" data-view="grid">
                            <span>🎛️</span> <span>{view_grid_label}</span>
                            <span class="view-btn-badge">{len(blog_posts)}</span>
                        </button>
                    </div>
                </div>
            </section>
            {timeline_view_html}
            {grid_view_html}
        </div>
        """

        fm = {
            "title": hero_title,
            "layout": "blog",
            "slug": "index",
            "route_prefix": "blog",
            "description": hero_desc
        }

        sub_path_for_render = f"{lang}/blog/index.html" if not is_source else "blog/index.html"
        full_html = render_html_page(
            html_content=body_html,
            fm=fm,
            target_lang=lang,
            sub_path=sub_path_for_render,
            root_path=root_path,
            site_name=site_name,
            i18n_cfg=i18n_cfg,
            engine=engine
        )

        with open(out_html_file, 'w', encoding='utf-8') as f:
            f.write(full_html)

        if hasattr(engine, 'janitor'):
            engine.janitor.mark_as_fresh(out_html_file)
