#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - SSG Rendering Base (Central Hub)
模块职责：定义 SSG 输出端渲染器的抽象基类协议与全局导航/主题参数分发门面。
🛡️ [SOP-02 模块拆分 / AEL-Iter-v10.3 基因克隆]
"""
import abc
import os
import json
from typing import Tuple, Dict, Any, List

from .mixins import CITemplateMixin
from .base_shards.ssg_nav_synthesizer import SSGNavSynthesizer, SLOT_I18N_FALLBACK
from .base_shards.ssg_theme_compiler import SSGThemeCompiler

__all__ = ["BaseSSGAdapter", "SLOT_I18N_FALLBACK"]


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
        self.theme_schema = {}
        if self.theme_settings:
            theme_name = getattr(self.theme_settings, 'name', 'sovereign')
            if theme_name == 'default':
                theme_name = 'sovereign'
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
        if hasattr(self, 'engine') and self.engine and hasattr(self.engine, 'config'):
            cfg = self.engine.config

            # 自愈逻辑：site_name Fallback 为 imprint_name/press_name; site_description Fallback 为 imprint_description
            g_site_name = getattr(cfg, "site_name", None) or getattr(cfg, "imprint_name", None)
            g_site_desc = getattr(cfg, "site_description", None) or getattr(cfg, "imprint_description", None)

            # 版权声明与出版合规自愈逻辑：合并单数据源，提取合规元数据
            fm_defaults = getattr(cfg, "frontmatter_defaults", {}) or {}
            g_copyright = fm_defaults.get("copyright", None)
            g_license = fm_defaults.get("license", None)
            g_author = fm_defaults.get("author", None)
            g_icp = fm_defaults.get("icp_license") or getattr(cfg, "icp_license", None)
            g_police = fm_defaults.get("police_license") or getattr(cfg, "police_license", None)

            global_promotions = {
                "site_name": g_site_name,
                "site_description": g_site_desc,
                "favicon_path": getattr(cfg, "favicon_path", None),
                "logo_path": getattr(cfg, "logo_path", None),
                "footer_copyright": g_copyright,
                "license": g_license,
                "author": g_author,
                "icp_license": g_icp,
                "police_license": g_police
            }

            for g_key, g_val in global_promotions.items():
                if g_val is not None and str(g_val).strip() != "":
                    options[g_key] = g_val

        if self.theme_settings and hasattr(self.theme_settings, 'options') and self.theme_settings.options:
            for key, val in self.theme_settings.options.items():
                if val is not None and str(val).strip() != "":
                    options[key] = val

        # 🧭 [Universal Navigation Injection] 将 route_matrix 动态合成的导航项注入 options
        try:
            nav_synthesis = self.generate_navigation_items()
            if nav_synthesis and isinstance(nav_synthesis, dict):
                if nav_synthesis.get('nav_links'):
                    options['nav_links'] = nav_synthesis['nav_links']
                if nav_synthesis.get('nav_links_i18n'):
                    options['nav_links_i18n'] = nav_synthesis['nav_links_i18n']
        except Exception:
            pass

        return options


    @abc.abstractmethod
    def render(self, body: str, fm: Dict[str, Any], seo_data: Dict[str, Any] = None, target_lang: str = "en", sub_path: str = "") -> Tuple[str, Dict[str, Any]]:
        """[Contract] 执行特定 SSG 的语法转换与元数据增强。"""
        pass

    def supports_frontmatter(self, ext: str) -> bool:
        """🚀 [V15.6] 判定特定扩展名是否支持元数据头"""
        if not ext:
            return False
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

    def normalize_markdown_content(self, body: str, sub_path: str = "", target_lang: str = "zh", clean_url: bool = None) -> str:
        """
        🚀 [Universal Link Healing & Parity] 通用 Markdown/MDX 链接清洗与语法规范化：
        1. 将 Obsidian 双链 [[target|alias]]、[[target]] 标准化为符合通用 Markdown 规范的相对链接 [alias](./target.md)。
        2. 自愈相对超链接中的 .html 后缀为 .md (契合第三方 SSG 框架内部 SPA 路由器要求) 或 Clean URL。
        3. 确保第三方框架（Docusaurus/VitePress/Starlight/Nextra/Hugo/Hexo）MDX 编译器 0 语法报错。
        """
        import re
        if clean_url is None:
            clean_url = getattr(self, 'IS_CLEAN_URL', False)

        try:
            from core.adapters.egress.ssg.generic_shards.navigation_builder import get_doc_slug_map
            slug_map = get_doc_slug_map(self.engine) if self.engine else {}
        except Exception:
            slug_map = {}

        raw_current_dir = os.path.dirname(sub_path.replace('\\', '/')).strip('/')
        lang_code = self.get_language_code(target_lang) if hasattr(self, 'get_language_code') else ""
        lang_prefix = f"/{lang_code}" if lang_code else ""

        # 🛡️ 剥离当前目录中的物理语言前缀 (如 ja/docs -> docs, ja -> "")，杜绝 /ja/ja/ 双重语种叠加
        current_dir_parts = [p for p in raw_current_dir.split('/') if p]
        if current_dir_parts and lang_code and current_dir_parts[0] == lang_code:
            current_dir_parts = current_dir_parts[1:]
        current_dir = '/'.join(current_dir_parts)

        def _resolve_target_md(target_str: str, anchor: str = "") -> str:
            raw_t = target_str.replace('\\', '/').strip()
            while raw_t.startswith('./'):
                raw_t = raw_t[2:]
            clean_t = raw_t.strip('/')
            if not clean_t:
                return f"./{anchor}" if anchor else ""
            clean_lookup = clean_t.lower().removesuffix('.md').removesuffix('.html')
            stem = os.path.splitext(os.path.basename(clean_t))[0].lower()

            matched = slug_map.get(clean_lookup)
            if not matched and stem != 'index':
                matched = slug_map.get(stem)
            elif not matched and clean_lookup == 'index':
                matched = slug_map.get('index')

            if clean_url:
                # 🛡️ Clean URL 模式下必须使用站点绝对根路径 (Root-relative URL)，
                # 彻底根绝末尾斜杠 (/) 导致的浏览器相对路径层级叠加 (如 /docs/quick-start/authoring-and-vault-guide/ 404)。
                if matched:
                    actual_slug = matched.get('slug', stem)
                    channel = matched.get('channel', '')
                    target_dir = channel if (channel and channel not in ('', 'pages')) else ""

                    if actual_slug == 'index':
                        if target_dir:
                            res_url = f"{lang_prefix}/{target_dir}/{anchor}"
                        else:
                            res_url = f"{lang_prefix}/{anchor}" if lang_prefix else f"/{anchor}"
                    else:
                        if target_dir:
                            res_url = f"{lang_prefix}/{target_dir}/{actual_slug}/{anchor}"
                        else:
                            res_url = f"{lang_prefix}/{actual_slug}/{anchor}"
                else:
                    clean_name = clean_lookup
                    is_index_target = clean_name.endswith('/index') or clean_name == 'index'
                    if clean_name.endswith('/index'):
                        clean_name = clean_name.removesuffix('/index')

                    # 🛡️ 剥离 clean_name 中可能已存在的语言前缀
                    clean_parts = [p for p in clean_name.split('/') if p]
                    if clean_parts and lang_code and clean_parts[0] == lang_code:
                        clean_parts = clean_parts[1:]
                        clean_name = '/'.join(clean_parts)

                    if clean_name.startswith('../'):
                        resolved_parts = [p for p in (current_dir.split('/') if current_dir else []) if p]
                        sub_parts = clean_name.split('/')
                        for p in sub_parts:
                            if p == '..':
                                if resolved_parts:
                                    resolved_parts.pop()
                            elif p and p != '.':
                                resolved_parts.append(p)
                        abs_path = '/'.join(resolved_parts)
                        if abs_path:
                            res_url = f"{lang_prefix}/{abs_path}/{anchor}"
                        else:
                            res_url = f"{lang_prefix}/{anchor}" if lang_prefix else f"/{anchor}"
                    elif '/' in clean_name:
                        res_url = f"{lang_prefix}/{clean_name}/{anchor}"
                    else:
                        if current_dir and not is_index_target and clean_name != 'index':
                            res_url = f"{lang_prefix}/{current_dir}/{clean_name}/{anchor}"
                        elif clean_name and clean_name != 'index':
                            res_url = f"{lang_prefix}/{clean_name}/{anchor}"
                        else:
                            res_url = f"{lang_prefix}/{anchor}" if lang_prefix else f"/{anchor}"

                # 🛡️ 终极防重守卫：确保永远不会出现双重语种前缀 (如 /ja/ja/ 或 /en/en/)
                if lang_code and clean_url:
                    double_pfx = f"/{lang_code}/{lang_code}/"
                    single_pfx = f"/{lang_code}/"
                    while double_pfx in res_url:
                        res_url = res_url.replace(double_pfx, single_pfx)
                return res_url
            else:
                # 传统 .md / .html 相对路径模式
                suffix = ".md"
                if matched:
                    actual_slug = matched.get('slug', stem)
                    channel = matched.get('channel', '')
                    target_dir = channel if (channel and channel not in ('', 'pages')) else ""

                    if current_dir == target_dir:
                        return f"./{actual_slug}{suffix}{anchor}"
                    elif not current_dir and target_dir:
                        return f"./{target_dir}/{actual_slug}{suffix}{anchor}"
                    elif current_dir and not target_dir:
                        return f"../{actual_slug}{suffix}{anchor}"
                    else:
                        return f"../{target_dir}/{actual_slug}{suffix}{anchor}"
                else:
                    return f"./{clean_lookup}{suffix}{anchor}"

        # 1. 转换 Obsidian 双链 [[target|alias]] 或 [[target]]
        def _wikilink_repl(match):
            target = match.group(1).strip()
            alias = (match.group(2) or target).strip()
            if target.startswith(('AEL-Iter-ID:', 'AEL:')) or 'Iter-ID' in target:
                return match.group(0)
            clean_target = target.replace('\\', '/').strip('/')
            if not clean_target:
                return alias
            anchor = ""
            if '#' in clean_target:
                parts = clean_target.split('#', 1)
                clean_target = parts[0]
                anchor = f"#{parts[1]}"
            if clean_target.startswith(('http://', 'https://', 'mailto:', '/')):
                return f"[{alias}]({clean_target}{anchor})"
            
            resolved_md = _resolve_target_md(clean_target, anchor)
            return f"[{alias}]({resolved_md})"

        wiki_pattern = re.compile(r'(?<!\!)\[\[([^\]|]+)(?:\|([^\]]+))?\]\]')
        processed = wiki_pattern.sub(_wikilink_repl, body)

        # 2. 规范化标准 Markdown 相对链接中的 .html / .md
        def _mdlink_repl(match):
            alias = match.group(1)
            target = match.group(2).strip()
            if target.startswith(('http://', 'https://', 'mailto:', '/', '#')):
                return match.group(0)
            anchor = ""
            clean_target = target
            if '#' in clean_target:
                parts = clean_target.split('#', 1)
                clean_target = parts[0]
                anchor = f"#{parts[1]}"
            if clean_url:
                resolved = _resolve_target_md(clean_target, anchor)
                if resolved:
                    return f"[{alias}]({resolved})"
                if clean_target.endswith(('.html', '.md')):
                    clean_stem = clean_target.removesuffix('.html').removesuffix('.md')
                    if clean_stem.endswith('/index'):
                        clean_stem = clean_stem.removesuffix('/index')
                    if not clean_stem.endswith('/'):
                        clean_stem += '/'
                    return f"[{alias}]({clean_stem}{anchor})"
            else:
                if clean_target.endswith('.html'):
                    clean_stem = clean_target.removesuffix('.html')
                    return f"[{alias}]({clean_stem}.md{anchor})"
            return match.group(0)

        processed = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', _mdlink_repl, processed)

        # 3. 规范化原生 HTML 中的 <a href="..."> 相对链接
        def _html_a_repl(match):
            prefix_attr = match.group(1)
            href_val = match.group(2).strip()
            suffix_attr = match.group(3)
            if href_val.startswith(('http://', 'https://', 'mailto:', '/', '#')):
                return match.group(0)
            anchor = ""
            clean_href = href_val
            if '#' in clean_href:
                parts = clean_href.split('#', 1)
                clean_href = parts[0]
                anchor = f"#{parts[1]}"
            if clean_url:
                resolved = _resolve_target_md(clean_href, anchor)
                if resolved:
                    return f'<a {prefix_attr}href="{resolved}"{suffix_attr}>'
                if clean_href.endswith(('.html', '.md')):
                    clean_stem = clean_href.removesuffix('.html').removesuffix('.md')
                    if clean_stem.endswith('/index'):
                        clean_stem = clean_stem.removesuffix('/index')
                    if not clean_stem.endswith('/'):
                        clean_stem += '/'
                    return f'<a {prefix_attr}href="{clean_stem}{anchor}"{suffix_attr}>'
            return match.group(0)

        html_a_pattern = re.compile(r'<a\s+([^>]*?)href=["\']([^"\']+)["\']([^>]*)>', re.IGNORECASE)
        processed = html_a_pattern.sub(_html_a_repl, processed)

        # 4. 🛡️ 消除 CommonMark 陷阱：将带有 4+ 空格缩进的 HTML 标签行自动顶格，
        # 防止其在空行后被 Remark/CommonMark 错误识别为缩进代码块 (<pre><code>)。
        lines = processed.split('\n')
        new_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith(('<', '</', '<!--')) or stripped.endswith('>') or ('</' in stripped):
                new_lines.append(stripped)
            elif '<' in line and '>' in line and not line.strip().startswith(('`', '-', '*', '1.', '2.', '3.')):
                new_lines.append(stripped)
            else:
                new_lines.append(line)
        processed = '\n'.join(new_lines)

        return processed

    def get_language_code(self, logic_code: str) -> str:
        """[Sovereignty] 物理路径语种对齐。"""
        from core.utils.language_hub import LanguageHub
        iso_code = LanguageHub.resolve_to_iso(logic_code)
        if not self.force_default_lang_prefix and iso_code == LanguageHub.resolve_to_iso(self.default_lang):
            return ""
        return LanguageHub.get_physical_path(iso_code, "generic")

    def get_i18n_path_template(self, source_type: str = "docs") -> str:
        """[Sovereignty] 获取当前 SSG 的多语言路径模版。"""
        return "{lang}/{sub_dir}"

    def generate_navigation_items(self) -> Dict[str, Any]:
        """
        🧭 [V100.9 Universal Navigation Synthesis]
        根据引擎配置的 route_matrix 自动合成适配各 SSG 主题的全景导航结构。
        委派至 SSGNavSynthesizer 执行。
        """
        return SSGNavSynthesizer.generate_navigation_items(self)

    def compile_theme_options(self) -> bool:
        """
        🎯 [SSG 热对齐] 将用户最新的自定义主题选项编译并输出为物理层样式，
        委派至 SSGThemeCompiler 执行。
        """
        return SSGThemeCompiler.compile_theme_options(self)

    def get_theme_root(self) -> str:
        """🚀 获取当前主题的物理根目录路径"""
        if self.engine and hasattr(self.engine, 'paths') and self.engine.paths:
            themes_root = self.engine.paths.get("themes", "themes")
        else:
            from core.config.config import THEMES_DIR
            themes_root = THEMES_DIR
        theme_name = getattr(self.theme_settings, 'name', 'generic') if self.theme_settings else 'generic'
        if theme_name in ('default', ''):
            theme_name = 'sovereign'
        return os.path.join(themes_root, theme_name)

    def has_autonomous_blog_engine(self) -> bool:
        """
        🎨 博客自治能力契约声明：
        返回 True 表示此主题具备独立的博客列表与展示流合成器（如 Sovereign / 自定义主题），
        通用生命周期插件将自动让路，绝不执行外部通用 HTML 覆盖。
        """
        if hasattr(self, 'theme_settings') and getattr(self.theme_settings, 'autonomous_blog', None) is not None:
            return bool(self.theme_settings.autonomous_blog)
        theme_root = self.get_theme_root()
        if theme_root and os.path.exists(theme_root):
            if os.path.exists(os.path.join(theme_root, "scripts", "blog_synthesizer.py")):
                return True
            if os.path.exists(os.path.join(theme_root, "hooks.py")):
                try:
                    with open(os.path.join(theme_root, "hooks.py"), 'r', encoding='utf-8') as f:
                        h_content = f.read()
                        if "BlogSynthesizer" in h_content or "blog" in h_content:
                            return True
                except Exception:
                    pass
        return False

    def is_framework_engine(self) -> bool:
        """
        🚀 外部框架 SSG 构建能力声明：
        基于物理特征（如 package.json 或配置文件）探测，实现零硬编码适配。
        """
        theme_root = self.get_theme_root()
        if not theme_root or not os.path.exists(theme_root):
            return False
        has_pkg = os.path.exists(os.path.join(theme_root, "package.json"))
        has_cfg = any(os.path.exists(os.path.join(theme_root, f)) for f in (
            "astro.config.mjs", "docusaurus.config.js", "theme.config.jsx",
            ".vitepress", "config.toml", "hugo.toml"
        ))
        return bool(has_pkg or has_cfg)
