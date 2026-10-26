# -*- coding: utf-8 -*-
"""
Illacme Plenipes - Tests for Media & Video Syntax Resolver
测试富媒体与视频语法的解析、自愈与出版物降级保护。
"""

import pytest
from core.adapters.egress.ssg.base_shards.ssg_media_resolver import SSGMediaResolver
from core.adapters.egress.ssg.base_shards.ssg_link_healer import SSGLinkHealer
from core.bindery.image_packager import ImagePackager


class DummyAdapter:
    """Mock Adapter for Link Healer tests"""
    IS_CLEAN_URL = False

    def get_feature_slots(self):
        return {}


def test_obsidian_local_video_embedding():
    """测试 Obsidian 本地视频嵌入语法 ![[video.mp4]] 与尺寸自愈"""
    raw_md = (
        "## 本地视频演示\n\n"
        "![[demo.mp4]]\n\n"
        "带尺寸限制的视频：\n"
        "![[presentation.webm|640]]\n"
    )

    resolved = SSGMediaResolver.resolve_media_content(raw_md)

    assert '<div class="video-container local-video">' in resolved
    assert '<source src="demo.mp4" type="video/mp4">' in resolved
    assert '<source src="presentation.webm" type="video/webm">' in resolved
    assert 'style="max-width: 640px;"' in resolved
    assert 'controls preload="metadata"' in resolved


def test_markdown_local_video_embedding():
    """测试 Markdown 图像语法中的视频 ![alt](video.mov) 自愈"""
    raw_md = "![宣传片](assets/promo.mov)"
    resolved = SSGMediaResolver.resolve_media_content(raw_md)

    assert '<div class="video-container local-video">' in resolved
    assert '<source src="assets/promo.mov" type="video/quicktime">' in resolved


def test_bilibili_embedding_and_standalone():
    """测试 Bilibili 嵌入与独立行链接解析为响应式 16:9 播放器"""
    raw_md = (
        "观看 Bilibili 教学视频：\n\n"
        "https://www.bilibili.com/video/BV1xx411c7mD\n\n"
        "或者短链：\n"
        "https://b23.tv/BV1984y1Q7Yn\n\n"
        "或者内嵌语法：\n"
        "![[bilibili:BV1vW4y1F7wD]]\n"
    )

    resolved = SSGMediaResolver.resolve_media_content(raw_md)

    assert '<div class="video-container responsive-video bilibili-embed">' in resolved
    assert 'bvid=BV1xx411c7mD' in resolved
    assert 'bvid=BV1984y1Q7Yn' in resolved
    assert 'bvid=BV1vW4y1F7wD' in resolved
    assert 'allowfullscreen="true"' in resolved


def test_youtube_embedding_and_standalone():
    """测试 YouTube 嵌入与独立行链接解析为响应式 16:9 播放器"""
    raw_md = (
        "Watch YouTube tutorial:\n\n"
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ\n\n"
        "Short link:\n"
        "https://youtu.be/dQw4w9WgXcQ\n\n"
        "Embed syntax:\n"
        "![[youtube:dQw4w9WgXcQ]]\n"
    )

    resolved = SSGMediaResolver.resolve_media_content(raw_md)

    assert '<div class="video-container responsive-video youtube-embed">' in resolved
    assert 'https://www.youtube-nocookie.com/embed/dQw4w9WgXcQ' in resolved
    assert 'allow="accelerometer; autoplay; clipboard-write; encrypted-media' in resolved


def test_code_block_protection():
    """测试代码块与行内代码受严格保护，不被误转换为视频播放器"""
    raw_md = (
        "以下是代码示例：\n\n"
        "```markdown\n"
        "https://www.bilibili.com/video/BV1xx411c7mD\n"
        "![[video.mp4]]\n"
        "```\n\n"
        "行内代码：`https://youtu.be/dQw4w9WgXcQ` 不应受影响。\n\n"
        "而正文中的独立链接：\n"
        "https://www.bilibili.com/video/BV1xx411c7mD\n"
    )

    resolved = SSGMediaResolver.resolve_media_content(raw_md)

    # 代码块中必须原样保留
    assert "```markdown\nhttps://www.bilibili.com/video/BV1xx411c7mD\n![[video.mp4]]\n```" in resolved
    assert "`https://youtu.be/dQw4w9WgXcQ`" in resolved
    # 正文中的独立链接被解析为 iframe
    assert 'bvid=BV1xx411c7mD' in resolved
    assert '<iframe' in resolved


def test_ssg_link_healer_integration():
    """测试 SSGLinkHealer 对普通双链与视频语法的共存处理"""
    adapter = DummyAdapter()
    raw_md = (
        "欢迎访问 [[quick-start|快速入门]] 页面。\n\n"
        "![[tutorial.mp4|800]]\n"
    )

    healed = SSGLinkHealer.normalize_markdown_content(adapter, raw_md)

    # 普通双链被解析为相对链接
    assert "[快速入门](./quick-start.md)" in healed
    # 视频被解析为视频容器
    assert '<div class="video-container local-video">' in healed
    assert '<source src="tutorial.mp4" type="video/mp4">' in healed
    assert 'style="max-width: 800px;"' in healed


def test_bindery_image_packager_video_fallback():
    """测试 Bindery 电子书对视频语法的排版占位降级"""
    raw_md = (
        "电子书正文\n\n"
        "![[architecture.png]]\n\n"
        "![[lecture_demo.mp4]]\n\n"
        "![[bilibili:BV1xx411c7mD]]\n"
    )

    healed = ImagePackager.heal_obsidian_embedded_images(raw_md)

    # 图片正常转译为 <img> 标签
    assert '<img src="architecture.png" alt="architecture" />' in healed
    # 本地视频优雅转译为出版物媒体占位块
    assert '<div class="media-video-placeholder"' in healed
    assert '🎬 <b>视频资源</b>: <code>lecture_demo.mp4</code>' in healed
    # 在线视频优雅转译为在线视频占位块
    assert '🎬 <b>在线视频 (Bilibili)</b>: <code>BV1xx411c7mD</code>' in healed


def test_obsidian_and_markdown_audio_embedding():
    """测试 Obsidian 与 Markdown 本地音频嵌入语法"""
    raw_md = (
        "## 音频节目\n\n"
        "![[podcast_ep01.mp3]]\n\n"
        "![配乐](soundtrack.wav)\n"
    )

    resolved = SSGMediaResolver.resolve_media_content(raw_md)

    assert '<div class="audio-container local-audio">' in resolved
    assert '<source src="podcast_ep01.mp3" type="audio/mpeg">' in resolved
    assert '<source src="soundtrack.wav" type="audio/wav">' in resolved
    assert '<audio controls preload="metadata">' in resolved


def test_bindery_image_packager_audio_fallback():
    """测试 Bindery 电子书对音频语法的排版占位降级"""
    raw_md = "![[interview_record.mp3]]"
    healed = ImagePackager.heal_obsidian_embedded_images(raw_md)

    assert '<div class="media-audio-placeholder"' in healed
    assert '🎵 <b>音频资源</b>: <code>interview_record.mp3</code>' in healed


def test_additional_rich_media_platforms():
    """测试 Vimeo、腾讯视频、网易云音乐、Spotify、CodePen 的全语法嵌入"""
    raw_md = (
        "Vimeo 视频：\nhttps://vimeo.com/98765432\n\n"
        "腾讯视频：\nhttps://v.qq.com/x/cover/mzc00200/u00431234.html\n\n"
        "网易云音乐：\nhttps://music.163.com/#/song?id=654321\n\n"
        "Spotify 播放：\nhttps://open.spotify.com/track/3n3Ppam7vgaVa1iaRUc9Lp\n\n"
        "CodePen 沙盒：\nhttps://codepen.io/geoffgraham/pen/dyGaZq\n"
    )

    resolved = SSGMediaResolver.resolve_media_content(raw_md)

    assert '<div class="video-container responsive-video vimeo-embed"' in resolved
    assert 'player.vimeo.com/video/98765432' in resolved

    assert '<div class="video-container responsive-video qq-video-embed"' in resolved
    assert 'v.qq.com/txp/iframe/player.html?vid=u00431234' in resolved

    assert '<div class="audio-container netease-music-embed"' in resolved
    assert 'music.163.com/outchain/player?type=2&id=654321' in resolved

    assert '<div class="audio-container spotify-embed"' in resolved
    assert 'open.spotify.com/embed/track/3n3Ppam7vgaVa1iaRUc9Lp' in resolved

    assert '<div class="embed-container codepen-embed"' in resolved
    assert 'codepen.io/geoffgraham/embed/dyGaZq' in resolved


def test_media_resolver_query_parameters():
    """测试多媒体解析对 B站分P 与 YouTube 起始时间戳的透传"""
    raw_md = (
        "B站多P教程：\n"
        "https://www.bilibili.com/video/BV1xx411c7mD?p=3\n\n"
        "YouTube 进度视频：\n"
        "https://youtu.be/dQw4w9WgXcQ?t=150s\n"
    )

    resolved = SSGMediaResolver.resolve_media_content(raw_md)

    # 验证 B 站分 P 透传
    assert "player.bilibili.com/player.html?bvid=BV1xx411c7mD&page=3" in resolved
    # 验证 YouTube 起始时间戳透传
    assert "youtube-nocookie.com/embed/dQw4w9WgXcQ?start=150" in resolved



