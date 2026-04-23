#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Notion Dialect
模块职责：处理 Notion 导出语法（UUID 清洗、引用块对齐）的标准化。
🛡️ [AEL-Iter-v5.3]：模块化归位后的纯净处理器。
"""

import re
from typing import Tuple, Dict, Any
from .base import BaseDialect

class NotionDialect(BaseDialect):
    """🌀 Notion 方言处理器：处理 UUID 后缀清洗与引用块转换"""
    def normalize(self, text: str, fm_dict: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        # 1. 链接中的 UUID 物理清洗 (Notion 导出时常在文件名后带 32 位 ID)
        text = re.sub(r'(\.md|\.png|\.jpg|\.pdf)([a-f0-9]{32})', r'\1', text)
        return text, fm_dict
