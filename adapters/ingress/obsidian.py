#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Obsidian Dialect
模块职责：处理 Obsidian 专属语法（WikiLinks, Block Refs, Callouts）。
🛡️ [AEL-Iter-v5.3]：全自治方言处理器。
"""

import re
from typing import Tuple, Dict, Any
from core.adapters.ingress.base import BaseDialect

class ObsidianDialect(BaseDialect):
    """💎 Obsidian 方言处理器"""
    
    def normalize(self, text: str, fm_dict: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        # 1. 🚀 [V10.4] 路由主权：WikiLinks 不再在此处剥离。
        # 括号将保留并流转至 masking_routing 步骤进行深度提取与占位符遮蔽。
        pass
        
        # 2. 清理块引用标记 (Block IDs):  ^block-id
        text = re.sub(r'^[ \t]*\^[a-zA-Z0-9-]+[ \t]*$', '', text, flags=re.MULTILINE)
        
        # 3. 处理 Obsidian 专属的高亮语法: ==highlight== -> <mark>highlight</mark>
        text = re.sub(r'==(.+?)==', r'<mark>\1</mark>', text)
        
        # 4. 处理 Obsidian 注释: %%comment%% -> (空)
        text = re.sub(r'%%.*?%%', '', text, flags=re.DOTALL)
        
        return text, fm_dict
