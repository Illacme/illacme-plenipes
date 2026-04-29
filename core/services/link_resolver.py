#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Semantic Link Resolver
模块职责：全域语义断链愈合器。
负责在物理分发阶段，将 Markdown 中的逻辑链接动态解析为当前 SSG 主题、当前语种下的真实物理 URL。
🚀 [Stage V9.0]：实现“逻辑唯一，物理多样”的寻址主权。
"""

import logging
import re
import os

from core.utils.tracing import tlog

class LinkResolver:
    """🚀 语义寻址大脑：彻底消灭跨框架、跨语种的 404 链接"""

    def __init__(self, meta, route_manager, active_theme):
        self.meta = meta
        self.router = route_manager
        self.theme = active_theme.lower()

    def resolve_link(self, target_logic_id, current_lang, route_prefix, mapped_sub_dir):
        """
        [Sovereignty] 核心解析逻辑：
        1. 尝试在当前语种账本中寻找目标 Slug。
        2. 如果找不到，尝试回退到默认语种。
        3. 基于当前 SSG 主题模版构造最终 URL。
        """
        # 1. 寻找目标文档在账本中的元数据
        doc_info = self.meta.get_doc_info(target_logic_id)

        if not doc_info:
            # 💡 可能是外部链接或尚未索引的文档，保持原样
            return None

        slug = doc_info.get('slug', '')
        if not slug:
            # 兜底：使用文件名作为 Slug
            slug = os.path.splitext(os.path.basename(target_logic_id))[0]

        # 2. 构造逻辑 URL (穿透 RouteManager)
        # 这里会自动处理主题感知的语种路径前缀
        final_url = self.router.resolve_logical_url(
            current_lang,
            route_prefix,
            mapped_sub_dir,
            slug
        )

        return final_url

    def heal_content(self, content, current_lang, route_prefix, mapped_sub_dir):
        """
        [Resilience] 扫描内容中的所有链接并执行语义修复
        """
        # 匹配标准 MD 链接: [Text](Target)
        # 排除 http/https/mailto 等外部链接
        def link_repl(match):
            text = match.group(1)
            target = match.group(2)

            if target.startswith(('http', 'mailto', 'tel', '#', '/')):
                return match.group(0)

            # 执行解析
            # 假设 target 是相对路径，如 "Docs/B.md"
            resolved = self.resolve_link(target, current_lang, route_prefix, mapped_sub_dir)

            if resolved:
                return f"[{text}]({resolved})"
            return match.group(0)

        # 1. 处理标准 Markdown 链接
        pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
        content = pattern.sub(link_repl, content)

        # 2. 处理 Wikilinks: [[Target|Alias]]
        wiki_pattern = re.compile(r'\[\[([^\]|]+)(?:\|([^\]]+))?\]\]')
        def wiki_repl(match):
            target = match.group(1)
            alias = match.group(2) or target
            resolved = self.resolve_link(target, current_lang, route_prefix, mapped_sub_dir)
            if resolved:
                return f"[{alias}]({resolved})"
            return match.group(0)

        content = wiki_pattern.sub(wiki_repl, content)

        return content
