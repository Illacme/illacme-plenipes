# -*- coding: utf-8 -*-
"""
Illacme Plenipes Core - SSG Media Resolver Shard
模块职责：提供富媒体（视频与音频）语法的统一解析与自愈器。
支持能力：
1. Obsidian 本地视频语法 ![[video.mp4]] 与 ![[video.mp4|600]] -> HTML5 <video> 标签
2. Markdown 标准图像语法中的视频 ![](video.mp4) -> HTML5 <video> 标签
3. Obsidian 本地音频语法 ![[audio.mp3]] 与 ![](audio.wav) -> HTML5 <audio> 标签
4. Bilibili 独立链接与嵌入语法 -> 响应式 16:9 无边框自适应播放器
5. YouTube 独立链接与嵌入语法 -> 响应式 16:9 播放器
6. 严格保护代码块与行内代码，防止误伤代码片段。
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""

import os
import re
from typing import Dict, List, Tuple


class SSGMediaResolver:
    """🎬 SSG 富媒体（视频与音频）语法解析器"""

    VIDEO_MIME_MAP: Dict[str, str] = {
        ".mp4": "video/mp4",
        ".webm": "video/webm",
        ".mov": "video/quicktime",
        ".m4v": "video/x-m4v",
        ".ogv": "video/ogg",
        ".mkv": "video/x-matroska",
    }
    VIDEO_EXTENSIONS = tuple(VIDEO_MIME_MAP.keys())

    AUDIO_MIME_MAP: Dict[str, str] = {
        ".mp3": "audio/mpeg",
        ".wav": "audio/wav",
        ".ogg": "audio/ogg",
        ".m4a": "audio/mp4",
        ".aac": "audio/aac",
        ".flac": "audio/flac",
    }
    AUDIO_EXTENSIONS = tuple(AUDIO_MIME_MAP.keys())

    @classmethod
    def get_video_mime(cls, ext_or_path: str) -> str:
        """获取视频文件对应的 MIME 类型"""
        ext = os.path.splitext(ext_or_path)[1].lower() if "." in ext_or_path else ext_or_path.lower()
        if not ext.startswith("."): ext = f".{ext}"
        return cls.VIDEO_MIME_MAP.get(ext, "video/mp4")

    @classmethod
    def get_audio_mime(cls, ext_or_path: str) -> str:
        """获取音频文件对应的 MIME 类型"""
        ext = os.path.splitext(ext_or_path)[1].lower() if "." in ext_or_path else ext_or_path.lower()
        if not ext.startswith("."): ext = f".{ext}"
        return cls.AUDIO_MIME_MAP.get(ext, "audio/mpeg")

    @classmethod
    def resolve_media_content(cls, body: str) -> str:
        """全量解析正文中的富媒体（视频/音频/在线平台）语法"""
        if not body: return body

        # 1. 🛡️ 保护代码块 (```...``` 与 `...`)
        code_blocks: List[str] = []
        def _stash_code(m: re.Match) -> str:
            idx = len(code_blocks)
            code_blocks.append(m.group(0))
            return f"@@MEDIA_CODE_ESC_{idx}@@"

        protected_body = re.sub(r'```[\s\S]*?```', _stash_code, body)
        protected_body = re.sub(r'`[^`\n]+`', _stash_code, protected_body)

        # 2. 📺 解析在线流媒体与交互平台
        protected_body = cls._resolve_bilibili(protected_body)
        protected_body = cls._resolve_youtube(protected_body)
        protected_body = cls._resolve_vimeo(protected_body)
        protected_body = cls._resolve_qq_video(protected_body)
        protected_body = cls._resolve_netease_music(protected_body)
        protected_body = cls._resolve_spotify(protected_body)
        protected_body = cls._resolve_codepen(protected_body)

        # 3. 🎬 解析本地视频与音频
        protected_body = cls._resolve_obsidian_video(protected_body)
        protected_body = cls._resolve_markdown_video(protected_body)
        protected_body = cls._resolve_obsidian_audio(protected_body)
        protected_body = cls._resolve_markdown_audio(protected_body)

        # 4. 还原代码块
        for idx, block in enumerate(code_blocks):
            protected_body = protected_body.replace(f"@@MEDIA_CODE_ESC_{idx}@@", block)

        return protected_body

    @classmethod
    def _render_bilibili_container(cls, bvid: str, query: str = "") -> str:
        page = "1"
        if query:
            p_match = re.search(r'[?&](?:p|page)=([0-9]+)', str(query), re.I)
            if p_match: page = p_match.group(1)
        return (
            f'\n<div class="video-container responsive-video bilibili-embed">\n'
            f'  <iframe src="//player.bilibili.com/player.html?bvid={bvid}&page={page}&high_quality=1&as_wide=1" '
            f'scrolling="no" border="0" frameborder="no" framespacing="0" allowfullscreen="true"></iframe>\n'
            f'</div>\n'
        )

    @classmethod
    def _render_youtube_container(cls, video_id: str, query: str = "") -> str:
        extra = ""
        if query:
            t_match = re.search(r'[?&](?:t|start)=([0-9]+)s?', str(query), re.I)
            if t_match: extra = f"?start={t_match.group(1)}"
        return (
            f'\n<div class="video-container responsive-video youtube-embed">\n'
            f'  <iframe src="https://www.youtube-nocookie.com/embed/{video_id}{extra}" '
            f'title="YouTube video player" frameborder="0" '
            f'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" '
            f'allowfullscreen></iframe>\n'
            f'</div>\n'
        )

    @classmethod
    def _render_local_video_container(cls, src: str, width_style: str = "") -> str:
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
    def _render_local_audio_container(cls, src: str) -> str:
        mime = cls.get_audio_mime(src)
        clean_src = src.replace("\\", "/")
        return (
            f'\n<div class="audio-container local-audio">\n'
            f'  <audio controls preload="metadata">\n'
            f'    <source src="{clean_src}" type="{mime}">\n'
            f'    您的浏览器不支持 HTML5 音频播放。\n'
            f'  </audio>\n'
            f'</div>\n'
        )

    @classmethod
    def _resolve_bilibili(cls, text: str) -> str:
        def _repl(m: re.Match) -> str: return cls._render_bilibili_container(m.group(1), m.group(2) if len(m.groups()) >= 2 else "")
        text = re.sub(r'!\[\[(?:https?:\/\/)?(?:www\.)?bilibili\.com\/video\/(BV[a-zA-Z0-9]+)([^\]]*)\]\]', _repl, text, flags=re.I)
        text = re.sub(r'!\[\[bilibili:(BV[a-zA-Z0-9]+)([^\]]*)\]\]', _repl, text, flags=re.I)
        text = re.sub(r'!\[[^\]]*\]\((?:https?:\/\/)?(?:www\.)?bilibili\.com\/video\/(BV[a-zA-Z0-9]+)([^)]*)\)', _repl, text, flags=re.I)

        def _standalone(m: re.Match) -> str: return f"{m.group(1)}{cls._render_bilibili_container(m.group(2), m.group(3) if len(m.groups()) >= 3 else '')}"
        text = re.sub(r'(^|\n)(?:https?:\/\/)?(?:www\.)?bilibili\.com\/video\/(BV[a-zA-Z0-9]+)(\?[^\s\n]*)?(?=$|\n)', _standalone, text, flags=re.I)
        text = re.sub(r'(^|\n)(?:https?:\/\/)?b23\.tv\/(BV[a-zA-Z0-9]+)(\?[^\s\n]*)?(?=$|\n)', _standalone, text, flags=re.I)
        return text

    @classmethod
    def _resolve_youtube(cls, text: str) -> str:
        def _repl(m: re.Match) -> str: return cls._render_youtube_container(m.group(1), m.group(2) if len(m.groups()) >= 2 else "")
        text = re.sub(r'!\[\[(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})([^\]]*)\]\]', _repl, text, flags=re.I)
        text = re.sub(r'!\[\[youtube:([a-zA-Z0-9_-]{11})([^\]]*)\]\]', _repl, text, flags=re.I)
        text = re.sub(r'!\[[^\]]*\]\((?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})([^)]*)\)', _repl, text, flags=re.I)

        def _standalone(m: re.Match) -> str: return f"{m.group(1)}{cls._render_youtube_container(m.group(2), m.group(3) if len(m.groups()) >= 3 else '')}"
        text = re.sub(r'(^|\n)(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([a-zA-Z0-9_-]{11})(\?[^\s\n]*)?(?=$|\n)', _standalone, text, flags=re.I)
        text = re.sub(r'(^|\n)(?:https?:\/\/)?youtu\.be\/([a-zA-Z0-9_-]{11})(\?[^\s\n]*)?(?=$|\n)', _standalone, text, flags=re.I)
        return text

    @classmethod
    def _resolve_vimeo(cls, text: str) -> str:
        def _render(vid: str) -> str:
            return (
                f'\n<div class="video-container responsive-video vimeo-embed" style="position:relative;width:100%;aspect-ratio:16/9;margin:14px 0;">\n'
                f'  <iframe src="https://player.vimeo.com/video/{vid}" frameborder="0" allow="autoplay; fullscreen; picture-in-picture" allowfullscreen style="position:absolute;top:0;left:0;width:100%;height:100%;border:none;border-radius:8px;"></iframe>\n'
                f'</div>\n'
            )
        text = re.sub(r'!\[\[(?:https?:\/\/)?(?:www\.)?vimeo\.com\/([0-9]+)[^\]]*\]\]', lambda m: _render(m.group(1)), text, flags=re.I)
        text = re.sub(r'!\[[^\]]*\]\((?:https?:\/\/)?(?:www\.)?vimeo\.com\/([0-9]+)[^)]*\)', lambda m: _render(m.group(1)), text, flags=re.I)
        return re.sub(r'(^|\n)(?:https?:\/\/)?(?:www\.)?vimeo\.com\/([0-9]+)(?:[^\s\n]*)?(?=$|\n)', lambda m: f"{m.group(1)}{_render(m.group(2))}", text, flags=re.I)

    @classmethod
    def _resolve_qq_video(cls, text: str) -> str:
        def _render(vid: str) -> str:
            return (
                f'\n<div class="video-container responsive-video qq-video-embed" style="position:relative;width:100%;aspect-ratio:16/9;margin:14px 0;">\n'
                f'  <iframe src="https://v.qq.com/txp/iframe/player.html?vid={vid}" allowFullScreen="true" frameborder="0" style="position:absolute;top:0;left:0;width:100%;height:100%;border:none;border-radius:8px;"></iframe>\n'
                f'</div>\n'
            )
        patt = r'(?:https?:\/\/)?v\.qq\.com\/x\/(?:cover\/[a-zA-Z0-9]+\/|page\/)([a-zA-Z0-9]+)\.html'
        text = re.sub(rf'!\[\[{patt}[^\]]*\]\]', lambda m: _render(m.group(1)), text, flags=re.I)
        text = re.sub(rf'!\[[^\]]*\]\({patt}[^)]*\)', lambda m: _render(m.group(1)), text, flags=re.I)
        return re.sub(rf'(^|\n){patt}(?:[^\s\n]*)?(?=$|\n)', lambda m: f"{m.group(1)}{_render(m.group(2))}", text, flags=re.I)

    @classmethod
    def _resolve_netease_music(cls, text: str) -> str:
        def _render(song_id: str) -> str:
            return (
                f'\n<div class="audio-container netease-music-embed" style="margin:14px 0;">\n'
                f'  <iframe frameborder="no" border="0" marginwidth="0" marginheight="0" width="100%" height="86" src="//music.163.com/outchain/player?type=2&id={song_id}&auto=0&height=66"></iframe>\n'
                f'</div>\n'
            )
        patt = r'(?:https?:\/\/)?music\.163\.com\/(?:#\/)?song\?id=([0-9]+)'
        text = re.sub(rf'!\[\[{patt}[^\]]*\]\]', lambda m: _render(m.group(1)), text, flags=re.I)
        text = re.sub(rf'!\[[^\]]*\]\({patt}[^)]*\)', lambda m: _render(m.group(1)), text, flags=re.I)
        return re.sub(rf'(^|\n){patt}(?:[^\s\n]*)?(?=$|\n)', lambda m: f"{m.group(1)}{_render(m.group(2))}", text, flags=re.I)

    @classmethod
    def _resolve_spotify(cls, text: str) -> str:
        def _render(m_type: str, m_id: str) -> str:
            return (
                f'\n<div class="audio-container spotify-embed" style="margin:14px 0;">\n'
                f'  <iframe style="border-radius:12px;border:none;" src="https://open.spotify.com/embed/{m_type}/{m_id}" width="100%" height="152" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>\n'
                f'</div>\n'
            )
        patt = r'(?:https?:\/\/)?open\.spotify\.com\/(track|episode|album)\/([a-zA-Z0-9]+)'
        text = re.sub(rf'!\[\[{patt}[^\]]*\]\]', lambda m: _render(m.group(1), m.group(2)), text, flags=re.I)
        text = re.sub(rf'!\[[^\]]*\]\({patt}[^)]*\)', lambda m: _render(m.group(1), m.group(2)), text, flags=re.I)
        return re.sub(rf'(^|\n){patt}(?:[^\s\n]*)?(?=$|\n)', lambda m: f"{m.group(1)}{_render(m.group(2), m.group(3))}", text, flags=re.I)

    @classmethod
    def _resolve_codepen(cls, text: str) -> str:
        def _render(user: str, pen_id: str) -> str:
            return (
                f'\n<div class="embed-container codepen-embed" style="margin:14px 0;">\n'
                f'  <iframe height="360" style="width:100%;border-radius:8px;border:none;" scrolling="no" title="CodePen Embed" src="https://codepen.io/{user}/embed/{pen_id}?default-tab=result" frameborder="no" loading="lazy" allowtransparency="true" allowfullscreen="true"></iframe>\n'
                f'</div>\n'
            )
        patt = r'(?:https?:\/\/)?codepen\.io\/([a-zA-Z0-9_-]+)\/pen\/([a-zA-Z0-9_-]+)'
        text = re.sub(rf'!\[\[{patt}[^\]]*\]\]', lambda m: _render(m.group(1), m.group(2)), text, flags=re.I)
        text = re.sub(rf'!\[[^\]]*\]\({patt}[^)]*\)', lambda m: _render(m.group(1), m.group(2)), text, flags=re.I)
        return re.sub(rf'(^|\n){patt}(?:[^\s\n]*)?(?=$|\n)', lambda m: f"{m.group(1)}{_render(m.group(2), m.group(3))}", text, flags=re.I)

    @classmethod
    def _resolve_obsidian_video(cls, text: str) -> str:
        patt = "|".join([re.escape(e.lstrip(".")) for e in cls.VIDEO_EXTENSIONS])
        obs_p = re.compile(rf'!\[\[([^\]|]+?\.(?:{patt}))(?:\s*\|\s*([^\]]+))?\]\]', re.I)
        def _repl(m: re.Match) -> str:
            raw_src = m.group(1).strip()
            spec = (m.group(2) or "").strip()
            style = ""
            if spec:
                dim_m = re.match(r'^(\d+)(?:x\d+)?$', spec)
                if dim_m: style = f"max-width: {dim_m.group(1)}px;"
                elif "width=" in spec: style = f"max-width: {spec.split('width=')[1].split(';')[0].strip()};"
            return cls._render_local_video_container(raw_src, style)
        return obs_p.sub(_repl, text)

    @classmethod
    def _resolve_markdown_video(cls, text: str) -> str:
        patt = "|".join([re.escape(e.lstrip(".")) for e in cls.VIDEO_EXTENSIONS])
        md_p = re.compile(rf'!\[([^\]]*)\]\(([^)\s]+?\.(?:{patt}))(?:\s+["\'](.*?)["\'])?\)', re.I)
        return md_p.sub(lambda m: cls._render_local_video_container(m.group(2).strip()), text)

    @classmethod
    def _resolve_obsidian_audio(cls, text: str) -> str:
        patt = "|".join([re.escape(e.lstrip(".")) for e in cls.AUDIO_EXTENSIONS])
        obs_p = re.compile(rf'!\[\[([^\]|]+?\.(?:{patt}))(?:\s*\|\s*([^\]]+))?\]\]', re.I)
        return obs_p.sub(lambda m: cls._render_local_audio_container(m.group(1).strip()), text)

    @classmethod
    def _resolve_markdown_audio(cls, text: str) -> str:
        patt = "|".join([re.escape(e.lstrip(".")) for e in cls.AUDIO_EXTENSIONS])
        md_p = re.compile(rf'!\[([^\]]*)\]\(([^)\s]+?\.(?:{patt}))(?:\s+["\'](.*?)["\'])?\)', re.I)
        return md_p.sub(lambda m: cls._render_local_audio_container(m.group(2).strip()), text)
