#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - SSG Rendering Base
模块职责：定义 SSG 输出端渲染器的基类协议。
🛡️ [AEL-Iter-v5.3]：全链路解耦的渲染基座。
"""
import abc
from typing import Tuple, Dict, Any, List

from .mixins import CITemplateMixin

# 🌍 [V100.9] 全量 50 语种导航标准字典矩阵 (100% 对齐 SUPPORTED_MATRIX)
SLOT_I18N_FALLBACK: Dict[str, Dict[str, str]] = {
    "docs": {
        "zh": "文档中心", "zh-hans": "文档中心", "zh-hant": "文檔中心", "en": "Documentation",
        "hi": "दस्तावेज़", "es": "Documentación", "fr": "Documentation", "ar": "التوثيق",
        "bn": "নথিপত্র", "pt": "Documentação", "ru": "Документация", "ur": "دستاویزات",
        "id": "Dokumentasi", "de": "Dokumentation", "ja": "ドキュメント", "mr": "दस्तऐवजीकरण",
        "te": "డాక్యుమెంటేషన్", "tr": "Belgeler", "ta": "ஆவணங்கள்", "vi": "Tài liệu",
        "tl": "Dokumentasyon", "ko": "문서 센터", "fa": "مستندات", "ha": "Takardu",
        "sw": "Nyaraka", "jv": "Dokumentasi", "it": "Documentazione", "pa": "ਦਸਤਾਵੇਜ਼",
        "kn": "ದಾಖಲೆಗಳು", "gu": "દસ્તાવેજીકરણ", "th": "เอกสาร", "am": "ሰነዶች",
        "yo": "Àwọn àkọsílẹ̀", "my": "စာရွက်စာတမ်းများ", "om": "Sanadoota", "ps": "اسناد",
        "uk": "Документація", "su": "Dokuméntasi", "pl": "Dokumentacja", "uz": "Hujjatlar",
        "ro": "Documentație", "az": "Sənədlər", "ml": "രേഖകൾ", "sd": "دستاويز",
        "ig": "Akwụkwọ", "hu": "Dokumentáció", "el": "Τεκμηρίωση", "cs": "Dokumentace",
        "nl": "Documentatie", "sv": "Dokumentation", "fi": "Dokumentaatio", "no": "Dokumentasjon"
    },
    "blog": {
        "zh": "官方博客", "zh-hans": "官方博客", "zh-hant": "官方博客", "en": "Blog",
        "hi": "ब्लॉग", "es": "Blog", "fr": "Blog", "ar": "المدونة",
        "bn": "ব্লগ", "pt": "Blog", "ru": "Блог", "ur": "بلاگ",
        "id": "Blog", "de": "Blog", "ja": "ブログ", "mr": "ब्लॉग",
        "te": "బ్లాగ్", "tr": "Blog", "ta": "வலைப்பதிவு", "vi": "Blog",
        "tl": "Blog", "ko": "블로그", "fa": "وبلاگ", "ha": "Blog",
        "sw": "Blogu", "jv": "Blog", "it": "Blog", "pa": "ਬਲੌਗ",
        "kn": "ಬ್ಲಾಗ್", "gu": "બ્લોગ", "th": "บล็อก", "am": "ብሎግ",
        "yo": "Búlọ́ọ̀gì", "my": "ဘလော့ဂ်", "om": "Biloogii", "ps": "بلاګ",
        "uk": "Блог", "su": "Blog", "pl": "Blog", "uz": "Blog",
        "ro": "Blog", "az": "Bloq", "ml": "ബ്ലോഗ്", "sd": "بلاگ",
        "ig": "Blọọgụ", "hu": "Blog", "el": "Ιστολόγιο", "cs": "Blog",
        "nl": "Blog", "sv": "Blogg", "fi": "Blogi", "no": "Blogg"
    },
    "pages": {
        "zh": "展示页面", "zh-hans": "展示页面", "zh-hant": "展示頁面", "en": "Showcase",
        "hi": "प्रदर्शनी", "es": "Exhibición", "fr": "Vitrines", "ar": "المعرض",
        "bn": "শোকেস", "pt": "Vitrine", "ru": "Витрина", "ur": "شوکیس",
        "id": "Showcase", "de": "Seiten", "ja": "ショーケース", "mr": "प्रदर्शन",
        "te": "ప్రదర్శన", "tr": "Vitrin", "ta": "காட்சி", "vi": "Trưng bày",
        "tl": "Showcase", "ko": "쇼케이스", "fa": "ویترین", "ha": "Nunin",
        "sw": "Maonyesho", "jv": "Pameran", "it": "Vetrina", "pa": "ਸ਼ੋਕੇਸ",
        "kn": "ಪ್ರದರ್ಶನ", "gu": "પ્રદર્શન", "th": "ผลงาน", "am": "ማሳያ",
        "yo": "Àfihàn", "my": "ပြခန်း", "om": "Agarsiisa", "ps": "ننداره",
        "uk": "Вітрина", "su": "Pameran", "pl": "Prezentacja", "uz": "Vitrina",
        "ro": "Vitrină", "az": "Vitrin", "ml": "ഷോകേസ്", "sd": "ڏيکاءُ",
        "ig": "Ngosipụta", "hu": "Bemutató", "el": "Βιτρίνα", "cs": "Ukázky",
        "nl": "Showcase", "sv": "Showcase", "fi": "Esittely", "no": "Showcase"
    },
    "custom": {
        "zh": "自定义频道", "zh-hans": "自定义频道", "zh-hant": "自定義頻道", "en": "Channel",
        "hi": "चैनल", "es": "Canal", "fr": "Canal", "ar": "القناة",
        "bn": "চ্যানেল", "pt": "Canal", "ru": "Канал", "ur": "چینل",
        "id": "Kanal", "de": "Kanal", "ja": "チャンネル", "mr": "चॅनेल",
        "te": "ఛానల్", "tr": "Kanal", "ta": "சேனல்", "vi": "Kênh",
        "tl": "Channel", "ko": "채널", "fa": "کانال", "ha": "Tashar",
        "sw": "Idhaa", "jv": "Saluran", "it": "Canale", "pa": "ਚੈਨਲ",
        "kn": "ಚಾನಲ್", "gu": "ચેનલ", "th": "ช่อง", "am": "ቻናል",
        "yo": "Ipa ọ̀nà", "my": "ချန်နယ်", "om": "Madaala", "ps": "چینل",
        "uk": "Канал", "su": "Saluran", "pl": "Kanał", "uz": "Kanal",
        "ro": "Canal", "az": "Kanal", "ml": "ചാനൽ", "sd": "چينل",
        "ig": "Ọwa", "hu": "Csatorna", "el": "Κανάλι", "cs": "Kanál",
        "nl": "Kanaal", "sv": "Kanal", "fi": "Kanava", "no": "Kanal"
    }
}

class BaseSSGAdapter(CITemplateMixin, abc.ABC):
    PLUGIN_ID = "generic"
    """所有 SSG 渲染插件的抽象基类"""
    
    @classmethod
    def get_default_path_mappings(cls) -> Dict[str, str]:
        """🚀 [V76.0] 声明该适配器推荐的原生默认物理寻址映射"""
        return {
            'source_dir': "src/content",
            'site_dir': "dist",
            'assets_dir': "public/assets",
            'graph_json_dir': "public"
        }

    @classmethod
    def get_build_command(cls) -> str:
        """🚀 [V105.0] 默认 SSG 静态构建命令"""
        return "python plenipes.py --sync"

    def __init__(self, theme_settings: Any = None, engine=None):
        self.theme_settings = theme_settings
        self.engine = engine
        self.default_lang = "zh"
        # 🚀 [V11.2] 双相出口扩展名定义
        self.output_extensions = {
            "source": None,  # 🚀 [V12.0] None 表示跟随原文件后缀
            "static": ".html"
        }
        # 🚀 [V11.2] 默认语言路径契约：是否强制在物理路径中包含语言前缀
        self.force_default_lang_prefix = False
        # 🚀 [V15.6] 元数据主权：定义哪些输出后缀支持 Frontmatter
        self.frontmatter_extensions = [".md", ".mdx", ".markdown"]
        # 🚀 [V80.0] 自动物理探测并加载主题自描述 JSON Schema 协议
        import os
        import json
        self.theme_schema = {}
        if self.theme_settings:
            theme_name = getattr(self.theme_settings, 'name', 'sovereign')
            if theme_name == 'default': theme_name = 'sovereign'
            if self.engine and hasattr(self.engine, 'paths') and self.engine.paths:
                themes_root = self.engine.paths.get("themes", "themes")
            elif self.engine and hasattr(self.engine, '_resolve_path'):
                themes_root = self.engine._resolve_path("themes")
            else:
                themes_root = "themes"
            schema_path = os.path.join(themes_root, theme_name, "theme.schema.json")
            if os.path.exists(schema_path):
                try:
                    with open(schema_path, 'r', encoding='utf-8') as f:
                        self.theme_schema = json.load(f)
                except Exception:
                    pass

    def get_custom_options(self) -> Dict[str, Any]:
        """
        🚀 [V80.0] 获取并合并强校验的主题自定义选项映射。
        自动将用户填写的 theme_settings.options 与主题 schema 默认值进行深层合并，实现自愈降级。
        """
        options = {}
        properties = self.theme_schema.get("properties", {})
        for key, prop in properties.items():
            if "default" in prop:
                options[key] = prop["default"]
                
        # 🚀 [Unified Promotion Architecture] 引入全局基础信息继承层 (I&O Engine)
        # 如果全局配置中定义了通用合规与视觉基础，将其作为基底加载（实现跨主题单一数据源）
        if hasattr(self, 'engine') and self.engine and hasattr(self.engine, 'config'):
            cfg = self.engine.config
            
            # 自愈逻辑：site_name Fallback 为 imprint_name/press_name; site_description Fallback 为 imprint_description
            g_site_name = getattr(cfg, "site_name", None) or getattr(cfg, "imprint_name", None)
            g_site_desc = getattr(cfg, "site_description", None) or getattr(cfg, "imprint_description", None)
            
            # 版权声明自愈逻辑：彻底合并为单数据源，直接继承自全域默认版权设置 frontmatter_defaults.copyright
            fm_defaults = getattr(cfg, "frontmatter_defaults", {}) or {}
            g_copyright = fm_defaults.get("copyright", None)
            
            global_promotions = {
                "site_name": g_site_name,
                "site_description": g_site_desc,
                "favicon_path": getattr(cfg, "favicon_path", None),
                "logo_path": getattr(cfg, "logo_path", None),
                "footer_copyright": g_copyright
            }
            
            for g_key, g_val in global_promotions.items():
                if g_val is not None and str(g_val).strip() != "":
                    options[g_key] = g_val
                    
        if self.theme_settings and hasattr(self.theme_settings, 'options') and self.theme_settings.options:
            for key, val in self.theme_settings.options.items():
                if val is not None and str(val).strip() != "":
                    options[key] = val
        return options

    @abc.abstractmethod
    def render(self, body: str, fm: Dict[str, Any], seo_data: Dict[str, Any] = None, target_lang: str = "en", sub_path: str = "") -> Tuple[str, Dict[str, Any]]:
        """[Contract] 执行特定 SSG 的语法转换与元数据增强。"""
        pass

    def supports_frontmatter(self, ext: str) -> bool:
        """🚀 [V15.6] 判定特定扩展名是否支持元数据头"""
        if not ext: return False
        return ext.lower() in self.frontmatter_extensions

    def get_output_schema(self) -> List[str]:
        """🚀 [V11.2] 获取该适配器支持的输出出口列表。"""
        schema = ["source"]
        if hasattr(self, 'active_renderer') and self.active_renderer:
            schema.append("static")
        return schema

    def get_feature_slots(self) -> Dict[str, Dict[str, str]]:
        """🚀 [V56.0/V80.0] 意图感知协议：声明该适配器支持的功能槽及其物理路径映射。
        优先从 theme.schema.json 中动态读取，实现数据驱动的零代码适配。"""
        if hasattr(self, 'theme_schema') and self.theme_schema and 'slots' in self.theme_schema:
            return self.theme_schema['slots']
            
        return {
            "docs": {"label": "文档中心", "single": "docs", "multi": "i18n/{lang}/docs"},
            "blog": {"label": "博客文章", "single": "blog", "multi": "i18n/{lang}/blog"},
            "pages": {"label": "独立页面", "single": "pages", "multi": "i18n/{lang}/pages"},
            "static": {"label": "静态资产", "single": "static", "multi": "static"}
        }

    def adapt_metadata(self, fm: dict, date_obj, author_name) -> dict:
        """[Sovereignty] 物理元数据方言适配"""
        return fm

    def inject_seo(self, fm: dict, desc_or_data: Any, keywords: list = None) -> dict:
        """[SEO] 框架感知的 SEO 字段映射协议"""
        from .seo_helper import inject_seo_helper
        return inject_seo_helper(fm, desc_or_data, keywords)

    def get_language_code(self, logic_code: str) -> str:
        """[Sovereignty] 物理路径语种对齐。"""
        from core.utils.language_hub import LanguageHub
        iso_code = LanguageHub.resolve_to_iso(logic_code)
        if not self.force_default_lang_prefix and iso_code == LanguageHub.resolve_to_iso(self.default_lang):
            return ""
        return LanguageHub.get_physical_path(iso_code, "generic")

    def get_i18n_path_template(self, source_type: str = "docs") -> str:
        """
        [Sovereignty] 获取当前 SSG 的多语言路径模版。
        """
        return "{lang}/{sub_dir}"

    def generate_navigation_items(self) -> Dict[str, Any]:
        """
        🧭 [V100.9 Universal Navigation Synthesis]
        根据引擎配置的 route_matrix 自动合成适配各 SSG 主题的全景导航结构。
        输出包括：
          - navbar_items: 兼容 Docusaurus/Nextra/VitePress 的对象列表
          - nav_links: 兼容 Sovereign/Starlight/Astro 模板的轻量链接列表
        """
        routes = getattr(self.engine.config, 'route_matrix', []) if self.engine and hasattr(self.engine, 'config') else []
        
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
            github_repo = getattr(self.theme_settings, 'options', {}).get('github_repo') if self.theme_settings else None
            if not github_repo and self.engine and hasattr(self.engine, 'config'):
                g_url = getattr(self.engine.config, 'site_url', '') or ''
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
        if self.engine and hasattr(self.engine, 'config') and getattr(self.engine.config, 'i18n_settings', None):
            i18n_cfg = self.engine.config.i18n_settings
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

    def compile_theme_options(self) -> bool:
        """
        🎯 [SSG 热对齐] 将用户最新的自定义主题选项编译并输出为物理层样式，
        使 SSG 引擎或前台预览能免刷新、瞬时热感知。
        """
        options = self.get_custom_options()
        theme_name = getattr(self.theme_settings, 'name', 'sovereign')
        if theme_name == 'default':
            theme_name = 'sovereign'
        
        # 🚀 [Docusaurus 适配自愈] 针对 Docusaurus navbar logo 路径在子目录/多语言下需为相对路径以正确水合的特性，在写入物理桥接前自动剥离首斜杠及冗余的 static/ 前缀
        if theme_name == "docusaurus":
            if "logo_path" in options:
                l_path = options["logo_path"]
                if l_path and not l_path.startswith("http") and not l_path.startswith("//"):
                    if l_path.startswith("/"):
                        l_path = l_path[1:]
                    if l_path.startswith("static/"):
                        l_path = l_path[len("static/"):]
                    options["logo_path"] = l_path
            
            # 🚀 [Docusaurus i18n 与路径动态自愈] 对齐多语种配置与 docs 默认路径
            if self.engine and hasattr(self.engine, 'config') and self.engine.config.i18n_settings:
                i18n_cfg = self.engine.config.i18n_settings
                
                source_logic = i18n_cfg.source.lang_code or "zh"
                default_locale = self.get_language_code(source_logic)
                if not default_locale:
                    default_locale = "zh-Hans" if "zh" in source_logic.lower() else source_logic.lower()
                
                locales = [default_locale]
                
                from core.utils.language_hub import LanguageHub
                default_label = i18n_cfg.source.name or LanguageHub.resolve_to_name(default_locale)
                locale_configs = {
                    default_locale: {
                        "label": default_label,
                        "direction": "ltr"
                    }
                }
                
                if i18n_cfg.enabled and i18n_cfg.targets:
                    from core.config.models.governance import PublishingMode
                    pub_mode = self.engine.config.governance.publishing_mode if hasattr(self.engine.config, 'governance') else None
                    if pub_mode == PublishingMode.GLOBAL:
                        for target in i18n_cfg.targets:
                            target_logic = target.lang_code
                            target_locale = self.get_language_code(target_logic)
                            if not target_locale:
                                target_locale = target_logic.lower()
                            if target_locale not in locales:
                                locales.append(target_locale)
                                locale_configs[target_locale] = {
                                    "label": target.name or LanguageHub.resolve_to_name(target_locale),
                                    "direction": "ltr"
                                }
                
                options["i18n"] = {
                    "defaultLocale": default_locale,
                    "locales": locales,
                    "localeConfigs": locale_configs
                }
                
                options["default_docs_path"] = "docs"
                options["default_blog_path"] = "blog"
                options["default_pages_path"] = "src/pages"
        
        # 🧭 [V100.9 Universal Navigation Synthesis] 自动将频道映射合成全景导航结构，注入 theme.options
        nav_data = self.generate_navigation_items()
        options["navbar_items"] = nav_data.get("navbar_items", [])
        options["nav_links"] = nav_data.get("nav_links", [])
        options["navbar_items_i18n"] = nav_data.get("navbar_items_i18n", {})
        options["nav_links_i18n"] = nav_data.get("nav_links_i18n", {})
        
        import os
        if self.engine and hasattr(self.engine, 'paths') and self.engine.paths:
            themes_root = self.engine.paths.get("themes", "themes")
        elif self.engine and hasattr(self.engine, '_resolve_path'):
            themes_root = self.engine._resolve_path("themes")
        else:
            themes_root = "themes"
            
        theme_dir = os.path.join(themes_root, theme_name)
        assets_dir = os.path.join(theme_dir, "static", "assets")
        if not os.path.exists(assets_dir):
            os.makedirs(assets_dir, exist_ok=True)
            
        style_path = os.path.join(assets_dir, "theme.options.css")
        
        # 🚀 [V88.8] 原厂样式防卫拦截网：在未显式勾选自定义开关时，完全不编译输出任何 CSS 视觉变量，以 100% 保持主题出厂的最佳质感与稳健度！
        if not options.get('enable_custom_style', False):
            try:
                if os.path.exists(style_path):
                    os.remove(style_path)
            except Exception:
                pass
                
            # 虽清除/不输出高危 CSS 视觉变量，但保留导出基础 JS/JSON 桥接文件，确保 site_name, logo 等非破坏性工程参数安全生效
            json_path = os.path.join(theme_dir, "theme.options.json")
            js_path = os.path.join(theme_dir, "theme.options.js")
            try:
                import json
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(options, f, indent=2, ensure_ascii=False, default=str)
                js_content = "/**\n * 🚀 [V88.0 Live Hot-Reload] 自动生成的主题选项常量，请勿手动编辑\n */\n"
                js_content += f"export const themeOptions = {json.dumps(options, indent=2, ensure_ascii=False, default=str)};\n"
                js_content += "export default themeOptions;\n"
                with open(js_path, 'w', encoding='utf-8') as f:
                    f.write(js_content)
            except Exception:
                pass
            return True
            
        css_vars = []
        for k, v in options.items():
            if isinstance(v, (str, int, float)) and not str(v).startswith("http"):
                css_key = k.replace("_", "-")
                css_vars.append(f"  --{css_key}: {v};")
                
        css_content = "/* 🚀 [V74.96 Live Hot-Reload] 自动生成的主题运行时变量对齐，请勿手动编辑 */\n"
        css_content += ":root {\n" + "\n".join(css_vars) + "\n}\n"
        
        try:
            with open(style_path, 'w', encoding='utf-8') as f:
                f.write(css_content)
        except Exception:
            pass
            
        # 🚀 [V88.0] 物理 JSON 桥接：将自愈合并后的自定义选项导出至主题根目录，供异构 SSG 编译热加载
        json_path = os.path.join(theme_dir, "theme.options.json")
        try:
            import json
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(options, f, indent=2, ensure_ascii=False, default=str)
        except Exception:
            pass
            
        # 🚀 [V88.0] 纯前端 JS 桥接：生成无 Node.js 模块依赖的纯前端 JS 常量文件，彻底绕过 Webpack/Vite 客户端打包时的 fs 模块丢失限制
        js_path = os.path.join(theme_dir, "theme.options.js")
        try:
            import json
            js_content = "/**\n * 🚀 [V88.0 Live Hot-Reload] 自动生成的主题选项常量，请勿手动编辑\n */\n"
            js_content += f"export const themeOptions = {json.dumps(options, indent=2, ensure_ascii=False, default=str)};\n"
            js_content += "export default themeOptions;\n"
            with open(js_path, 'w', encoding='utf-8') as f:
                f.write(js_content)
        except Exception:
            pass
            
        return True
