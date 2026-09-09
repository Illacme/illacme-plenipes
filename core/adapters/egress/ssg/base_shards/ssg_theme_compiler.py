#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - SSG Theme Options Compiler
模块职责：将用户自定义主题选项热编译为物理样式 (CSS Variables) 与异构 SSG 运行时桥接 (JSON / JS)。
🛡️ [SOP-02 模块拆分 / AEL-Iter-v10.3 基因克隆]
"""
import os
import json
from typing import Any


class SSGThemeCompiler:
    @staticmethod
    def compile_theme_options(adapter: Any) -> bool:
        """
        🎯 [SSG 热对齐] 将用户最新的自定义主题选项编译并输出为物理层样式，
        使 SSG 引擎或前台预览能免刷新、瞬时热感知。
        """
        options = adapter.get_custom_options()
        theme_name = getattr(adapter.theme_settings, 'name', 'sovereign')
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
            if adapter.engine and hasattr(adapter.engine, 'config') and adapter.engine.config.i18n_settings:
                i18n_cfg = adapter.engine.config.i18n_settings

                source_logic = (i18n_cfg.source.lang_code or "zh").strip()
                default_locale = adapter.get_language_code(source_logic)
                if not default_locale or default_locale.lower() in ("auto", "none", ""):
                    default_locale = "zh-Hans"

                locales = [default_locale]

                from core.utils.language_hub import LanguageHub
                raw_label = i18n_cfg.source.name
                default_label = "简体中文" if (not raw_label or raw_label in ("自动探测", "auto", "Auto")) else raw_label
                locale_configs = {
                    default_locale: {
                        "label": default_label,
                        "direction": "ltr"
                    }
                }

                if i18n_cfg.enabled and i18n_cfg.targets:
                    from core.config.models.governance import PublishingMode
                    pub_mode = adapter.engine.config.governance.publishing_mode if hasattr(adapter.engine.config, 'governance') else None
                    if pub_mode == PublishingMode.GLOBAL:
                        for target in i18n_cfg.targets:
                            target_logic = (target.lang_code or "").strip()
                            if not target_logic or target_logic.lower() in ("auto", "none"):
                                continue
                            target_locale = adapter.get_language_code(target_logic)
                            if not target_locale or target_locale.lower() in ("auto", "none"):
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
        nav_data = adapter.generate_navigation_items()
        raw_nav_items = nav_data.get("navbar_items", [])
        if theme_name == "docusaurus":
            cleaned_nav_items = []
            for item in raw_nav_items:
                clean_item = {
                    "position": item.get("position", "left"),
                    "label": item.get("label", "")
                }
                if item.get("type") == "docSidebar":
                    clean_item["type"] = "docSidebar"
                    clean_item["sidebarId"] = item.get("sidebarId", "tutorialSidebar")
                elif item.get("href"):
                    clean_item["href"] = item["href"]
                elif item.get("to"):
                    clean_item["to"] = item["to"]
                cleaned_nav_items.append(clean_item)
            options["navbar_items"] = cleaned_nav_items
        else:
            options["navbar_items"] = raw_nav_items
        options["nav_links"] = nav_data.get("nav_links", [])
        options["navbar_items_i18n"] = nav_data.get("navbar_items_i18n", {})
        options["nav_links_i18n"] = nav_data.get("nav_links_i18n", {})

        # 🌐 [Nextra & VitePress 多语言矩阵与 Locales 桥接自愈]
        if theme_name in ("nextra", "vitepress") and adapter.engine and hasattr(adapter.engine, 'config') and getattr(adapter.engine.config, 'i18n_settings', None):
            from core.utils.language_hub import LanguageHub
            i18n_cfg = adapter.engine.config.i18n_settings
            def_lang = getattr(i18n_cfg.source, 'lang_code', 'zh') or 'zh'
            if not def_lang or def_lang == "auto":
                def_lang = "zh"
                def_name = "简体中文"
            else:
                def_name = getattr(i18n_cfg.source, 'name', None) or LanguageHub.resolve_to_name(def_lang)
            targets = [t for t in getattr(i18n_cfg, 'targets', []) if getattr(t, 'enabled', True) and getattr(t, 'lang_code', None)]

            if theme_name == "nextra":
                nextra_i18n = [{"locale": def_lang, "text": def_name}]
                for t in targets:
                    t_code = t.lang_code
                    t_name = getattr(t, 'name', None) or LanguageHub.resolve_to_name(t_code)
                    nextra_i18n.append({"locale": t_code, "text": t_name})
                options["i18n"] = nextra_i18n
                options["defaultLocale"] = def_lang

            elif theme_name == "vitepress":
                vp_locales = {
                    "root": {"label": def_name, "lang": def_lang}
                }
                for t in targets:
                    t_code = t.lang_code
                    t_name = getattr(t, 'name', None) or LanguageHub.resolve_to_name(t_code)
                    vp_locales[t_code] = {
                        "label": t_name,
                        "lang": t_code,
                        "link": f"/{t_code}/"
                    }
                options["locales"] = vp_locales

        if adapter.engine and hasattr(adapter.engine, 'paths') and adapter.engine.paths:
            themes_root = adapter.engine.paths.get("themes", "themes")
        elif adapter.engine and hasattr(adapter.engine, '_resolve_path'):
            themes_root = adapter.engine._resolve_path("themes")
        else:
            themes_root = "themes"

        theme_dir = os.path.join(themes_root, theme_name)
        assets_dir = os.path.join(theme_dir, "static", "assets")
        if not os.path.exists(assets_dir):
            os.makedirs(assets_dir, exist_ok=True)

        style_path = os.path.join(assets_dir, "theme.options.css")

        # 🧭 [Nextra / SSG 文档槽位路径自愈] 若文档槽位无子路径，纠正死链接 /docs/ 为 /quick-start
        if theme_name == "nextra":
            for n_item in options.get("nav_links", []):
                if n_item.get("slot") == "docs" and n_item.get("url") in ("/docs/", "/docs"):
                    n_item["url"] = "/quick-start"
            for lang_code, n_list in options.get("nav_links_i18n", {}).items():
                for n_item in n_list:
                    if n_item.get("slot") == "docs" and n_item.get("url") in (f"/{lang_code}/docs/", f"/{lang_code}/docs", "/docs/", "/docs"):
                        n_item["url"] = "/quick-start"

        target_dirs = []
        cur_imprint_id = getattr(adapter.engine, 'imprint_id', None) or getattr(getattr(adapter.engine, 'config', None), 'active_imprint', None)
        if not cur_imprint_id:
            try:
                from core.governance.imprint_manager import im
                cur_imprint_id = im.get_active_imprint()
            except Exception:
                cur_imprint_id = "default"
        if cur_imprint_id:
            imp_dir = os.path.join("imprints", cur_imprint_id, "themes", theme_name)
            if os.path.exists(imp_dir) and imp_dir not in target_dirs:
                target_dirs.append(imp_dir)

        if not target_dirs:
            target_dirs.append(theme_dir)

        # 🚀 [V88.8] 原厂样式防卫拦截网：在未显式勾选自定义开关时，完全不编译输出任何 CSS 视觉变量
        if not options.get('enable_custom_style', False):
            for t_dir in target_dirs:
                t_style_path = os.path.join(t_dir, "static", "assets", "theme.options.css")
                try:
                    if os.path.exists(t_style_path):
                        os.remove(t_style_path)
                except Exception:
                    pass

                # 保留导出基础 JS/JSON 桥接文件，确保 i18n, site_name, nav 等工程参数安全生效
                json_path = os.path.join(t_dir, "theme.options.json")
                js_path = os.path.join(t_dir, "theme.options.js")
                try:
                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump(options, f, indent=2, ensure_ascii=False, default=str)
                    js_content = "/**\n * 🚀 [V88.0 Live Hot-Reload] 自动生成的主题选项常量，请勿手动编辑\n */\n"
                    js_content += f"export const themeOptions = {json.dumps(options, indent=2, ensure_ascii=False, default=str)};\n"
                    js_content += "export default themeOptions;\n"
                    with open(js_path, 'w', encoding='utf-8') as f:
                        f.write(js_content)
                except Exception:
                    pass

                # 📑 [Nextra 侧边栏元数据全景水合]
                if theme_name == "nextra":
                    try:
                        from .nextra_meta_synthesizer import NextraMetaSynthesizer
                        NextraMetaSynthesizer.synthesize(t_dir, adapter.engine)
                    except Exception:
                        pass

                if theme_name == "docusaurus":
                    SSGThemeCompiler._heal_and_synthesize_docusaurus(t_dir, options)

            return True

        css_vars = [f"  --{k.replace('_', '-')}: {v};" for k, v in options.items() if isinstance(v, (str, int, float)) and not str(v).startswith("http")]
        if options.get("accent_color"):
            ac = options["accent_color"]
            css_vars.extend([f"  --ifm-color-primary: {ac} !important;", f"  --ifm-color-primary-dark: {ac} !important;", f"  --ifm-color-primary-light: {ac} !important;", f"  --theme-color: {ac} !important;"])
        css_content = "/* 🚀 [V74.96 Live Hot-Reload] 自动生成的主题运行时变量对齐，请勿手动编辑 */\n:root, [data-theme='dark'], [data-theme='light'], html {\n" + "\n".join(css_vars) + "\n}\n"



        for t_dir in target_dirs:
            t_assets = os.path.join(t_dir, "static", "assets")
            os.makedirs(t_assets, exist_ok=True)
            t_style_path = os.path.join(t_assets, "theme.options.css")
            try:
                with open(t_style_path, 'w', encoding='utf-8') as f:
                    f.write(css_content)
            except Exception:
                pass

            json_path = os.path.join(t_dir, "theme.options.json")
            try:
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(options, f, indent=2, ensure_ascii=False, default=str)
            except Exception:
                pass

            js_path = os.path.join(t_dir, "theme.options.js")
            try:
                js_content = "/**\n * 🚀 [V88.0 Live Hot-Reload] 自动生成的主题选项常量，请勿手动编辑\n */\n"
                js_content += f"export const themeOptions = {json.dumps(options, indent=2, ensure_ascii=False, default=str)};\nexport default themeOptions;\n"
                with open(js_path, 'w', encoding='utf-8') as f:
                    f.write(js_content)
            except Exception:
                pass

            if theme_name == "nextra":
                try:
                    from .nextra_meta_synthesizer import NextraMetaSynthesizer
                    NextraMetaSynthesizer.synthesize(t_dir, adapter.engine)
                except Exception:
                    pass

            if theme_name == "docusaurus":
                SSGThemeCompiler._heal_and_synthesize_docusaurus(t_dir, options)
        return True

    @staticmethod
    def _heal_and_synthesize_docusaurus(t_dir: str, options: dict):
        """自愈 Docusaurus 嵌套目录并全自动水合多语言导航字典"""
        SSGThemeCompiler._heal_docusaurus_nested_dirs(t_dir)
        try:
            from .docusaurus_i18n_synthesizer import DocusaurusI18nSynthesizer
            DocusaurusI18nSynthesizer.synthesize(t_dir, options)
        except Exception:
            pass

    @staticmethod
    def _heal_docusaurus_nested_dirs(t_dir: str):
        """自愈 Docusaurus 同名嵌套目录 (如 docs/engineering/engineering/)"""
        candidates, i18n_root = [os.path.join(t_dir, "docs")], os.path.join(t_dir, "i18n")
        if os.path.exists(i18n_root):
            for loc in os.listdir(i18n_root):
                p = os.path.join(i18n_root, loc, "docusaurus-plugin-content-docs", "current")
                if os.path.exists(p): candidates.append(p)
        import shutil
        for base in candidates:
            if not os.path.exists(base): continue
            for item in os.listdir(base):
                sub_path = os.path.join(base, item)
                if os.path.isdir(sub_path):
                    nested = os.path.join(sub_path, item)
                    if os.path.exists(nested) and os.path.isdir(nested):
                        try:
                            shutil.rmtree(nested, ignore_errors=True)
                        except Exception:
                            pass
