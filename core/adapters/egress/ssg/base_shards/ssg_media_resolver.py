# -*- coding: utf-8 -*-
"""
Illacme Plenipes Core - SSG Media Resolver Shard
模块职责：提供富媒体与视频语法的解析与自愈器。
支持能力：
1. Obsidian 本地视频语法 ![[video.mp4]] 与 ![[video.mp4|600]] -> HTML5 <video> 标签
2. Markdown 标准图像语法中的视频 ![](video.mp4) -> HTML5 <video> 标签
3. Bilibili 独立链接与嵌入语法 -> 响应式 16:9 无边框自适应播放器
4. YouTube 独立链接与嵌入语法 -> 响应式 16:9 播放器
5. 严格保护代码块与行内代码，防止误伤代码片段。
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""

import os
import re
from typing import Dict, List, Tuple


class SSGMediaResolver:
    """🎬 SSG 富媒体与视频语法解析器"""

    VIDEO_MIME_MAP: Dict[str, str] = {
        ".mp4": "video/mp4",
        ".webm": "video/webm",
        ".mov": "video/quicktime",
        ".m4v": "video/x-m4v",
        ".ogv": "video/ogg",
        ".mkv": "video/x-matroska",
    }

    VIDEO_EXTENSIONS = tuple(VIDEO_MIME_MAP.keys())

    @classmethod
    def get_video_mime(cls, ext_or_path: str) -> str:
        """获取视频文件对应的 MIME 类型"""
        ext = os.path.splitext(ext_or_path)[1].lower() if "." in ext_or_path else ext_or_path.lower()
        if not ext.startswith("."):
            ext = f".{ext}"
        return cls.VIDEO_MIME_MAP.get(ext, "video/mp4")

    @classmethod
    def is_video_file(cls, path: str) -> bool:
        """判定路径是否为支持的视频格式"""
        clean = path.split("?")[0].split("#")[0].strip().lower()
        return any(clean.endswith(ext) for ext in cls.VIDEO_EXTENSIONS)

    @classmethod
    def resolve_media_content(cls, body: str) -> str:
        """
        全量解析正文中的富媒体语法：
        代码块保护 -> Bilibili/YouTube 嵌入 -> Obsidian 本地视频 -> Markdown 本地视频 -> 恢复代码块
        """
        if not body:
            return body

        # 1. 🛡️ 保护代码块 (```...``` 与 `...`)
        code_blocks: List[str] = []

        def _stash_code(m: re.Match) -> str:
            idx = len(code_blocks)
            code_blocks.append(m.group(0))
            return f"@@MEDIA_CODE_ESC_{idx}@@"

        protected_body = re.sub(r'```[\s\S]*?```', _stash_code, body)
        protected_body = re.sub(r'`[^`\n]+`', _stash_code, protected_body)

        # 2. 📺 解析 Bilibili 嵌入
        protected_body = cls._resolve_bilibili(protected_body)

        # 3. 📺 解析 YouTube 嵌入
        protected_body = cls._resolve_youtube(protected_body)

        # 4. 🎬 解析 Obsidian 本地视频语法 ![[video.mp4]] 或 ![[video.mp4|600]]
        protected_body = cls._resolve_obsidian_video(protected_body)

        # 5. 🎬 解析 Markdown 图像语法中的视频 ![alt](video.mp4)
        protected_body = cls._resolve_markdown_video(protected_body)

        # 6. 还原代码块
        for idx, block in enumerate(code_blocks):
            protected_body = protected_body.replace(f"@@MEDIA_CODE_ESC_{idx}@@", block)

        return protected_body

    @classmethod
    def _render_bilibili_container(cls, bvid: str) -> str:
        """生成 Bilibili 响应式播放容器"""
        return (
            f'\n<div class="video-container responsive-video bilibili-embed">\n'
            f'  <iframe src="//player.bilibili.com/player.html?bvid={bvid}&page=1&high_quality=1&as_wide=1" '
            f'scrolling="no" border="0" frameborder="no" framespacing="0" allowfullscreen="true"></iframe>\n'
            f'</div>\n'
        )

    @classmethod
    def _render_youtube_container(cls, video_id: str) -> str:
        """生成 YouTube 响应式播放容器"""
        return (
            f'\n<div class="video-container responsive-video youtube-embed">\n'
            f'  <iframe src="https://www.youtube-nocookie.com/embed/{video_id}" '
            f'title="YouTube video player" frameborder="0" '
            f'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" '
            f'allowfullscreen></iframe>\n'
            f'</div>\n'
        )

    @classmethod
    def _render_local_video_container(cls, src: str, width_style: str = "") -> str:
        """生成 HTML5 本地视频播放容器"""
        mime = cls.get_video_mime(src)
        clean_src = src.replace("\\", "/")
        style_attr = f' style="{width_style}"' if width_style else ''
        return (
            f'\n<div class="video-container local-video">\n'
            f'  <video controls preload="metadata"{style_attr}>\n'
            f'    <source src="{clean_src}" type="{mime}">\n'
            f'    您的浏览器不支持 HTML5 视频播放。\n'
            f'  </video>\n'
            f'</div>\n'
        )

    @classmethod
    def _resolve_bilibili(cls, text: str) -> str:
        """解析 Bilibili 语法：内嵌与独立行链接"""
        def _obsidian_repl(m: re.Match) -> str:
            bvid = m.group(1)
            return cls._render_bilibili_container(bvid)

        text = re.sub(
            r'!\[\[(?:https?:\/\/)?(?:www\.)?bilibili\.com\/video\/(BV[a-zA-Z0-9]+)[^\]]*\]\]',
            _obsidian_repl,
            text,
            flags=re.IGNORECASE
        )
        text = re.sub(r'!\[\[bilibili:(BV[a-zA-Z0-9]+)\]\]', _obsidian_repl, text, flags=re.IGNORECASE)

        text = re.sub(
            r'!\[[^\]]*\]\((?:https?:\/\/)?(?:www\.)?bilibili\.com\/video\/(BV[a-zA-Z0-9]+)[^)]*\)',
            _obsidian_repl,
            text,
            flags=re.IGNORECASE
        )

        def _standalone_repl(m: re.Match) -> str:
            prefix = m.group(1)
            bvid = m.group(2)
            return f"{prefix}{cls._render_bilibili_container(bvid)}"

        text = re.sub(
            r'(^|\n)(?:https?:\/\/)?(?:www\.)?bilibili\.com\/video\/(BV[a-zA-Z0-9]+)(?:[^\s\n]*)?(?=$|\n)',
            _standalone_repl,
            text,
            flags=re.IGNORECASE
        )
        text = re.sub(
            r'(^|\n)(?:https?:\/\/)?b23\.tv\/(BV[a-zA-Z0-9]+)(?:[^\s\n]*)?(?=$|\n)',
            _standalone_repl,
            text,
            flags=re.IGNORECASE
        )
        return text

    @classmethod
    def _resolve_youtube(cls, text: str) -> str:
        """解析 YouTube 语法：内嵌与独立行链接"""
        def _yt_repl(m: re.Match) -> str:
            vid = m.group(1)
            return cls._render_youtube_container(vid)

        text = re.sub(
            r'!\[\[(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})[^\]]*\]\]',
            _yt_repl,
            text,
            flags=re.IGNORECASE
        )
        text = re.sub(r'!\[\[youtube:([a-zA-Z0-9_-]{11})\]\]', _yt_repl, text, flags=re.IGNORECASE)

        text = re.sub(
            r'!\[[^\]]*\]\((?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})[^)]*\)',
            _yt_repl,
            text,
            flags=re.IGNORECASE
        )

        def _standalone_yt_repl(m: re.Match) -> str:
            prefix = m.group(1)
            vid = m.group(2)
            return f"{prefix}{cls._render_youtube_container(vid)}"

        text = re.sub(
            r'(^|\n)(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([a-zA-Z0-9_-]{11})(?:[^\s\n]*)?(?=$|\n)',
            _standalone_yt_repl,
            text,
            flags=re.IGNORECASE
        )
        text = re.sub(
            r'(^|\n)(?:https?:\/\/)?youtu\.be\/([a-zA-Z0-9_-]{11})(?:[^\s\n]*)?(?=$|\n)',
            _standalone_yt_repl,
            text,
            flags=re.IGNORECASE
        )
        return text

    @classmethod
    def _resolve_obsidian_video(cls, text: str) -> str:
        """解析 Obsidian 本地视频嵌入 ![[video.mp4]] 与 ![[video.mp4|600]]"""
        ext_pattern = "|".join([re.escape(ext.lstrip(".")) for ext in cls.VIDEO_EXTENSIONS])
        obsidian_pattern = re.compile(
            rf'!\[\[([^\]|]+?\.(?:{ext_pattern}))(?:\s*\|\s*([^\]]+))?\]\]',
            re.IGNORECASE
        )

        def _repl(m: re.Match) -> str:
            raw_src = m.group(1).strip()
            spec = (m.group(2) or "").strip()
            style = ""
            if spec:
                dim_m = re.match(r'^(\d+)(?:x\d+)?$', spec)
                if dim_m:
                    style = f"max-width: {dim_m.group(1)}px;"
                elif "width=" in spec:
                    w_val = spec.split("width=")[1].split(";")[0].strip()
                    style = f"max-width: {w_val};"
            return cls._render_local_video_container(raw_src, style)

        return obsidian_pattern.sub(_repl, text)

    @classmethod
    def _resolve_markdown_video(cls, text: str) -> str:
        """解析 Markdown 图像语法中的视频 ![alt](video.mp4)"""
        ext_pattern = "|".join([re.escape(ext.lstrip(".")) for ext in cls.VIDEO_EXTENSIONS])
        md_pattern = re.compile(
            rf'!\[([^\]]*)\]\(([^)\s]+?\.(?:{ext_pattern}))(?:\s+["\'](.*?)["\'])?\)',
            re.IGNORECASE
        )

        def _repl(m: re.Match) -> str:
            src = m.group(2).strip()
            return cls._render_local_video_container(src)

        return md_pattern.sub(_repl, text)
