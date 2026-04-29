"""
💎 Obsidian 方言适配器 — Obsidian 格式内容的标准化转换。
将 Obsidian 特有的双链语法、Callout 与嵌入标记转换为统一中间表示。
"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
from typing import Tuple, Dict, Any
from core.ingress.base import BaseDialect

class ObsidianDialect(BaseDialect):
    """💎 Obsidian 方言处理器 (V16.0 插件化版)"""
    
    def normalize(self, text: str, fm_dict: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        # 1. 清理块引用标记 (Block IDs):  ^block-id
        text = re.sub(r'^[ \t]*\^[a-zA-Z0-9-]+[ \t]*$', '', text, flags=re.MULTILINE)
        
        # 2. 处理 Obsidian 专属的高亮语法: ==highlight== -> <mark>highlight</mark>
        text = re.sub(r'==(.+?)==', r'<mark>\1</mark>', text)
        
        # 3. 处理 Obsidian 注释: %%comment%% -> (空)
        text = re.sub(r'%%.*?%%', '', text, flags=re.DOTALL)
        
        return text, fm_dict

    def staticize(self, text: str) -> str:
        """目前暂无特定静态化需求，原样返回"""
        return text
