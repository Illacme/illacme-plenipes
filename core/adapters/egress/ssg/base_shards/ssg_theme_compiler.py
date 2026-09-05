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

                source_logic = i18n_cfg.source.lang_code or "zh"
                default_locale = adapter.get_language_code(source_logic)
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
                    pub_mode = adapter.engine.config.governance.publishing_mode if hasattr(adapter.engine.config, 'governance') else None
                    if pub_mode == PublishingMode.GLOBAL:
                        for target in i18n_cfg.targets:
                            target_logic = target.lang_code
                            target_locale = adapter.get_language_code(target_logic)
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
        nav_data = adapter.generate_navigation_items()
        options["navbar_items"] = nav_data.get("navbar_items", [])
        options["nav_links"] = nav_data.get("nav_links", [])
        options["navbar_items_i18n"] = nav_data.get("navbar_items_i18n", {})
        options["nav_links_i18n"] = nav_data.get("nav_links_i18n", {})

        # 🌐 [Nextra & VitePress 多语言矩阵与 Locales 桥接自愈]
        if theme_name in ("nextra", "vitepress") and adapter.engine and hasattr(adapter.engine, 'config') and getattr(adapter.engine.config, 'i18n_settings', None):
            from core.utils.language_hub import LanguageHub
            i18n_cfg = adapter.engine.config.i18n_settings
            def_lang = getattr(i18n_cfg.source, 'lang_code', 'zh') or 'zh'
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
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(options, f, indent=2, ensure_ascii=False, default=str)
        except Exception:
            pass

        # 🚀 [V88.0] 纯前端 JS 桥接：生成无 Node.js 模块依赖的纯前端 JS 常量文件，彻底绕过 Webpack/Vite 客户端打包时的 fs 模块丢失限制
        js_path = os.path.join(theme_dir, "theme.options.js")
        try:
            js_content = "/**\n * 🚀 [V88.0 Live Hot-Reload] 自动生成的主题选项常量，请勿手动编辑\n */\n"
            js_content += f"export const themeOptions = {json.dumps(options, indent=2, ensure_ascii=False, default=str)};\n"
            js_content += "export default themeOptions;\n"
            with open(js_path, 'w', encoding='utf-8') as f:
                f.write(js_content)
        except Exception:
            pass

        return True
