#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Semantic Block Parser
模块职责：负责 Markdown 正文的语义化切片与状态机维护。
🚀 [Stage V6]：支持复杂容器 (Callouts, Tabs, Code Blocks) 的递归解析与指纹生成。
"""

import hashlib
import re

class MarkdownBlock:
    """Markdown 语义块对象"""
    def __init__(self, content, block_type="paragraph", metadata=None):
        self.content = content
        self.type = block_type
        self.metadata = metadata or {}
        self.fingerprint = self._generate_fingerprint()

    def _generate_fingerprint(self):
        return hashlib.md5(self.content.strip().encode('utf-8')).hexdigest()

    def __repr__(self):
        return f"<Block type={self.type} hash={self.fingerprint[:8]}>"

class MarkdownBlockParser:
    """🚀 [Stage V6] 工业级 Markdown 语义切片引擎"""
    
    def __init__(self):
        # 定义容器块的起始标记
        self.container_patterns = {
            "code": re.compile(r'^(\s*)```'),
            "callout": re.compile(r'^(\s*)>\s*'),
            "custom_container": re.compile(r'^(\s*):::\s*(\w+)'),
            "header": re.compile(r'^(\s*)#+\s+')
        }

    def parse(self, text):
        """将文本解析为 Block 序列"""
        if not text.strip(): return []
        
        lines = text.splitlines()
        blocks = []
        current_block_lines = []
        state = "paragraph"
        indent_level = 0
        container_type = ""

        i = 0
        while i < len(lines):
            line = lines[i]
            
            # 1. 代码块处理 (优先级最高)
            if state == "code":
                current_block_lines.append(line)
                if self.container_patterns["code"].match(line):
                    blocks.append(MarkdownBlock("\n".join(current_block_lines), "code"))
                    current_block_lines = []
                    state = "paragraph"
                i += 1
                continue

            # 2. 探测状态切换
            code_match = self.container_patterns["code"].match(line)
            if code_match:
                if current_block_lines:
                    blocks.append(MarkdownBlock("\n".join(current_block_lines), state))
                    current_block_lines = []
                state = "code"
                current_block_lines.append(line)
                i += 1
                continue

            # 3. 容器块探测 (Callout / :::)
            callout_match = self.container_patterns["callout"].match(line)
            custom_match = self.container_patterns["custom_container"].match(line)
            header_match = self.container_patterns["header"].match(line)

            if header_match:
                if current_block_lines:
                    blocks.append(MarkdownBlock("\n".join(current_block_lines), state))
                    current_block_lines = []
                blocks.append(MarkdownBlock(line, "header"))
                i += 1
                continue

            # 如果是容器块，我们目前将其视为一个整体（V6.0 暂不递归切碎容器内部，确保翻译上下文连贯）
            if callout_match or custom_match:
                if current_block_lines:
                    blocks.append(MarkdownBlock("\n".join(current_block_lines), state))
                    current_block_lines = []
                
                # 贪婪匹配容器直到边界
                container_start_idx = i
                if callout_match:
                    # Callout 结束于非 > 开头的行
                    while i < len(lines) and (self.container_patterns["callout"].match(lines[i]) or not lines[i].strip()):
                        i += 1
                    blocks.append(MarkdownBlock("\n".join(lines[container_start_idx:i]), "callout"))
                else:
                    # ::: 结束于下一个 :::
                    tag = custom_match.group(2)
                    i += 1
                    while i < len(lines) and not self.container_patterns["custom_container"].match(lines[i]):
                        i += 1
                    if i < len(lines): i += 1 # 包含结尾的 :::
                    blocks.append(MarkdownBlock("\n".join(lines[container_start_idx:i]), "container", {"tag": tag}))
                continue

            # 4. 普通段落处理
            if not line.strip():
                if current_block_lines:
                    blocks.append(MarkdownBlock("\n".join(current_block_lines), "paragraph"))
                    current_block_lines = []
                # 保留空行作为间隔块，确保重组时不丢行
                blocks.append(MarkdownBlock("", "spacer"))
            else:
                current_block_lines.append(line)
            
            i += 1

        # 扫尾
        if current_block_lines:
            blocks.append(MarkdownBlock("\n".join(current_block_lines), state))

        return blocks

    def rebuild(self, blocks):
        """将 Block 序列重新组合为完整文本"""
        return "\n".join([b.content for b in blocks])
