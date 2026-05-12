#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Markup Plugin - Standard Markdown Blocks
职责：处理符合 CommonMark 规范的标准块。
"""
import re
from typing import Dict, Any, List
from core.markup.base import ISyntaxBlockPlugin

class HeaderBlockPlugin(ISyntaxBlockPlugin):
    """# Header 插件"""
    PLUGIN_ID = "standard_header"
    DISPLAY_NAME = "Markdown Headers"
    DESCRIPTION = "解析标准 Markdown 标题语法（#），支持多级标题的结构化感应与锚点生成。"
    @property
    def block_type(self) -> str: return "header"

    def get_start_pattern(self) -> str:
        return r'^(\s*)#+\s+'

    def is_end(self, line: str, state: Dict[str, Any]) -> bool:
        # Header 是一行式的，起始即结束
        return True

class CodeBlockPlugin(ISyntaxBlockPlugin):
    """```Code Block 插件"""
    PLUGIN_ID = "standard_code"
    DISPLAY_NAME = "Markdown Code Blocks"
    DESCRIPTION = "解析标准 Markdown 代码块语法（```），支持多语言语法高亮标识的提取与处理。"
    @property
    def block_type(self) -> str: return "code"

    def get_start_pattern(self) -> str:
        return r'^(\s*)```'

    def is_end(self, line: str, state: Dict[str, Any]) -> bool:
        # 记录起始缩进，只有匹配到闭合的 ``` 才结束
        if line.strip() == "```":
            return True
        return False

    @property
    def include_end_line(self) -> bool: return True
