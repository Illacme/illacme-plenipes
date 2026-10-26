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

        # 0. 转换视频与音频嵌入 iframe 为高亲和性 Markdown 链接引用卡片
        def _iframe_to_md_link(match):
            src = match.group(1).strip()
            orig_url = src
            name, emoji = "在线演示与多媒体资源", "🔗"
            if "player.bilibili.com" in src or "bilibili.com" in src:
                bvid_m = re.search(r'bvid=(BV[a-zA-Z0-9]+)', src)
                if bvid_m: orig_url = f"https://www.bilibili.com/video/{bvid_m.group(1)}"
                name, emoji = "哔哩哔哩视频演示", "📺"
            elif "youtube" in src:
                yt_m = re.search(r'embed/([a-zA-Z0-9_-]{11})', src)
                if yt_m: orig_url = f"https://www.youtube.com/watch?v={yt_m.group(1)}"
                name, emoji = "YouTube 视频演示", "▶️"
            elif "vimeo.com" in src:
                vim_m = re.search(r'video/([0-9]+)', src)
                if vim_m: orig_url = f"https://vimeo.com/{vim_m.group(1)}"
                name, emoji = "Vimeo 视频演示", "🎬"
            elif "v.qq.com" in src:
                qq_m = re.search(r'vid=([a-zA-Z0-9]+)', src)
                if qq_m: orig_url = f"https://v.qq.com/x/cover/{qq_m.group(1)}.html"
                name, emoji = "腾讯视频演示", "🎥"
            elif "music.163.com" in src:
                ne_m = re.search(r'id=([0-9]+)', src)
                if ne_m: orig_url = f"https://music.163.com/song?id={ne_m.group(1)}"
                name, emoji = "网易云音乐", "🎵"
            elif "spotify" in src:
                sp_m = re.search(r'track/([a-zA-Z0-9]+)', src)
                if sp_m: orig_url = f"https://open.spotify.com/track/{sp_m.group(1)}"
                name, emoji = "Spotify 音乐", "🎧"
            elif "codepen.io" in src:
                name, emoji = "CodePen 交互代码演示", "💻"

            if orig_url.startswith("//"):
                orig_url = "https:" + orig_url

            return f"\n\n> {emoji} **[{name}：点击直达原网页播放与体验]({orig_url})**\n\n"

        t = re.sub(
            r'<iframe[^>]*?src=["\']([^"\']+)["\'][^>]*>.*?</iframe>',
            _iframe_to_md_link,
            t,
            flags=re.IGNORECASE | re.DOTALL
        )

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
