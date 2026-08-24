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

        # 默认回退槽位标签与图标
        slot_label_fallback = {
            "docs": "文档中心",
            "blog": "官方博客",
            "pages": "展示页面",
            "custom": "自定义频道"
        }
        slot_icon_fallback = {
            "docs": "📚",
            "blog": "📰",
            "pages": "📄",
            "custom": "🌐"
        }

        nav_items = []

        # 1. 过滤并排序需要展示在导航栏的项
        visible_routes = [r for r in routes if getattr(r, 'show_in_nav', True)]
        try:
            visible_routes.sort(key=lambda x: getattr(x, 'nav_order', 0))
        except Exception:
            pass

        for r in visible_routes:
            slot = getattr(r, 'target_slot', 'docs') or 'docs'
            source = getattr(r, 'source', '')
            prefix = getattr(r, 'prefix', '') or (source.lower() if source else '')
            prefix = prefix.strip('/')

            # 计算标签名
            label = getattr(r, 'nav_label', None)
            if not label:
                if source:
                    label = source
                else:
                    label = slot_label_fallback.get(slot, slot.capitalize())

            icon = getattr(r, 'nav_icon', None) or slot_icon_fallback.get(slot, '📄')
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
                target_path = f"/{prefix}/" if prefix else "/"
                if slot == "docs":
                    nav_items.append({
                        "type": "docSidebar",
                        "sidebarId": "tutorialSidebar",
                        "position": position,
                        "label": f"{icon} {label}".strip() if icon else label,
                        "raw_label": label,
                        "icon": icon,
                        "to": target_path,
                        "target_slot": "docs"
                    })
                else:
                    nav_items.append({
                        "type": "link",
                        "to": target_path,
                        "label": f"{icon} {label}".strip() if icon else label,
                        "raw_label": label,
                        "icon": icon,
                        "position": position,
                        "target_slot": slot
                    })

        # 若未配置任何 route_matrix，提供自愈默认项 (Docs + Blog)
        if not nav_items:
            nav_items = [
                {
                    "type": "docSidebar",
                    "sidebarId": "tutorialSidebar",
                    "position": "left",
                    "label": "📚 文档中心",
                    "raw_label": "文档中心",
                    "icon": "📚",
                    "to": "/docs/",
                    "target_slot": "docs"
                },
                {
                    "type": "link",
                    "to": "/blog/",
                    "label": "📰 官方博客",
                    "raw_label": "官方博客",
                    "icon": "📰",
                    "position": "left",
                    "target_slot": "blog"
                }
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
                if "github.com" in g_url:
                    github_repo = g_url
                else:
                    github_repo = 'https://github.com/Illacme/illacme-plenipes'
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
            def_lang = getattr(i18n_cfg.source, 'lang_code', 'zh') or 'zh'
            targets = [t.lang_code for t in getattr(i18n_cfg, 'targets', []) if getattr(t, 'enabled', True) and t.lang_code]
            langs = [def_lang] + [t for t in targets if t != def_lang]
            if langs:
                enabled_languages = list(set(enabled_languages + langs))

        navbar_items_i18n = {}
        nav_links_i18n = {}
        for l_code in enabled_languages:
            l_items = []
            for r in visible_routes:
                slot = getattr(r, 'target_slot', 'docs') or 'docs'
                source = getattr(r, 'source', '')
                prefix = getattr(r, 'prefix', '') or (source.lower() if source else '')
                prefix = prefix.strip('/')
                icon = getattr(r, 'nav_icon', None) or slot_icon_fallback.get(slot, '📄')
                position = getattr(r, 'nav_position', 'left') or 'left'
                ext_url = getattr(r, 'external_url', None)

                # 优先读取自定义字典 -> 其次读取内置术语字典 -> 最后回落到默认主语言
                i18n_map = getattr(r, 'nav_label_i18n', {}) or {}
                if isinstance(i18n_map, dict) and i18n_map.get(l_code):
                    l_label = i18n_map.get(l_code)
                elif slot in SLOT_I18N_FALLBACK and l_code in SLOT_I18N_FALLBACK[slot]:
                    l_label = SLOT_I18N_FALLBACK[slot][l_code]
                else:
                    l_label = getattr(r, 'nav_label', None) or (source if source else slot_label_fallback.get(slot, slot.capitalize()))

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
                    target_path = f"/{prefix}/" if prefix else "/"
                    if slot == "docs":
                        l_items.append({
                            "type": "docSidebar",
                            "sidebarId": "tutorialSidebar",
                            "position": position,
                            "label": display_l_label,
                            "raw_label": l_label,
                            "icon": icon,
                            "to": target_path,
                            "target_slot": "docs"
                        })
                    else:
                        l_items.append({
                            "type": "link",
                            "to": target_path,
                            "label": display_l_label,
                            "raw_label": l_label,
                            "icon": icon,
                            "position": position,
                            "target_slot": slot
                        })

            if not l_items:
                l_items = nav_items

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
