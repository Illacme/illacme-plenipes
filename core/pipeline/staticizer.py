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

    def _staticize_tabs(self, text: str) -> str:
        """
        将 ```tabs 语法转换为通用的 :::tabs 语义（后续由 egress 派发器针对框架转换为 JSX 或 Shortcode）
        """
        def tabs_repl(match):
            content = match.group(1)
            # 简单解析：支持 tab: Title 语法
            # 这里我们先将其转换为中间态格式，等待 egress_dispatcher 根据 SSG 类型转换
            return f"\n:::tabs\n{content}\n:::\n"

        # 匹配 ```tabs ... ```
        return re.sub(r'```tabs\s*\n(.*?)\n```', tabs_repl, text, flags=re.DOTALL | re.IGNORECASE)

    def _staticize_dataview(self, text: str) -> str:
        """
        针对 Dataview 代码块，若发现有渲染结果注入，则尝试提取；否则保留占位符或物理隐藏。
        """
        def dataview_repl(match):
            # 由于后端无法执行 Dataview JS，我们将其转换为一个静态提醒或占位符
            # 这比直接让用户在网页上看到源码要专业得多
            return "\n> [!info] 提示\n> 此处是 Obsidian 动态查询内容（Dataview），静态发布版暂仅保留结构占位。\n"

        return re.sub(r'```dataview\s*\n(.*?)\n```', dataview_repl, text, flags=re.DOTALL | re.IGNORECASE)
