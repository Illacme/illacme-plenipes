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

    def resolve_link(self, target_logic_id, current_lang, route_prefix, mapped_sub_dir, source_rel_path=None):
        """
        [Sovereignty] 核心解析逻辑：
        1. 尝试对 target_logic_id 进行归一化和模糊寻址定位。
        2. 在当前语种账本中寻找目标 Slug。
        3. 如果找不到，尝试回退到默认语种。
        4. 基于当前 SSG 主题模版构造最终 URL。
        """
        # 🚀 [V100.7] 动态映射解析精度提升逻辑：
        resolved_logic_id = target_logic_id

        # 提取锚点信息
        anchor = None
        if '#' in target_logic_id:
            parts_hash = target_logic_id.split('#', 1)
            target_logic_id = parts_hash[0]
            anchor = parts_hash[1]

        # 1. 尝试处理相对路径（如 ../Index/index.md）
        if source_rel_path and not target_logic_id.startswith(('/', 'http://', 'https://')):
            try:
                combined = os.path.join(os.path.dirname(source_rel_path), target_logic_id)
                normalized = os.path.normpath(combined).replace('\\', '/')
                if normalized.startswith('./'):
                    normalized = normalized[2:]
                
                # 如果规整化后的相对路径在数据库中存在，则锁定它
                if self.meta.get_doc_info(normalized):
                    resolved_logic_id = normalized
            except Exception:
                pass

        # 2. 如果依然未命中，利用 ledger 的模糊 Wikilink 解析引擎尝试定位
        if not self.meta.get_doc_info(resolved_logic_id):
            clean_target = resolved_logic_id.split('^')[0].strip()
            base_target = os.path.splitext(clean_target)[0]
            
            # 尝试通过 resolve_link 寻址（支持标题、Slug、文件名等匹配）
            found_rel_path = self.meta.resolve_link(clean_target) or self.meta.resolve_link(base_target)
            if found_rel_path:
                resolved_logic_id = found_rel_path

        # 3. 寻找目标文档在账本中的元数据
        doc_info = self.meta.get_doc_info(resolved_logic_id)

        if not doc_info:
            # 💡 可能是外部链接或尚未索引的文档，保持原样
            return None

        slug = doc_info.get('slug', '')
        if not slug:
            # 兜底：使用文件名作为 Slug
            slug = os.path.splitext(os.path.basename(resolved_logic_id))[0]

        # 4. 构造逻辑 URL (穿透 RouteManager)
        # 这里会自动处理主题感知的语种路径前缀
        final_url = self.router.resolve_logical_url(
            current_lang,
            route_prefix,
            mapped_sub_dir,
            slug
        )

        # 5. 还原锚点信息
        if anchor:
            final_url = f"{final_url}#{anchor}"

        return final_url

    def heal_content(self, content, current_lang, route_prefix, mapped_sub_dir, source_rel_path=None):
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
            resolved = self.resolve_link(target, current_lang, route_prefix, mapped_sub_dir, source_rel_path)

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
            resolved = self.resolve_link(target, current_lang, route_prefix, mapped_sub_dir, source_rel_path)
            if resolved:
                return f"[{alias}]({resolved})"
            return match.group(0)

        content = wiki_pattern.sub(wiki_repl, content)

        return content
