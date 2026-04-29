#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Semantic Block Parser
模块职责：负责 Markdown 正文的语义化切片与状态机维护。
🚀 [Stage V16]：插件驱动型 Markdown 语义切片引擎。
"""

import re
from core.markup.base import MarkupBlock
from core.markup.registry import markup_registry

class MarkdownBlockParser:
    """🚀 [V16.0] 插件驱动型 Markdown 语义切片引擎"""

    def __init__(self):
        # 🛡️ 此时不再维护硬编码的 patterns 列表
        pass

    def _find_matching_plugin(self, line):
        """寻找能处理当前行起始的插件"""
        for plugin in markup_registry.get_blocks():
            if re.match(plugin.get_start_pattern(), line):
                return plugin
        return None

    def parse(self, text):
        """将文本解析为 Block 序列 (插件化版本)"""
        if not text.strip(): return []

        lines = text.splitlines()
        blocks = []
        current_block_lines = []
        state = "paragraph"
        active_plugin = None

        i = 0
        while i < len(lines):
            line = lines[i]

            # 1. 如果当前处于某个特殊块中，询问该插件是否结束
            if active_plugin:
                is_end_line = active_plugin.is_end(line, {"state": state})
                should_include = getattr(active_plugin, 'include_end_line', False)
                
                if is_end_line:
                    if should_include:
                        current_block_lines.append(line)
                        i += 1 # 包含结束行，指针步进
                    
                    blocks.append(MarkupBlock("\n".join(current_block_lines), active_plugin.block_type))
                    current_block_lines = []
                    active_plugin = None
                    state = "paragraph"
                    # 指针不步进（如果是 exclude 情况），下一轮循环将该行作为 paragraph 或新块起始处理
                    continue
                else:
                    current_block_lines.append(line)
                    i += 1
                    continue

            # 2. 探测新块的起始 (询问所有已注册插件)
            plugin = self._find_matching_plugin(line)
            if plugin:
                if current_block_lines:
                    blocks.append(MarkupBlock("\n".join(current_block_lines), state))
                    current_block_lines = []
                
                active_plugin = plugin
                current_block_lines.append(line)
                
                # 特殊处理：如果是单行块（起始即结束），立即切分
                if plugin.is_end(line, {"state": "start"}):
                    blocks.append(MarkupBlock("\n".join(current_block_lines), plugin.block_type))
                    current_block_lines = []
                    active_plugin = None
                
                i += 1
                continue

            # 3. 普通段落处理
            if not line.strip():
                if current_block_lines:
                    blocks.append(MarkupBlock("\n".join(current_block_lines), "paragraph"))
                    current_block_lines = []
                blocks.append(MarkupBlock("", "spacer"))
            else:
                current_block_lines.append(line)
            i += 1

        # 扫尾
        if current_block_lines:
            blocks.append(MarkupBlock("\n".join(current_block_lines), state))

        return blocks

    def rebuild(self, blocks):
        """将 Block 序列重新组合为完整文本"""
        return "\n".join([b.content for b in blocks])
