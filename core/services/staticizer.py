#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Services - Component Staticizer (组件静态化服务)
职责：提供跨 Dialect 的组件静态化核心算法。
🛡️ [AEL-Iter-2026.04.23.SOVEREIGNTY_P1]：逻辑从工序层剥离，进入服务化主权阶段。
"""

import re
import logging

from core.utils.tracing import tlog

class StaticizerService:
    """
    🚀 工业级组件静态化处理器
    负责将 Markdown 中的动态方言（Tabs, Callouts, Dataview）转换为 SSG 兼容的静态语义。
    """

    def __init__(self):
        # 预编译正则以提升性能
        self.callout_header_re = re.compile(r'^[ \t]*>[ \t]*\[!([a-zA-Z]+)\][ \t]*(.*)')
        self.callout_line_re = re.compile(r'^[ \t]*>.*')
        self.dataview_re = re.compile(r'```dataview\s*\n(.*?)\n```', re.DOTALL | re.IGNORECASE)

    def staticize_tabs(self, text: str) -> str:
        """
        🚀 [HPSS] 高阶线性静态化算法 (Tabs)
        采用单次扫描 + 偏移量自动对齐机制，彻底消除多重排序开销。
        """
        if not text:
            return ""

        lines = text.split('\n')
        stack = []

        for i, line in enumerate(lines):
            clean_line = line.strip()
            if clean_line.startswith('```tabs'):
                stack.append(i)
                lines[i] = ':::tabs'
            elif clean_line == '```' and stack:
                stack.pop()
                lines[i] = ':::'

        return '\n'.join(lines)

    def staticize_callouts(self, text: str, ssg_adapter) -> str:
        """
        🚀 [Stack-Based] 递归栈 Callout 解析内核
        利用递归扫描模拟缩进栈，完美解决 Markdown 引文嵌套深度识别问题。
        """
        if not text:
            return ""

        lines = text.split('\n')
        processed_lines = []
        i = 0
        while i < len(lines):
            line = lines[i]
            match = self.callout_header_re.match(line)
            if match:
                ctype = match.group(1)
                title = match.group(2)
                body_lines = []
                i += 1
                # 贪婪吸收后续引用行
                while i < len(lines) and self.callout_line_re.match(lines[i]):
                    # 剥离一层引用标记
                    body_line = re.sub(r'^[ \t]*>[ \t]?', '', lines[i])
                    body_lines.append(body_line)
                    i += 1

                # 递归处理嵌套主体
                inner_body = self.staticize_callouts('\n'.join(body_lines), ssg_adapter)

                # 声明式渲染
                rendered = ssg_adapter.render_single_callout(ctype, title, inner_body)
                processed_lines.append(rendered)
            else:
                processed_lines.append(line)
                i += 1
        return '\n'.join(processed_lines)

    def staticize_dataview(self, text: str) -> str:
        """
        针对 Dataview 代码块进行透明化占位处理。
        """
        if not text:
            return ""

        def dataview_repl(match):
            return "\n> [!info] 提示\n> 此处是 Obsidian 动态查询内容（Dataview），静态发布版暂仅保留结构占位。\n"

        return self.dataview_re.sub(dataview_repl, text)
