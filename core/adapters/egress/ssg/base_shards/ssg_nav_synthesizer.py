#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - SSG Navigation Synthesizer
模块职责：根据引擎配置的 route_matrix 自动合成适配各 SSG 主题的全景导航结构。
🛡️ [SOP-02 模块拆分 / AEL-Iter-v10.3 基因克隆]
"""
from typing import Dict, Any
from .ssg_slot_matrix import SLOT_I18N_FALLBACK


class SSGNavSynthesizer:
    @staticmethod
    def generate_navigation_items(adapter: Any) -> Dict[str, Any]:
        """
        🧭 [V100.9 Universal Navigation Synthesis]
        根据引擎配置的 route_matrix 自动合成适配各 SSG 主题的全景导航结构。
        输出包括：
          - navbar_items: 兼容 Docusaurus/Nextra/VitePress 的对象列表
          - nav_links: 兼容 Sovereign/Starlight/Astro 模板的轻量链接列表
        """
        routes = getattr(adapter.engine.config, 'route_matrix', []) if adapter.engine and hasattr(adapter.engine, 'config') else []
        if not isinstance(routes, list):
            routes = []

        # 🚀 读取网址组织形态 (flat/prefix/nested)
        dir_mode = 'nested'
        if adapter.engine and hasattr(adapter.engine, 'config'):
            trans_cfg = getattr(adapter.engine.config, 'translation', None)
            dir_mode = getattr(trans_cfg, 'slug_dir_mode', 'nested') if trans_cfg else 'nested'

        default_lang = getattr(adapter, 'default_lang', 'zh') or 'zh'
        force_src_prefix = getattr(adapter, 'force_source_prefix', False)
        is_clean_url = getattr(adapter, 'clean_urls', False) or getattr(adapter, 'is_framework', False) or (getattr(adapter, 'PLUGIN_ID', '') in ('starlight', 'docusaurus', 'nextra', 'vitepress'))

        def _calc_target_path(p_prefix: str, p_slot: str, p_lang_prefix: str = "") -> str:
            """统一计算符合 Clean URL 规范与多语言隔离的导航目标路径"""
            is_standalone = (p_slot in ("pages", "page") or p_prefix in ("about", "terms", "privacy", "disclaimer", "contact"))
            clean_p = p_prefix.strip('/')
            p_lang = f"/{p_lang_prefix.strip('/')}" if p_lang_prefix.strip('/') else ""
            if is_clean_url:
                if is_standalone:
                    return f"{p_lang}/{clean_p}" if clean_p else (f"{p_lang}" if p_lang else "/")
                return f"{p_lang}/{clean_p}/" if clean_p else (f"{p_lang}/" if p_lang else "/")
            if is_standalone:
                return f"{p_lang}/{clean_p}.html" if clean_p else (f"{p_lang}/index.html" if p_lang else "/")
            if dir_mode == 'flat' and clean_p:
                return f"{p_lang}/{clean_p}.html"
            if dir_mode == 'prefix' and clean_p:
                return f"{p_lang}/{clean_p}-index.html"
            return f"{p_lang}/{clean_p}/" if clean_p else (f"{p_lang}/" if p_lang else "/")

        slot_label_fallback = {
            "docs": "文档中心",
            "blog": "官方博客",
            "pages": "展示页面",
            "showcase": "产品特性",
            "custom": "自定义频道"
        }
        slot_icon_fallback = {
            "docs": "📚",
            "blog": "📰",
            "pages": "📄",
            "showcase": "🎨",
            "custom": "🌐"
        }

        # 1. 过滤并排序需要展示在导航栏的项
        visible_routes = [r for r in routes if getattr(r, 'show_in_nav', True)]
        try:
            visible_routes.sort(key=lambda x: getattr(x, 'nav_order', 0))
        except Exception:
            pass

        nav_items = []
        for r in visible_routes:
            slot = getattr(r, 'target_slot', 'docs') or 'docs'
            source = getattr(r, 'source', '')
            prefix = getattr(r, 'prefix', '') or (source.lower() if source else '')
            prefix = prefix.strip('/')

            label = getattr(r, 'nav_label', None)
            if not label:
                if source:
                    label = source
                elif prefix == "about":
                    label = "关于我们"
                else:
                    label = slot_label_fallback.get(slot, slot.capitalize())

            icon = getattr(r, 'nav_icon', None) or ('✨' if prefix == 'about' else slot_icon_fallback.get(slot, '📄'))
            position = getattr(r, 'nav_position', 'left') or 'left'
            ext_url = getattr(r, 'external_url', None)

            if ext_url:
                nav_items.append({
                    "type": "link",
                    "label": f"{icon} {label}".strip() if icon else label,
                    "raw_label": label,
                    "icon": icon,
                    "href": ext_url,
                    "position": position,
                    "external": True,
                    "target_slot": "external"
                })
            else:
                target_path = _calc_target_path(prefix, slot, default_lang if force_src_prefix else "")
                item_type = "docSidebar" if slot == "docs" else "link"
                item_dict = {
                    "type": item_type,
                    "position": position,
                    "label": f"{icon} {label}".strip() if icon else label,
                    "raw_label": label,
                    "icon": icon,
                    "to": target_path,
                    "target_slot": slot
                }
                if slot == "docs":
                    item_dict["sidebarId"] = "tutorialSidebar"
                nav_items.append(item_dict)

        # 若未配置任何 route_matrix，提供自愈默认项 (全套 4 个标准频道)
        if not nav_items:
            def_lp = default_lang if force_src_prefix else ""
            nav_items = [
                {"type": "docSidebar", "sidebarId": "tutorialSidebar", "position": "left", "label": "📚 文档指南", "raw_label": "文档指南", "icon": "📚", "to": _calc_target_path("docs", "docs", def_lp), "target_slot": "docs"},
                {"type": "link", "to": _calc_target_path("blog", "blog", def_lp), "label": "📰 演示博客", "raw_label": "演示博客", "icon": "📰", "position": "left", "target_slot": "blog"},
                {"type": "link", "to": _calc_target_path("showcase", "showcase", def_lp), "label": "🎨 产品特性", "raw_label": "产品特性", "icon": "🎨", "position": "left", "target_slot": "showcase"},
                {"type": "link", "to": _calc_target_path("about", "pages", def_lp), "label": "✨ 关于我们", "raw_label": "关于我们", "icon": "✨", "position": "left", "target_slot": "pages"}
            ]

        # 始终注入 GitHub 仓库项（若未显式配置 GitHub 且存在仓库地址）
        has_github = any(
            (item.get("target_slot") == "github" or "github" in item.get("label", "").lower() or "github" in str(item.get("href", "")).lower())
            for item in nav_items
        )
        if not has_github:
            github_repo = getattr(adapter.theme_settings, 'options', {}).get('github_repo') if adapter.theme_settings else None
            if not github_repo and adapter.engine and hasattr(adapter.engine, 'config'):
                g_url = getattr(adapter.engine.config, 'site_url', '') or ''
                github_repo = g_url if "github.com" in g_url else 'https://github.com/Illacme/illacme-plenipes'
            elif not github_repo:
                github_repo = 'https://github.com/Illacme/illacme-plenipes'

            if github_repo:
                nav_items.append({
                    "type": "link",
                    "href": github_repo,
                    "label": "GitHub",
                    "raw_label": "GitHub",
                    "icon": "🐙",
                    "position": "right",
                    "external": True,
                    "target_slot": "github"
                })

        # 🌐 [多语言矩阵导航合成] 为各启用的目标语言生成独立的本地化导航结构
        enabled_languages = ["zh", "en", "ja", "fr", "de", "es", "ru", "ar", "ko"]
        if adapter.engine and hasattr(adapter.engine, 'config') and getattr(adapter.engine.config, 'i18n_settings', None):
            i18n_cfg = adapter.engine.config.i18n_settings
            def_l = getattr(i18n_cfg.source, 'lang_code', default_lang) or default_lang
            targets = [t.lang_code for t in getattr(i18n_cfg, 'targets', []) if getattr(t, 'enabled', True) and t.lang_code]
            langs = [def_l] + [t for t in targets if t != def_l]
            if langs:
                enabled_languages = list(set(enabled_languages + langs))

        navbar_items_i18n = {}
        nav_links_i18n = {}
        for l_code in enabled_languages:
            l_prefix = l_code if (l_code != default_lang or force_src_prefix) else ""
            l_items = []
            for r in visible_routes:
                slot = getattr(r, 'target_slot', 'docs') or 'docs'
                source = getattr(r, 'source', '')
                prefix = getattr(r, 'prefix', '') or (source.lower() if source else '')
                prefix = prefix.strip('/')
                icon = getattr(r, 'nav_icon', None) or slot_icon_fallback.get(slot, '📄')
                position = getattr(r, 'nav_position', 'left') or 'left'
                ext_url = getattr(r, 'external_url', None)

                # 优先读取自定义多语言字典 -> 默认母语使用用户 nav_label -> 目标语言优先读取内置术语字典 -> 最后回落
                i18n_map = getattr(r, 'nav_label_i18n', {}) or {}
                user_nav_label = getattr(r, 'nav_label', None)
                if isinstance(i18n_map, dict) and i18n_map.get(l_code):
                    l_label = i18n_map.get(l_code)
                elif l_code == default_lang and user_nav_label:
                    l_label = user_nav_label
                elif prefix == "about":
                    l_label = "关于我们" if l_code in ("zh", "zh-hans") else (SLOT_I18N_FALLBACK.get("about", {}).get(l_code) or "About Us")
                elif slot in SLOT_I18N_FALLBACK and l_code in SLOT_I18N_FALLBACK[slot]:
                    l_label = SLOT_I18N_FALLBACK[slot][l_code]
                else:
                    l_label = user_nav_label or (source if source else slot_label_fallback.get(slot, slot.capitalize()))

                display_l_label = f"{icon} {l_label}".strip() if icon else l_label

                if ext_url:
                    l_items.append({
                        "type": "link",
                        "label": display_l_label,
                        "raw_label": l_label,
                        "icon": icon,
                        "href": ext_url,
                        "position": position,
                        "external": True,
                        "target_slot": "external"
                    })
                else:
                    target_path = _calc_target_path(prefix, slot, l_prefix)
                    item_type = "docSidebar" if slot == "docs" else "link"
                    item_dict = {
                        "type": item_type,
                        "position": position,
                        "label": display_l_label,
                        "raw_label": l_label,
                        "icon": icon,
                        "to": target_path,
                        "target_slot": slot
                    }
                    if slot == "docs":
                        item_dict["sidebarId"] = "tutorialSidebar"
                    l_items.append(item_dict)

            if not l_items:
                def_docs_lbl = SLOT_I18N_FALLBACK.get("docs", {}).get(l_code, "Documentation")
                def_blog_lbl = SLOT_I18N_FALLBACK.get("blog", {}).get(l_code, "Blog")
                def_show_lbl = SLOT_I18N_FALLBACK.get("showcase", {}).get(l_code, "Showcase")
                def_abt_lbl = "关于我们" if l_code in ("zh", "zh-hans", "zh-hant") else (SLOT_I18N_FALLBACK.get("about", {}).get(l_code) or "About Us")
                l_items = [
                    {"type": "docSidebar", "sidebarId": "tutorialSidebar", "position": "left", "label": f"📚 {def_docs_lbl}", "raw_label": def_docs_lbl, "icon": "📚", "to": _calc_target_path("docs", "docs", l_prefix), "target_slot": "docs"},
                    {"type": "link", "to": _calc_target_path("blog", "blog", l_prefix), "label": f"📰 {def_blog_lbl}", "raw_label": def_blog_lbl, "icon": "📰", "position": "left", "target_slot": "blog"},
                    {"type": "link", "to": _calc_target_path("showcase", "showcase", l_prefix), "label": f"🎨 {def_show_lbl}", "raw_label": def_show_lbl, "icon": "🎨", "position": "left", "target_slot": "showcase"},
                    {"type": "link", "to": _calc_target_path("about", "pages", l_prefix), "label": f"✨ {def_abt_lbl}", "raw_label": def_abt_lbl, "icon": "✨", "position": "left", "target_slot": "pages"}
                ]

            navbar_items_i18n[l_code] = l_items
            nav_links_i18n[l_code] = [
                {
                    "text": item.get("label", ""),
                    "raw_text": item.get("raw_label", ""),
                    "icon": item.get("icon", ""),
                    "url": item.get("to") or item.get("href", "#"),
                    "slot": item.get("target_slot", "docs"),
                    "external": item.get("external", False),
                    "position": item.get("position", "left")
                }
                for item in l_items if item.get("target_slot") != "github"
            ]

        return {
            "navbar_items": nav_items,
            "nav_links": [
                {
                    "text": item.get("label", ""),
                    "raw_text": item.get("raw_label", ""),
                    "icon": item.get("icon", ""),
                    "url": item.get("to") or item.get("href", "#"),
                    "slot": item.get("target_slot", "docs"),
                    "external": item.get("external", False),
                    "position": item.get("position", "left")
                }
                for item in nav_items if item.get("target_slot") != "github"
            ],
            "navbar_items_i18n": navbar_items_i18n,
            "nav_links_i18n": nav_links_i18n
        }
