"""
📓 Logseq 方言适配器 — Logseq 格式内容的标准化转换。
将 Logseq 特有的大纲式语法、页面引用与属性标记转换为统一中间表示。
"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
from typing import Tuple, Dict, Any
from core.ingress.base import BaseDialect

class LogseqDialect(BaseDialect):
    """🌿 Logseq 方言处理器 (V16.0 插件化版)"""
    
    def normalize(self, text: str, fm_dict: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        # 1. 强力剥离 Logseq 属性块 (Properties)
        text = re.sub(r'^[a-zA-Z0-9_-]+::.*$', '', text, flags=re.MULTILINE)
        
        # 2. 剥离 :LOGBOOK: 及其内部所有内容
        text = re.sub(r':LOGBOOK:.*?:END:', '', text, flags=re.DOTALL | re.IGNORECASE)
        
        # 3. 处理 Logseq 的页面引用: [[Page Name]] -> Page Name
        text = re.sub(r'\[\[([^\]]+)\]\]', r'\1', text)
        
        return text.strip(), fm_dict

    def staticize(self, text: str) -> str:
        """目前暂无特定静态化需求，原样返回"""
        return text
