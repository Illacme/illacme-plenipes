# -*- coding: utf-8 -*-
"""
Illacme Plenipes - Rich Media Full Lifecycle Integration Test Suite
全面端到端验证原稿中携带图片、音频、视频时在四大生命周期阶段的稳定输出：
1. 多语言翻译与语义屏蔽阶段 (AI Translation & AST Masking)
2. 文档导出与出版装订阶段 (Bindery: EPUB, DOCX, WebBook, PDF)
3. 静态网站发布阶段 (SSG: Universal, Docusaurus, VitePress 等)
4. 社交媒体多渠道分发阶段 (Syndication: WeChat, Dev.to, Medium 等)
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""

import os
import tempfile
import pytest

from core.logic.ai.ai_logic_shards.ai_masker_ops import mask_block, unmask_block
from core.bindery.image_packager import ImagePackager
from core.adapters.egress.ssg.generic import GenericSSGAdapter
from core.adapters.egress.ssg.base_shards.ssg_link_healer import SSGLinkHealer
from core.editorial.ast_processor import MarkdownASTProcessor
from adapters.egress.syndication.wechat_shards.wechat_formatter import render_wechat_html
from adapters.egress.syndication.devto import DevToSyndicator


@pytest.fixture
def rich_media_manuscript():
    """提供覆盖图片、音频、本地视频与在线流媒体的全功能测试原稿"""
    return (
        "# 跨媒介主权出版典籍指南\n\n"
        "欢迎阅读本期多媒体专刊。请参阅 [[system-overview|系统全景]] 了解详情。\n\n"
        "## 一、核心架构图解\n"
        "![[architecture_diagram.png|800]]\n\n"
        "标准 Markdown 图片：\n"
        "![模块细节](assets/module_detail.jpg)\n\n"
        "## 二、原声有声书与技术访谈\n"
        "![[keynote_podcast.mp3]]\n"
        "录音副本：\n"
        "![发布会录音](assets/interview.wav)\n\n"
        "## 三、实机操作视频演示\n"
        "![[system_walkthrough.mp4|720]]\n\n"
        "宣传短片：\n"
        "![产品宣发](promo_trailer.webm)\n\n"
        "## 四、全球流媒体教程直连\n"
        "Bilibili 官方实战课：\n"
        "https://www.bilibili.com/video/BV1xx411c7mD\n\n"
        "YouTube 国际直播：\n"
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ\n"
    )


# ==============================================================================
# 阶段 1：多语言翻译阶段验证 (Translation & AI Masking)
# ==============================================================================

def test_translation_masking_and_unmasking_integrity(rich_media_manuscript):
    """验证多语言翻译过程中，所有媒体实体均被安全屏蔽并在翻译后 100% 完好无损还原"""
    masked_text, masks = mask_block(rich_media_manuscript, translate_labels=True)

    # 1. 断言所有多媒体语法均已被遮罩保护为 __B_MASK_X__
    assert "architecture_diagram.png" not in masked_text
    assert "keynote_podcast.mp3" not in masked_text
    assert "system_walkthrough.mp4" not in masked_text
    assert "BV1xx411c7mD" in masked_text or any("BV1xx411c7mD" in v for v in masks.values())

    # 2. 模拟大模型将中文翻译为英文 (技术占位符与掩码保持原样)
    mock_translated = masked_text.replace("跨媒介主权出版典籍指南", "Cross-Media Sovereign Publishing Guide")
    mock_translated = mock_translated.replace("核心架构图解", "Core Architecture Diagram")
    mock_translated = mock_translated.replace("原声有声书与技术访谈", "Original Audiobook and Interviews")
    mock_translated = mock_translated.replace("实机操作视频演示", "Hands-on Video Walkthrough")

    # 3. 执行解除护盾还原
    restored_text = unmask_block(mock_translated, masks)

    # 4. 断言所有富媒体路径与语法 100% 准确还原，零丢失、零路径篡改
    assert "![[architecture_diagram.png|800]]" in restored_text
    assert "![模块细节](assets/module_detail.jpg)" in restored_text
    assert "![[keynote_podcast.mp3]]" in restored_text
    assert "![发布会录音](assets/interview.wav)" in restored_text
    assert "![[system_walkthrough.mp4|720]]" in restored_text
    assert "![产品宣发](promo_trailer.webm)" in restored_text
    assert "Cross-Media Sovereign Publishing Guide" in restored_text


# ==============================================================================
# 阶段 2：文档与电子书导出排版验证 (Bindery: EPUB, DOCX, PDF)
# ==============================================================================

def test_bindery_media_transmutation_for_ebooks(rich_media_manuscript):
    """验证文档导出时，图片转换为 <img> 且音视频优雅降级为出版物媒体占位块"""
    healed_markdown = ImagePackager.heal_obsidian_embedded_images(rich_media_manuscript)

    # 1. 图片转译为标准 <img> 并附带宽度控制
    assert '<img src="architecture_diagram.png" alt="architecture_diagram" style="max-width: 800px;" />' in healed_markdown
    # 2. 音频优雅转译为有声出版物占位块
    assert '<div class="media-audio-placeholder"' in healed_markdown
    assert '🎵 <b>音频资源</b>: <code>keynote_podcast.mp3</code>' in healed_markdown
    # 3. 视频优雅转译为视频出版物占位块
    assert '<div class="media-video-placeholder"' in healed_markdown
    assert '🎬 <b>视频资源</b>: <code>system_walkthrough.mp4</code>' in healed_markdown
    # 4. 在线视频优雅转译为在线媒体占位块
    assert '🎬 <b>在线视频 (Bilibili)</b>: <code>BV1xx411c7mD</code>' in healed_markdown


def test_bindery_epub_compilation_with_rich_media(rich_media_manuscript):
    """验证 EPUB 电子书装订器处理富媒体内容不报异常，能够生成合规且内容完整的 EPUB 产物"""
    from core.adapters.egress.ebook.epub import EpubAdapter
    import zipfile
    adapter = EpubAdapter()

    healed_body = ImagePackager.heal_obsidian_embedded_images(rich_media_manuscript)
    meta = {"title": "多媒体技术专刊", "author": "测试团队", "language": "zh"}

    with tempfile.NamedTemporaryFile(suffix=".epub", delete=False) as tf:
        out_epub = tf.name

    try:
        manuscript_tree = [
            {
                "title": "第一章 多媒体演进",
                "html_body": f"<div>{healed_body}</div>",
                "assets": []
            }
        ]
        res = adapter.bind_book(manuscript_tree, meta, output_file_path=out_epub)
        assert res is True
        assert os.path.exists(out_epub)
        assert os.path.getsize(out_epub) > 0

        with zipfile.ZipFile(out_epub, "r") as zf:
            namelist = zf.namelist()
            assert "OEBPS/content.opf" in namelist
            assert "OEBPS/text/ch_1.xhtml" in namelist
            ch_content = zf.read("OEBPS/text/ch_1.xhtml").decode("utf-8")
            assert 'class="media-video-placeholder"' in ch_content
            assert 'class="media-audio-placeholder"' in ch_content
            assert '<img src="architecture_diagram.png"' in ch_content
    finally:
        if os.path.exists(out_epub):
            try: os.remove(out_epub)
            except Exception: pass


# ==============================================================================
# 阶段 3：静态网站发布阶段验证 (SSG: Universal, Docusaurus, VitePress 等)
# ==============================================================================

def test_ssg_universal_page_rendering_with_media(rich_media_manuscript):
    """验证 Universal SSG 适配器渲染出的 HTML 页面包含完整 HTML5 视频/音频与 iframe 播放器"""
    adapter = GenericSSGAdapter()
    fm = {"title": "多媒体技术展厅", "slug": "media-showcase", "layout": "docs"}

    html_page, out_fm = adapter.render(
        body=rich_media_manuscript,
        fm=fm,
        target_lang="zh",
        sub_path="docs/media-showcase.html"
    )

    # 1. HTML5 视频播放器验证
    assert '<div class="video-container local-video">' in html_page
    assert '<source src="system_walkthrough.mp4" type="video/mp4">' in html_page
    assert 'style="max-width: 720px;"' in html_page
    # 2. HTML5 音频播放器验证
    assert '<div class="audio-container local-audio">' in html_page
    assert '<source src="keynote_podcast.mp3" type="audio/mpeg">' in html_page
    assert '<audio controls preload="metadata">' in html_page
    # 3. Bilibili 响应式播放器验证
    assert '<div class="video-container responsive-video bilibili-embed">' in html_page
    assert 'bvid=BV1xx411c7mD' in html_page
    # 4. YouTube 响应式播放器验证
    assert '<div class="video-container responsive-video youtube-embed">' in html_page
    assert 'https://www.youtube-nocookie.com/embed/dQw4w9WgXcQ' in html_page
    # 5. 普通双链正常自愈为超链接
    assert '<a href="./system-overview.html" class="universal-link wikilink">系统全景</a>' in html_page


def test_ssg_link_healer_markdown_normalization_for_external_ssgs(rich_media_manuscript):
    """验证全系第三方 SSG (Docusaurus, VitePress 等) 在 LinkHealer 下的 Markdown 媒体自愈"""
    class MockDocusaurus:
        IS_CLEAN_URL = False
        def get_feature_slots(self): return {}

    adapter = MockDocusaurus()
    healed_md = SSGLinkHealer.normalize_markdown_content(adapter, rich_media_manuscript)

    # 1. 验证双链被规范化为通用相对链接
    assert "[系统全景](./system-overview.md)" in healed_md
    # 2. 验证多媒体标签被渲染为合法顶格 HTML 容器，消除 CommonMark 缩进陷阱
    assert '<div class="video-container local-video">' in healed_md
    assert '<div class="audio-container local-audio">' in healed_md
    assert '<div class="video-container responsive-video bilibili-embed">' in healed_md


# ==============================================================================
# 阶段 4：社媒渠道分发阶段验证 (Syndication: WeChat, Dev.to)
# ==============================================================================

def test_syndication_wechat_html_formatting(rich_media_manuscript):
    """验证微信公众号分发时，外链自动转脚注，媒体安全内联渲染，不产生非法异常"""
    formatted_html = render_wechat_html(rich_media_manuscript, {"convert_footnotes": True})

    # 1. 外部流媒体链接自动提取为脚注
    assert "参考资料" in formatted_html
    assert "https://www.bilibili.com/video/BV1xx411c7mD" in formatted_html
    assert "https://www.youtube.com/watch?v=dQw4w9WgXcQ" in formatted_html
    # 2. 正文外链附带角标
    assert '<sup style="color: #2563eb;' in formatted_html
    # 3. 页面注入了高保真内联排版样式容器
    assert '<section style="font-family:' in formatted_html


def test_syndication_devto_payload_formatting(rich_media_manuscript):
    """验证 Dev.to 国际社区分发时，富媒体内容正常包装且 Canonical URL 注入无误"""
    syndicator = DevToSyndicator({"published": True})
    metadata = {
        "tags": ["python", "media", "video"],
        "description": "富媒体出版全链路测试"
    }

    payload = syndicator.format_payload(
        title="跨媒介主权出版指南",
        slug="cross-media-guide",
        content=rich_media_manuscript,
        metadata=metadata,
        canonical_url="https://press.illacme.com/cross-media-guide"
    )

    art = payload["article"]
    assert art["title"] == "跨媒介主权出版指南"
    assert art["canonical_url"] == "https://press.illacme.com/cross-media-guide"
    assert "architecture_diagram.png" in art["body_markdown"]
    assert "keynote_podcast.mp3" in art["body_markdown"]
    assert "system_walkthrough.mp4" in art["body_markdown"]
