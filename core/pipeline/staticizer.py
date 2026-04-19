#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Component Staticizer (组件静态化引擎)
模块职责：将 Obsidian 插件生成的动态代码块 (Tabs, Dataview) 转换为静态 SSG 组件语义。
🚀 [V31 专家版]：支持跨框架的语义对齐。
"""

import re
import logging
from .runner import Step

logger = logging.getLogger("Illacme.plenipes")

class StaticizerStep(Step):
    """
    🚀 阶段 3.5: 组件语义提取与静态化
    在文档被归一化后，将特定的方言组件转换为标准中间态。
    """
    def process(self, ctx):
        # 🛡️ 尊重全局开关：如果配置中关闭了静态化，则直接跳过
        ingress_cfg = ctx.engine.config.ingress_settings
        if not ingress_cfg.staticize_components:
            return

        if not ctx.raw_body:
            return

        # 1. Obsidian Tabs 插件静态化 (```tabs 语法)
        ctx.raw_body = self._staticize_tabs(ctx.raw_body)
        
        # 2. Dataview 透明化处理 (防止代码块直接暴露在前端)
        ctx.raw_body = self._staticize_dataview(ctx.raw_body)

# 🛡️ [AEL-2026-04-19_hpss_optimization]
    def _staticize_tabs(self, text: str) -> str:
        """
        🚀 [HPSS] 高阶线性静态化算法。
        采用单次扫描 + 偏移量自动对齐机制，彻底消除原有算法中的多重排序与反向替换开销。
        针对超大规模文档进行内存优化，确保在 AEL 全自动流程中保持极致的执行效率。
        """
        lines = text.split('\n')
        stack = []
        
        # 🛡️ [AEL-2026-04-19_hpss_optimization] 线性单次扫描就地替换
        # 核心逻辑：利用栈的 LIFO 特性，在发现结束标记时立即回溯替换，无需二次排序。
        for i, line in enumerate(lines):
            clean_line = line.strip()
            if clean_line.startswith('```tabs'):
                stack.append(i)
                lines[i] = ':::tabs'
            elif clean_line == '```' and stack:
                stack.pop()
                lines[i] = ':::'
            
        return '\n'.join(lines)

    def _staticize_dataview(self, text: str) -> str:
        """
        针对 Dataview 代码块，若发现有渲染结果注入，则尝试提取；否则保留占位符或物理隐藏。
        """
        def dataview_repl(match):
            # 由于后端无法执行 Dataview JS，我们将其转换为一个静态提醒或占位符
            # 这比直接让用户在网页上看到源码要专业得多
            return "\n> [!info] 提示\n> 此处是 Obsidian 动态查询内容（Dataview），静态发布版暂仅保留结构占位。\n"

        return re.sub(r'```dataview\s*\n(.*?)\n```', dataview_repl, text, flags=re.DOTALL | re.IGNORECASE)
