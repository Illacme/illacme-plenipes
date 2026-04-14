#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Egress Adapter (输出端渲染工厂)
模块职责：前端声明式渲染工厂 (SSG Adapter)。
负责在最终写盘前，将标准化的 Markdown (如 Callout 和引用块)，
套入 config.yaml 中定义的框架模板 (如 Astro 的 ::: 语法或 Hugo 的 {{< >}} 语法)。
架构原则：纯粹的翻译官，彻底解除 Python 代码与前端框架的硬编码绑定。
"""

import re
import logging

logger = logging.getLogger("Illacme.plenipes")

class SSGAdapter:
    """
    策略模式：根据目标前端框架（Astro/VitePress/Docusaurus等），动态执行语法重构。
    
    核心职责：
    1. 大小写降维防御：统一代码块语言标识为小写，解决 Linux 环境下前端高亮引擎的匹配失效。
    2. Callout 转换：将 Obsidian 专有语法映射为各主流 SSG 框架支持的标准 Container 语法。
    """
    
    # 🚀 将正则和语义映射表提升为类级常量，彻底消灭运行时高频正则编译的 CPU 开销
    # 匹配规则：精确捕获 Callout 类型标识、自定义标题及后续连续的引用行块
    _CALLOUT_PATTERN = re.compile(r'^>[ \t]*\[!([a-zA-Z]+)\](.*?)\n((?:^[ \t]*>.*\n?)*)', re.MULTILINE)
    
    # 防御阵列：精准识别代码块起始位，用于强制执行大小写扁平化处理
    _CODE_BLOCK_PATTERN = re.compile(r'^([`~]{3,})([a-zA-Z0-9_+-]+)[ \t]*$', re.MULTILINE)
    
    # 通用语义映射表：将 Obsidian 极其细分的 Callout 类型映射为 SSG 核心标准类型
    _GENERIC_MAP = {
        'info': 'info', 'abstract': 'info', 'note': 'info', 'question': 'info',
        'warning': 'warning', 'attention': 'warning',
        'error': 'danger', 'bug': 'danger', 'danger': 'danger',
        'success': 'success', 'check': 'success', 'tip': 'tip'
    }

    def __init__(self, syntax_engine, custom_adapters=None):
        """
        初始化适配器。
        :param syntax_engine: 目标前端语法方言引擎（如 starlight, vitepress 等或自定义名称）。
        :param custom_adapters: 从 config.yaml 穿透注入的声明式适配器字典。
        """
        self.syntax_engine = syntax_engine.lower().strip()
        self.custom_adapters = custom_adapters or {}
        
        # [架构破壁] 预判当前前端引擎是否命中了配置文件中的声明式渲染策略
        self.is_declarative = self.syntax_engine in self.custom_adapters
        self.declarative_config = self.custom_adapters.get(self.syntax_engine, {})
        
        # 预加载目标框架映射表，实现单点构建中的 O(1) 级转换效率（保留作为系统内建兜底方案）
        self._engine_map = {}
        if self.syntax_engine == 'starlight':
            self._engine_map = {'info': 'note', 'warning': 'caution', 'danger': 'danger', 'success': 'tip', 'tip': 'tip'}
        elif self.syntax_engine in ['vitepress', 'docusaurus']:
            self._engine_map = {'info': 'info', 'warning': 'warning', 'danger': 'danger', 'success': 'success', 'tip': 'tip'}

    def convert_callouts(self, text):
        """
        执行语法全量转换与防御性预处理。
        """
        # 架构级防御：先抹平代码块的大写问题，彻底消灭前端渲染引擎常见的 Language Not Found 警告
        text = self._CODE_BLOCK_PATTERN.sub(lambda m: f"{m.group(1)}{m.group(2).lower()}", text)

        def repl(m):
            ctype = m.group(1).lower()
            title = m.group(2).strip()
            body = m.group(3)
            
            # 清理引用行中的每一行前导 '>' 标记，提取出纯净的 Callout 内容主体
            body = re.sub(r'^[ \t]*>[ \t]?', '', body, flags=re.MULTILINE).strip()
            g_type = self._GENERIC_MAP.get(ctype, 'info')

            # 优先级 1：声明式渲染引擎分发
            if self.is_declarative:
                tpl = self.declarative_config.get('callout_template', "\n> **{title}**\n> {body_quoted}\n\n")
                type_map = self.declarative_config.get('type_mapping', {})
                mapped_type = type_map.get(g_type, g_type)
                body_quoted = '\n> '.join(body.split('\n'))
                
                try:
                    return tpl.format(type=mapped_type, title=title, body=body, body_quoted=body_quoted)
                except KeyError as e:
                    logger.error(f"🛑 声明式渲染引擎模板存在语法错误，无法解析占位符 {e}。请检查 config.yaml。")
                    return f"\n> **{title}**\n> {body_quoted}\n\n"

            # 优先级 2：内建硬编码的系统级兜底策略（向下兼容历史版本）
            if self.syntax_engine == 'starlight':
                return f"\n:::{self._engine_map.get(g_type, 'note')} {title}\n{body}\n:::\n\n"
            elif self.syntax_engine in ['vitepress', 'docusaurus']:
                return f"\n:::{self._engine_map.get(g_type, 'info')} {title}\n{body}\n:::\n\n"
            elif self.syntax_engine == 'hugo':
                return f"\n{{{{< admonition type=\"{g_type}\" title=\"{title}\" >}}}}\n{body}\n{{{{< /admonition >}}}}\n\n"
            elif self.syntax_engine == 'hexo':
                return f"\n{{% note {g_type} %}}\n**{title}**\n{body}\n{{% endnote %}}\n\n"
            else:
                # 终极兜底方案：自动降级为 Markdown 标准加粗引用格式
                body_quoted = '\n> '.join(body.split('\n'))
                return f"\n> **{title}**\n> {body_quoted}\n\n"
                
        return self._CALLOUT_PATTERN.sub(repl, text)