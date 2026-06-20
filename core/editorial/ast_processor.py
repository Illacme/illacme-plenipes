#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Editorial AST Processor (文稿格式与资产处理器)
职责：对文稿进行分发前格式规约，处理相对路径资产上云与特定渠道的版式降级。
🛡️ [SOP-01] 物理行数限制：保持在 300 行以内。
"""

import os
import re
from typing import Callable

class MarkdownASTProcessor:
    def __init__(self):
        # 匹配本地相对路径图片 ![alt](path)
        self.img_pattern = re.compile(r'!\[(.*?)\]\(((?!https?://)(.*?))\)')
        # 匹配 HTML img src="path" 相对路径图片
        self.html_img_pattern = re.compile(r'<img[^>]+src=["\']((?!https?://)([^"\']+))["\']')

    def process_images(self, content: str, doc_dir: str, upload_fn: Callable[[str], str]) -> str:
        """
        提取正文中的相对路径图片，转换为绝对物理路径，调用 upload_fn 回调上传并原地替换链接。
        """
        if not content:
            return content

        def replace_img(match):
            alt_text = match.group(1)
            rel_path = match.group(2).strip()
            # 剔除可能存在的查询参数
            clean_path = rel_path.split('?')[0]
            
            # 定位本地物理路径
            abs_path = os.path.normpath(os.path.join(doc_dir, clean_path))
            if os.path.exists(abs_path) and os.path.isfile(abs_path):
                try:
                    public_url = upload_fn(abs_path)
                    if public_url:
                        query = rel_path.split('?')[1] if '?' in rel_path else ''
                        final_url = f"{public_url}?{query}" if query else public_url
                        return f"![{alt_text}]({final_url})"
                except Exception:
                    pass
            return match.group(0)

        # 1. 匹配替换标准 Markdown 图片
        content = self.img_pattern.sub(replace_img, content)

        # 2. 匹配替换 HTML img 标签 中的相对路径图片
        def replace_html_img(match):
            full_tag = match.group(0)
            rel_path = match.group(1).strip()
            clean_path = rel_path.split('?')[0]
            abs_path = os.path.normpath(os.path.join(doc_dir, clean_path))
            if os.path.exists(abs_path) and os.path.isfile(abs_path):
                try:
                    public_url = upload_fn(abs_path)
                    if public_url:
                        query = rel_path.split('?')[1] if '?' in rel_path else ''
                        final_url = f"{public_url}?{query}" if query else public_url
                        return full_tag.replace(rel_path, final_url)
                except Exception:
                    pass
            return full_tag

        content = self.html_img_pattern.sub(replace_html_img, content)
        return content

    def adapt_format(self, content: str, target_platform: str) -> str:
        """
        多平台版式降级规范化：针对特定发布平台对正文进行排版微调。
        - Medium: 不支持 # (H1) 和 ## (H2)，需自动降级为 ### (H3)。
        """
        if not content:
            return content
            
        platform = (target_platform or "").lower()
        if "medium" in platform:
            lines = content.split('\n')
            new_lines = []
            for line in lines:
                if line.startswith('# '):
                    line = '### ' + line[2:]
                elif line.startswith('## '):
                    line = '### ' + line[3:]
                new_lines.append(line)
            return '\n'.join(new_lines)
            
        return content
