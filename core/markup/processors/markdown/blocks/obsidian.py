#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Markup Plugin - Obsidian Specific Blocks
职责：处理 Obsidian 专属的复杂容器（如 Callouts）。
"""
import re
from typing import Dict, Any
from core.markup.base import ISyntaxBlockPlugin

class CalloutBlockPlugin(ISyntaxBlockPlugin):
    """> [!INFO] Callout 插件"""
    @property
    def block_type(self) -> str: return "callout"

    def get_start_pattern(self) -> str:
        # 匹配 Obsidian 风格的 Callout 起始
        return r'^(\s*)>\s*\[\!'

    def is_end(self, line: str, state: Dict[str, Any]) -> bool:
        # Callout 结束于非 > 开头的行（且非空行）
        if not line.strip():
            return False # 空行允许存在于 Callout 内部
        if not line.lstrip().startswith(">"):
            return True
        return False
