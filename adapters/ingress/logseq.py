#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Logseq Dialect
模块职责：处理 Logseq 专属语法（Bullet-based structure, Properties, Logbooks）。
🛡️ [AEL-Iter-v5.3]：全自治方言处理器。
"""

import re
from typing import Tuple, Dict, Any
from core.adapters.ingress.base import BaseDialect

class LogseqDialect(BaseDialect):
    """🌿 Logseq 方言处理器"""
    
    def normalize(self, text: str, fm_dict: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        # 1. 强力剥离 Logseq 属性块 (Properties)
        # 匹配文件开头或段落开头的 key:: value 结构
        text = re.sub(r'^[a-zA-Z0-9_-]+::.*$', '', text, flags=re.MULTILINE)
        
        # 2. 剥离 :LOGBOOK: 及其内部所有内容
        text = re.sub(r':LOGBOOK:.*?:END:', '', text, flags=re.DOTALL | re.IGNORECASE)
        
        # 3. 处理 Logseq 的页面引用: [[Page Name]] -> Page Name
        text = re.sub(r'\[\[([^\]]+)\]\]', r'\1', text)
        
        # 4. 清理多余的层级 Bullet 标记
        # Logseq 习惯在每一行前加 '-'，我们需要根据上下文进行柔性处理
        # 这里的策略是只保留真正列表性质的 '-'
        # (简单处理：暂时保持现状，等待后续 AST 静态分析)
        
        return text.strip(), fm_dict
