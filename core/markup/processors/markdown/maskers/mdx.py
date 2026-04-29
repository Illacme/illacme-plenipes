#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Markup Plugin - MDX Security Masker
职责：在 AI 翻译前屏蔽 MDX/JSX 特有代码块。
"""
import re
import uuid
from typing import Dict, Tuple
from core.markup.base import ISecurityMasker

class MDXMasker(ISecurityMasker):
    """🚀 [V16.0] MDX 代码隔离护盾"""
    
    def __init__(self):
        # 预编译 MDX 逻辑块捕获正则
        self.patterns = {
            "import": re.compile(r'^(import\s+(?:\{[^}]+\}|[^;]+)\s+from\s+[\'"][^\'"]+[\'"];?)', re.MULTILINE | re.DOTALL),
            "export": re.compile(r'^(export\s+(?:default\s+)?(?:const|let|var|function|class|type|interface)\s+[^;]+;?)', re.MULTILINE | re.DOTALL),
            "jsx_self": re.compile(r'(<[A-Z][A-Za-z0-9_]*[^>]*?/>)', re.DOTALL),
            "jsx_paired": re.compile(r'(<([A-Z][A-Za-z0-9_]*)[^>]*?>.*?</\2>)', re.DOTALL)
        }

    def mask(self, content: str) -> Tuple[str, Dict[str, str]]:
        masks = {}
        masked_content = content
        
        for name, pattern in self.patterns.items():
            matches = pattern.findall(masked_content)
            # 注意：jsx_paired 返回的是 tuple，取第一个元素
            if name == "jsx_paired":
                matches = [m[0] for m in matches]
                
            for match in set(matches):
                mask_id = f"[[MASK_MDX_{uuid.uuid4().hex[:8]}]]"
                masks[mask_id] = match
                masked_content = masked_content.replace(match, mask_id)
                
        return masked_content, masks

    def unmask(self, content: str, masks: Dict[str, str]) -> str:
        unmasked = content
        for mask_id, original in masks.items():
            unmasked = unmasked.replace(mask_id, original)
        return unmasked
