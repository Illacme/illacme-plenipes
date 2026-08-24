# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Generic SSG Adapter Navigation Builder Shard
模块职责：提供 Universal 主题与通用 SSG 的导航架构。
包含文档侧边栏树构建、原稿 Slug 映射提取与多语言切换器生成。
"""

import os
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
                "group": "⚙️ 3. 算力、主题与多语言",
                "items": [
                    {"title": "🧠 算力中心与 AI 翻译配置", "slug": "compute-and-ai", "stems": ["compute-and-ai", "compute-center-ai-translation-setup-guide"]},
                    {"title": "🌍 多语言矩阵与内容治理", "slug": "i18n-guide", "stems": ["i18n-guide"]},
                    {"title": "🎨 装帧主题与视觉定制", "slug": "themes-and-binding", "stems": ["themes-and-binding", "binding-themes-visual-customization"]},
                ]
            },
            {
                "group": "🛰️ 4. 全域分发与排障",
                "items": [
                    {"title": "🛰️ 分发矩阵与渠道配置", "slug": "distribution-channels", "stems": ["distribution-channels", "matrix-channel-configuration"]},
                    {"title": "❓ 常见问题与排障手册 (FAQ)", "slug": "faq", "stems": ["faq", "common-issues-and-troubleshooting-manual-faq"]},
                ]
            }
        ]

    # 尝试从引擎账本中匹配实际存在的 slug，保证点击不会 404
    slug_map = get_doc_slug_map(engine)

    html_parts = ['<nav class="universal-docs-sidebar"><div class="sidebar-inner">']
    for grp in default_groups:
        html_parts.append(f'<div class="sidebar-group"><div class="sidebar-group-title">{grp["group"]}</div><ul class="sidebar-nav-list">')
        for item in grp["items"]:
            actual_slug = item["slug"]
            # 若配置了别名列表，尝试在映射表中找存在的真实 slug
            for stem in item.get("stems", []):
                if stem.lower() in slug_map:
                    actual_slug = slug_map[stem.lower()]["slug"]
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

    return "".join(html_parts)


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
