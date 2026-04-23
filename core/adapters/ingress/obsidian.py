#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Obsidian Dialect
模块职责：处理 Obsidian 专属语法（WikiLinks, Block Refs, Callouts）。
🛡️ [AEL-Iter-v5.3]：全自治方言处理器。
"""

import re
from typing import Tuple, Dict, Any
from .base import BaseDialect

class ObsidianDialect(BaseDialect):
    """💎 Obsidian 方言处理器"""
    
    def normalize(self, text: str, fm_dict: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        # 1. 处理 WikiLinks: [[Link|Alias]] -> Alias 或 [[Link]] -> Link
        # 注意：这里仅提取文本，具体的链接转换由后续 MaskingStep 处理
        text = re.sub(r'\[\[(?:[^\]|]*\|)?([^\]]*)\]\]', r'\1', text)
        
        # 2. 清理块引用标记 (Block IDs):  ^block-id
        text = re.sub(r'^[ \t]*\^[a-zA-Z0-9-]+[ \t]*$', '', text, flags=re.MULTILINE)
        
        # 3. 处理 Obsidian 专属的高亮语法: ==highlight== -> <mark>highlight</mark>
        text = re.sub(r'==(.+?)==', r'<mark>\1</mark>', text)
        
        # 4. 处理 Obsidian 注释: %%comment%% -> (空)
        text = re.sub(r'%%.*?%%', '', text, flags=re.DOTALL)
        
        return text, fm_dict
