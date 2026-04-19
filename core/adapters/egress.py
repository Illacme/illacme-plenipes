#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Egress Adapter (输出端渲染工厂)
模块职责：前端声明式渲染工厂 (SSG Adapter)。
🚀 [V32.4 架构归一化]：完全由 SyntaxPreset 驱动，消除硬编码。
"""

import re
import logging
from ..config import SyntaxPreset

logger = logging.getLogger("Illacme.plenipes")

class SSGAdapter:
    # 🚀 [V32.4 预置库] 定义工业级标准语法模板
    PRESET_TEMPLATES = {
        SyntaxPreset.ADMONITIONS: "\n:::{type} {title}\n{body}\n:::\n\n",
        SyntaxPreset.CONTAINERS: "\n::: {type} {title}\n{body}\n:::\n\n",
        SyntaxPreset.LEGACY: "\n> [!{type}] {title}\n> {body_quoted}\n\n",
        SyntaxPreset.NONE: "\n> **{title}**\n> {body_quoted}\n\n"
    }

    _CALLOUT_PATTERN = re.compile(r'^[ \t]*>[ \t]*\[!([a-zA-Z]+)\][ \t]*(.*?)\n((?:^[ \t]*>.*\n?)*)', re.MULTILINE)
    _CODE_BLOCK_PATTERN = re.compile(r'^([`~]{3,})([a-zA-Z0-9_+-]+)[ \t]*$', re.MULTILINE)
    
    _GENERIC_MAP = {
        'info': 'info', 'abstract': 'info', 'note': 'info', 'question': 'info',
        'warning': 'warning', 'attention': 'warning',
        'error': 'danger', 'bug': 'danger', 'danger': 'danger',
        'success': 'success', 'check': 'success', 'tip': 'tip'
    }

    def __init__(self, theme_settings, custom_adapters=None):
        self.theme = theme_settings
        self.custom_adapters = custom_adapters or {}
        preset = self.theme.syntax_preset
        self.effective_tpl = self.theme.callout_template or self.PRESET_TEMPLATES.get(preset, self.PRESET_TEMPLATES[SyntaxPreset.NONE])
        self._engine_map = self.theme.type_mapping or {}
        
        if not self._engine_map:
            if preset == SyntaxPreset.ADMONITIONS:
                self._engine_map = {'info': 'note', 'warning': 'caution', 'danger': 'danger', 'success': 'tip', 'tip': 'tip'}
            elif preset == SyntaxPreset.CONTAINERS:
                self._engine_map = {'info': 'info', 'warning': 'warning', 'danger': 'danger', 'success': 'success', 'tip': 'tip'}

    def convert_callouts(self, content):
        def repl(m):
            g_type = m.group(1).lower()
            title = m.group(2).strip()
            raw_body = m.group(3)
            body_lines = []
            for line in raw_body.split('\n'):
                clean_line = re.sub(r'^[ \t]*>[ \t]?', '', line)
                body_lines.append(clean_line)
            body = '\n'.join(body_lines).strip()
            target_type = self._engine_map.get(g_type) or self._GENERIC_MAP.get(g_type, 'info')
            body_quoted = '\n> '.join(body.split('\n'))
            try:
                display_title = title if title else ""
                # 🚀 执行声明式渲染
                res = self.effective_tpl.format(type=target_type, title=display_title, body=body, body_quoted=body_quoted).replace('  ', ' ').strip() + "\n\n"
                # 🍎 [物理证据获取]：故意在此处 print 以便在日志中直接看到产物，绕过 f-string 限制
                return res
            except Exception as e:
                return f"\n> **{title or target_type.upper()}**\n> {body_quoted}\n\n"

        return self._CALLOUT_PATTERN.sub(repl, content)

    def convert_shortcodes(self, content):
        """
        🚀 [GGP] 通用短代码转换器
        使用正则表达式映射表，将 Obsidian 语法或其他方言直接翻译为目标 SSG 的私有语法 (如 Hugo {{< hint >}})。
        """
        if not self.theme.shortcode_mappings:
            return content
            
        mappings = self.theme.shortcode_mappings
        for pattern, replacement in mappings.items():
            try:
                # 支持捕获组的动态替换
                content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
            except Exception as e:
                logger.warning(f"⚠️ [Egress] 短代码正则替换失败 ({pattern}): {e}")
                
        return content

    def adapt_mdx_imports(self, content):
        if not self.theme.component_mappings: return content
        mappings = self.theme.component_mappings
        for component, template in mappings.items():
            def complex_repl(m):
                attrs_raw = m.group(1) or ""
                try: inner_content = m.group(2).strip()
                except: inner_content = ""
                attrs = dict(re.findall(r'(\w+)\s*=\s*["\'“”]([^"\'“”]+)["\'“”]', attrs_raw))
                res = template
                if "{children}" in res: res = res.replace("{children}", inner_content)
                for key, val in attrs.items(): res = res.replace(f'{{{key}}}', val)
                res = re.sub(r'\{([a-zA-Z_]+)\}', r'""', res)
                return res
            while f'<{component}' in content and f'</{component}>' in content:
                pattern = re.compile(rf'<{component}(?:\s*|(?:\s+[^>]*))>(((?!<{component}).)*?)</{component}>', re.DOTALL)
                new_content = pattern.sub(complex_repl, content)
                if new_content == content: break
                content = new_content
            single_pattern = re.compile(rf'<{component}(?:\s+([^/>]*))?/?>', re.MULTILINE)
            content = single_pattern.sub(complex_repl, content)
        return content

    def adapt_metadata(self, fm_dict, date_obj, author_name):
        mapping = self.theme.metadata_mapping
        new_fm = fm_dict.copy()
        mod_cfg = mapping.get('last_modified')
        if mod_cfg:
            key = mod_cfg.key or 'last_modified'
            style = mod_cfg.style or 'plain'
            
            # 🚀 [GGP] 增强：日期格式化逻辑
            final_val = date_obj
            if mod_cfg.datetime_format and hasattr(date_obj, 'strftime'):
                try:
                    final_val = date_obj.strftime(mod_cfg.datetime_format)
                except Exception as e:
                    logger.warning(f"⚠️ [Egress] 日期格式化失败: {e}")

            if style == 'object': 
                new_fm[key] = {'date': final_val, 'author': author_name}
            else: 
                new_fm[key] = final_val
        auth_cfg = mapping.get('author')
        if auth_cfg and 'author' in new_fm:
            target_key = auth_cfg.key or 'author'
            if target_key != 'author': new_fm[target_key] = new_fm.pop('author')
        kw_cfg = mapping.get('keywords')
        if kw_cfg:
            source_key = 'keywords'
            target_key = kw_cfg.key or 'tags'
            if source_key in new_fm and target_key != source_key: new_fm[target_key] = new_fm.pop(source_key)
        return new_fm