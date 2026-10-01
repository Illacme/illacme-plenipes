# -*- coding: utf-8 -*-
"""
Illacme Plenipes - Bindery HTML Sanitizer & Container Unwrapper
模块职责：将原稿 Markdown 中的前端专用 HTML 容器（如 div, span, style 等）语义化降级与脱壳，
生成专供 Word (.docx)、Markdown 合集 (.md) 与纯文本 (.txt) 的纯净内容，消除前端标签噪音。
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""

import re


class HtmlSanitizer:
    """🧹 装订排版专用的 HTML 容器脱壳与语义降级净化器"""

    # 容器型标签集合（仅保留其内部内容，彻底脱除标签外壳）
    CONTAINER_TAGS = r'(?:div|span|section|article|header|footer|nav|main|aside|figure|figcaption)'

    @classmethod
    def sanitize_to_markdown(cls, text: str) -> str:
        """将包含 HTML 的混排文本清洗为纯净规范的 Markdown（供 Word 与 Markdown 合集使用）"""
        if not text:
            return ""

        # 1. 移除 HTML 注释 <!-- ... -->
        cleaned = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)

        # 2. 将 HTML 标题标签 <h1> - <h6> 映射为标准 Markdown 标题
        for level in range(6, 0, -1):
            h_pattern = rf'<h{level}[^>]*>\s*(.*?)\s*</h{level}>'
            md_prefix = '#' * level
            cleaned = re.sub(h_pattern, rf'\n\n{md_prefix} \1\n\n', cleaned, flags=re.DOTALL | re.IGNORECASE)

        # 3. 将 <br> 转为独立换行
        cleaned = re.sub(r'<br\s*/?>', '\n', cleaned, flags=re.IGNORECASE)

        # 4. 将 <p> 段落脱壳并保留段落间距
        cleaned = re.sub(r'<p[^>]*>\s*(.*?)\s*</p>', r'\n\n\1\n\n', cleaned, flags=re.DOTALL | re.IGNORECASE)

        # 5. 将超链接 <a href="...">text</a> 转为 Markdown 链接 [text](url)
        cleaned = re.sub(r'<a\s+[^>]*href=["\']([^"\']+)["\'][^>]*>\s*(.*?)\s*</a>', r'[\2](\1)', cleaned, flags=re.DOTALL | re.IGNORECASE)

        # 6. 将加粗与斜体转为 Markdown 语法
        cleaned = re.sub(r'<(?:strong|b)[^>]*>\s*(.*?)\s*</(?:strong|b)>', r'**\1**', cleaned, flags=re.DOTALL | re.IGNORECASE)
        cleaned = re.sub(r'<(?:em|i)[^>]*>\s*(.*?)\s*</(?:em|i)>', r'*\1*', cleaned, flags=re.DOTALL | re.IGNORECASE)

        # 7. 将内联代码 <code>...</code> 转为 `...`
        cleaned = re.sub(r'<code[^>]*>\s*(.*?)\s*</code>', r'`\1`', cleaned, flags=re.DOTALL | re.IGNORECASE)

        # 8. 彻底脱壳前端容器型标签 (div, span, section, article 等)
        cleaned = re.sub(rf'</?{cls.CONTAINER_TAGS}[^>]*>', '', cleaned, flags=re.IGNORECASE)

        # 9. 移除残留的空或闭合标签（但保留数学公式或非标签尖括号）
        cleaned = re.sub(r'</?[a-zA-Z][a-zA-Z0-9:-]*[^>]*>', '', cleaned)

        # 10. 折叠多余连续空行，保持干净的 Markdown 拓扑
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)

        return cleaned.strip()

    @classmethod
    def sanitize_to_plain_text(cls, text: str) -> str:
        """将混排文本彻底脱水为 0 标签残留的纯自然语言文本（专供 TXT 便携书）"""
        if not text:
            return ""

        # 先通过 markdown 清洗流程将块级语义提取出来
        md_text = cls.sanitize_to_markdown(text)

        # 去除 Markdown 标题符号
        plain = re.sub(r'^#{1,6}\s*', '', md_text, flags=re.MULTILINE)
        # 去除 Markdown 粗体与斜体
        plain = re.sub(r'\*\*([^*]+)\*\*', r'\1', plain)
        plain = re.sub(r'\*([^*]+)\*', r'\1', plain)
        plain = re.sub(r'`([^`]+)`', r'\1', plain)
        # 去除 Markdown 链接语法 [text](url) -> text
        plain = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', plain)
        # 清除任何残余的尖括号标签
        plain = re.sub(r'<[^>]+>', '', plain)
        # 折叠多余空行
        plain = re.sub(r'\n{3,}', '\n\n', plain)

        return plain.strip()
