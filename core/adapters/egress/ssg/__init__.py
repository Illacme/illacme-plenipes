#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Egress Adapter (SSG 渲染矩阵)
模块职责：SSG 渲染插件的工厂与调度中心。
🚀 [V33 终极纯净版]：实现 Zero-Touch SSG 自发现。
"""

import logging
from .registry import SSGRegistry
from .base import BaseSSGAdapter
from core.utils.plugin_loader import discover_and_register

logger = logging.getLogger("Illacme.plenipes")

# 🚀 [Zero-Touch] 自动扫描并注册当前包下的所有 SSG 适配器插件
discover_and_register(__path__, __name__, BaseSSGAdapter, SSGRegistry.register)

class SSGAdapter:
    """🚀 SSG 渲染工厂：基于注册表动态发现渲染主权"""
    
    def __init__(self, theme_settings, custom_adapters=None):
        self.theme = theme_settings
        self.custom_adapters = custom_adapters or {}
        
        # 确定当前渲染插件名称
        theme_name = getattr(theme_settings, 'name', 'generic').lower()
        
        # 从注册表获取具体实现
        renderer_cls = SSGRegistry.get_renderer(theme_name)
        if renderer_cls:
            self.active_renderer = renderer_cls(theme_settings)
        else:
            from .generic import GenericSSGAdapter
            self.active_renderer = GenericSSGAdapter(theme_settings)
        
        logger.debug(f"🎨 [SSG 引擎] 已激活渲染插件: {self.active_renderer.__class__.__name__}")

    def render_single_callout(self, g_type: str, title: str, body: str) -> str:
        return self.active_renderer.render_callout(g_type, title, body)

    def adapt_metadata(self, fm_dict, date_obj, author_name):
        return self.active_renderer.adapt_metadata(fm_dict, date_obj, author_name)

    def convert_shortcodes(self, content):
        if not self.theme.shortcode_mappings: return content
        mappings = self.theme.shortcode_mappings
        import re
        for pattern, replacement in mappings.items():
            try:
                content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
            except Exception as e:
                logger.warning(f"⚠️ [Egress] 短代码替换失败: {e}")
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