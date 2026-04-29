#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Logic - Context Compressor
模块职责：语义算力精简。在不损失核心语义的前提下，通过结构化压缩降低 AI 请求的 Token 开销。
🛡️ [AEL-Iter-v1.0]：支持 Markdown 噪声过滤与关键段落提取。
"""

import re
from typing import Optional

class ContextCompressor:
    """🚀 [V1.0] 语义压缩引擎：物理级 Token 节约器"""
    
    @staticmethod
    def compress_markdown(text: str, max_chars: int = 5000) -> str:
        """
        压缩 Markdown 文本
        1. 移除 HTML 注释
        2. 合并多余空行
        3. 剔除 YAML Frontmatter (通常由业务层单独处理)
        4. 截断超长内容
        """
        if not text: return ""
        
        # 1. 移除 YAML Frontmatter (--- ... ---)
        text = re.sub(r'^---.*?---', '', text, flags=re.DOTALL)
        
        # 2. 移除 HTML 注释 (<!-- ... -->)
        text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
        
        # 3. 合并连续空行
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # 4. 移除行首尾空格
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(lines)
        
        # 5. 物理截断 (针对非翻译任务，如 SEO/Slug)
        if len(text) > max_chars:
            text = text[:max_chars] + "\n\n...(Content truncated for token efficiency)"
            
        return text.strip()

    @staticmethod
    def extract_core_semantics(text: str) -> str:
        """
        提取核心语义 (主要用于 SEO 生成)
        优先保留标题、第一段 and 最后一段
        """
        lines = text.split('\n')
        headers = [line for line in lines if line.startswith('#')]
        
        if len(lines) < 10: return text
        
        # 保留前 500 字和最后 500 字
        head = text[:800]
        tail = text[-400:] if len(text) > 1200 else ""
        
        return f"{head}\n\n[...]\n\n{tail}"
