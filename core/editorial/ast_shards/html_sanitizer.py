#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - AST Shards: HTML Sanitizer (全页外壳剥离与黑名单清洗器)
职责：探测并剥离整站 HTML 壳 (DOCTYPE/head/script/style/nav)，提取纯净语义主体。
🛡️ [SOP-01] 物理行数保持在 300 行以内。
"""

import re
from typing import Tuple

# 严打黑名单标签 (整站外壳、脚本、样式与全局导航)
PAGE_SHELL_PATTERNS = [
    re.compile(r'<!DOCTYPE[^>]*>', re.IGNORECASE),
    re.compile(r'<head\b[^>]*>.*?</head>', re.IGNORECASE | re.DOTALL),
    re.compile(r'<script\b[^>]*>.*?</script>', re.IGNORECASE | re.DOTALL),
    re.compile(r'<style\b[^>]*>.*?</style>', re.IGNORECASE | re.DOTALL),
    re.compile(r'<header\b[^>]*>.*?</header>', re.IGNORECASE | re.DOTALL),
    re.compile(r'<nav\b[^>]*>.*?</nav>', re.IGNORECASE | re.DOTALL),
    re.compile(r'<footer\b[^>]*>.*?</footer>', re.IGNORECASE | re.DOTALL),
    re.compile(r'<meta\b[^>]*>', re.IGNORECASE),
    re.compile(r'<link\b[^>]*>', re.IGNORECASE),
    re.compile(r'</?(?:html|body)[^>]*>', re.IGNORECASE),
]

class HtmlSanitizer:
    """🚀 [V121.0] 整页外壳剥离器与 HTML 深度清洗器"""

    @staticmethod
    def is_full_html_page(content: str) -> bool:
        """快速探测是否为完整的静态 HTML 网页（而非纯 Markdown 文章）"""
        if not content:
            return False
        sample = content[:1500].lower()
        return "<!doctype html" in sample or "<html" in sample or "<head" in sample

    @classmethod
    def strip_html_boilerplate(cls, content: str) -> Tuple[str, int]:
        """
        物理剥离整页 HTML 网页外壳，返回 (清洗后的正文片段, 剔除的标签行数估算)。
        保留创作者常用的合法内联标签 (如 details, summary, kbd, code)。
        """
        if not content:
            return "", 0

        initial_len = len(content.splitlines())
        clean_text = content

        # 1. 优先尝试提取 <main> 或 <article> 核心内容区
        main_match = re.search(r'<(?:main|article)\b[^>]*>(.*?)</(?:main|article)>', clean_text, re.IGNORECASE | re.DOTALL)
        if main_match:
            clean_text = main_match.group(1).strip()
        else:
            # 尝试提取 <body> 内部
            body_match = re.search(r'<body\b[^>]*>(.*?)</body>', clean_text, re.IGNORECASE | re.DOTALL)
            if body_match:
                clean_text = body_match.group(1).strip()

        # 2. 彻底剥离黑名单标签与全局外壳
        for pattern in PAGE_SHELL_PATTERNS:
            clean_text = pattern.sub('', clean_text)

        # 3. 移除多余注释 (保留 Callout 预置标记)
        clean_text = re.sub(r'<!--(?!\s*@@)(?:(?!-->).)*?-->', '', clean_text, flags=re.DOTALL)

        # 4. 消除多余空行
        lines = [line.rstrip() for line in clean_text.split('\n')]
        stripped_lines = []
        consecutive_empty = 0
        for line in lines:
            if not line:
                consecutive_empty += 1
                if consecutive_empty <= 2:
                    stripped_lines.append(line)
            else:
                consecutive_empty = 0
                stripped_lines.append(line)

        final_content = '\n'.join(stripped_lines).strip()
        stripped_count = max(0, initial_len - len(stripped_lines))
        return final_content, stripped_count
