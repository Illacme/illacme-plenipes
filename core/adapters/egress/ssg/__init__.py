#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Egress Adapter (SSG 渲染矩阵)
模块职责：SSG 渲染插件的工厂与调度中心。
🚀 [V33 终极纯净版]：实现 Zero-Touch SSG 自发现。
"""

import logging
import sys
from .registry import SSGRegistry
from .base import BaseSSGAdapter
from core.utils.plugin_loader import discover_and_register

from core.utils.tracing import tlog

# 🚀 [Zero-Touch] 自动扫描并注册当前包下的所有 SSG 适配器插件
discover_and_register(__path__, __name__, BaseSSGAdapter, SSGRegistry.register)

class SSGAdapter:
    PLUGIN_ID = "generic"
    """🚀 SSG 渲染工厂：基于注册表动态发现渲染主权"""

    def __init__(self, theme_settings, custom_adapters=None):
        self.theme = theme_settings
        self.custom_adapters = custom_adapters or {}

        # 🚀 [V33.1] 双轨动态插件扫描矩阵 (实现主权解耦)
        import os
        theme_name = getattr(theme_settings, 'name', 'generic').lower()

        # 路径 A：全局 SSG 平台插件库
        global_adapter_path = os.path.abspath("adapters/ssg")
        if os.path.exists(global_adapter_path):
            try:
                if os.path.abspath("adapters") not in sys.path:
                    sys.path.append(os.path.abspath("adapters"))
                discover_and_register([global_adapter_path], "adapters.ssg", BaseSSGAdapter, SSGRegistry.register)
            except Exception as e:
                tlog.warning(f"⚠️ [SSG 引擎] 加载全局适配器失败: {e}")

        # 路径 B：主题私有适配器库
        theme_adapter_path = os.path.abspath(f"themes/{theme_name}/adapters")
        if os.path.exists(theme_adapter_path):
            try:
                theme_root = os.path.abspath("themes")
                if theme_root not in sys.path:
                    sys.path.append(theme_root)
                pkg_name = f"{theme_name}.adapters"
                discover_and_register([theme_adapter_path], pkg_name, BaseSSGAdapter, SSGRegistry.register)
            except Exception as e:
                tlog.warning(f"⚠️ [SSG 引擎] 加载主题适配器失败: {e}")

        # 确定当前渲染插件名称
        # 从注册表获取具体实现 (注册表现在汇总了全局 + 主题的所有适配器)
        renderer_cls = SSGRegistry.get_renderer(theme_name)
        if renderer_cls:
            self.active_renderer = renderer_cls(theme_settings)
        else:
            from .generic import GenericSSGAdapter
            self.active_renderer = GenericSSGAdapter(theme_settings)

        tlog.debug(f"🎨 [SSG 引擎] 已激活渲染插件: {self.active_renderer.__class__.__name__}")

    @property
    def output_extension(self):
        """🚀 [Standardization] 暴露底层渲染器的输出扩展名 (兼容旧版)"""
        return getattr(self.active_renderer, 'output_extension', None)

    @property
    def output_extensions(self):
        """🚀 [V11.2] 暴露底层渲染器的双相输出扩展名矩阵"""
        # 默认使用 Base 类的定义，source 为 None 表示保留原后缀
        return getattr(self.active_renderer, 'output_extensions', {"source": None, "static": ".html"})

    def get_output_schema(self):
        """🚀 [V11.2] 获取该适配器支持的输出出口列表"""
        return self.active_renderer.get_output_schema()

    def supports_frontmatter(self, ext: str) -> bool:
        """🚀 [V15.6] 判定特定扩展名是否支持元数据头"""
        return self.active_renderer.supports_frontmatter(ext)

    def render(self, body: str, fm: dict, seo_data: dict = None, target_lang: str = "en", sub_path: str = ""):
        """🚀 [V10.3] 委托底层渲染器执行深度渲染任务"""
        return self.active_renderer.render(body, fm, seo_data=seo_data, target_lang=target_lang, sub_path=sub_path)

    def render_single_callout(self, g_type: str, title: str, body: str) -> str:
        return self.active_renderer.render_callout(g_type, title, body)

    def adapt_metadata(self, fm_dict, date_obj, author_name):
        return self.active_renderer.adapt_metadata(fm_dict, date_obj, author_name)

    def inject_seo(self, fm: dict, description: str, keywords: list) -> dict:
        return self.active_renderer.inject_seo(fm, description, keywords)

    def convert_shortcodes(self, content):
        if not self.theme.shortcode_mappings: return content
        mappings = self.theme.shortcode_mappings
        import re
        for pattern, replacement in mappings.items():
            try:
                content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
            except Exception as e:
                tlog.warning(f"⚠️ [Egress] 短代码替换失败: {e}")
        return content

    def adapt_mdx_imports(self, content):
        """🚀 扁平化重构：解决嵌套过深问题"""
        if not self.theme.component_mappings:
            return content

        for component, template in self.theme.component_mappings.items():
            content = self._process_component(content, component, template)
        return content

    def _process_component(self, content, component, template):
        import re
        pattern = re.compile(rf'<{component}(?:\s*|(?:\s+[^>]*))>(((?!<{component}).)*?)</{component}>', re.DOTALL)
        content = pattern.sub(lambda m: self._mdx_repl(m, template), content)

        single_pattern = re.compile(rf'<{component}(?:\s+([^/>]*))?/?>', re.MULTILINE)
        return single_pattern.sub(lambda m: self._mdx_repl(m, template), content)

    def get_language_code(self, logic_code: str) -> str:
        """[Sovereignty] 委托到底层渲染器执行语种对齐"""
        return self.active_renderer.get_language_code(logic_code)

    def get_i18n_path_template(self, source_type: str = "docs") -> str:
        """[Sovereignty] 委托到底层渲染器获取路径模版"""
        return self.active_renderer.get_i18n_path_template(source_type)

    def _mdx_repl(self, m, template):
        import re
        attrs_raw = m.group(1) if m.lastindex >= 1 else ""
        try:
            inner_content = m.group(2).strip() if m.lastindex >= 2 else ""
        except:
            inner_content = ""

        attrs = dict(re.findall(r'(\w+)\s*=\s*["\'“”]([^"\'“”]+)["\'“”]', attrs_raw))
        res = template.replace("{children}", inner_content) if "{children}" in template else template

        for key, val in attrs.items():
            res = res.replace(f'{{{key}}}', val)

        return res
