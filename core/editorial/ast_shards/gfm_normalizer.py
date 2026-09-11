#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - AST Shards: GFM Normalizer (GFM 降级与绝对外链补全器)
职责：将内联 HTML 片段规约为标准 GFM，并将相对超链接补全为官方站点 Canonical 绝对 URL。
🛡️ [SOP-01] 物理行数保持在 300 行以内。
"""

import re
from typing import Tuple
from urllib.parse import urljoin

class GfmNormalizer:
    """🚀 [V121.0] GFM 语义规范化与外链绝对化转换器"""

    @staticmethod
    def absolutize_links(content: str, site_url: str = "") -> Tuple[str, int]:
        """
        将 Markdown 与 HTML 中所有指向文档的相对链接补全为官方主站的绝对 Canonical URL。
        消除社媒端 404 坏链并建立 SEO 反向链接。
        """
        if not content or not site_url:
            return content, 0

        base_url = site_url.rstrip('/') + '/'
        converted_count = 0

        # 1. 规范化 Markdown 链接 [text](./docs/...)
        def _md_link_repl(match):
            nonlocal converted_count
            text = match.group(1)
            url = match.group(2).strip()
            if url.startswith(('./', '../', '/')) or (not url.startswith(('http://', 'https://', 'mailto:', '#')) and '.' in url):
                clean_rel = url.lstrip('./').lstrip('/')
                abs_url = urljoin(base_url, clean_rel)
                converted_count += 1
                return f"[{text}]({abs_url})"
            return match.group(0)

        content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', _md_link_repl, content)

        # 2. 规范化 HTML <a href="..."> 链接
        def _html_link_repl(match):
            nonlocal converted_count
            pre = match.group(1)
            url = match.group(2).strip()
            post = match.group(3)
            inner_text = match.group(4)
            if url.startswith(('./', '../', '/')) or (not url.startswith(('http://', 'https://', 'mailto:', '#')) and '.' in url):
                clean_rel = url.lstrip('./').lstrip('/')
                abs_url = urljoin(base_url, clean_rel)
                converted_count += 1
                return f'<a {pre}href="{abs_url}"{post}>{inner_text}</a>'
            return match.group(0)

        content = re.sub(r'<a\s+([^>]*?)href=["\']([^"\']+)["\']([^>]*)>(.*?)</a>', _html_link_repl, content, flags=re.IGNORECASE | re.DOTALL)
        return content, converted_count

    @staticmethod
    def html_to_clean_markdown(html_fragment: str) -> str:
        """
        将非整页 HTML 片段中的基础语义标签规约为通用 GFM 语法。
        保留 details/summary 等受支持标签。
        """
        if not html_fragment:
            return ""

        t = html_fragment

        # 1. 转换 h1 ~ h6
        for i in range(6, 0, -1):
            pattern = re.compile(rf'<h{i}\b[^>]*>(.*?)</h{i}>', re.IGNORECASE | re.DOTALL)
            t = pattern.sub(lambda m: f"\n\n{'#' * i} {m.group(1).strip()}\n\n", t)

        # 2. 转换强调和加粗
        t = re.sub(r'<(?:strong|b)\b[^>]*>(.*?)</(?:strong|b)>', r'**\1**', t, flags=re.IGNORECASE | re.DOTALL)
        t = re.sub(r'<(?:em|i)\b[^>]*>(.*?)</(?:em|i)>', r'*\1*', t, flags=re.IGNORECASE | re.DOTALL)

        # 3. 转换 HTML 链接 <a href="url">text</a>
        t = re.sub(
            r'<a\s+[^>]*?href=["\']([^"\']+)["\'][^>]*>(.*?)</a>',
            r'[\2](\1)',
            t,
            flags=re.IGNORECASE | re.DOTALL
        )

        # 4. 转换代码块与行内代码
        t = re.sub(r'<pre><code\b[^>]*>(.*?)</code></pre>', r'\n```\n\1\n```\n', t, flags=re.IGNORECASE | re.DOTALL)
        t = re.sub(r'<code\b[^>]*>(.*?)</code>', r'`\1`', t, flags=re.IGNORECASE | re.DOTALL)

        # 5. 转换段落 <p>
        t = re.sub(r'<p\b[^>]*>(.*?)</p>', r'\n\n\1\n\n', t, flags=re.IGNORECASE | re.DOTALL)

        # 6. 剥离无语义容器 div/span/section/aside/article/main (保留其内部文字，保留 details/summary/table)
        t = re.sub(r'</?(?:div|span|section|aside|article|main)\b[^>]*>', ' ', t, flags=re.IGNORECASE)

        # 7. 整理换行与多余空格
        t = re.sub(r'[ \t]+', ' ', t)
        t = re.sub(r'\n{3,}', '\n\n', t)
        return t.strip()
