#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Typora Dialect
模块职责：处理 Typora 专属语法（TOC, Latex Blocks, Image paths）。
🛡️ [AEL-Iter-v5.3]：全自治方言处理器。
"""

import re
from typing import Tuple, Dict, Any
from core.adapters.ingress.base import BaseDialect

class TyporaDialect(BaseDialect):
    """✍️ Typora 方言处理器"""
    
    def normalize(self, text: str, fm_dict: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        # 1. [TOC] 占位符抹除
        text = re.sub(r'^\[TOC\]\s*$', '', text, flags=re.MULTILINE | re.IGNORECASE)
        
        # 2. 处理 Typora 的 Latex 块对齐
        # Typora 有时会生成不带换行的 $$formula$$，某些渲染引擎要求必须有换行
        text = re.sub(r'\$\$(.*?)\$\$', r'\n$$\n\1\n$$\n', text, flags=re.DOTALL)
        
        # 3. 修复 Typora 生成的表格中的异常空行 (Prevent breaking SSG tables)
        text = re.sub(r'\|\n\n\|', '|\n|', text)
        
        return text, fm_dict
