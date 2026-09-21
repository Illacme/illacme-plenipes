# -*- coding: utf-8 -*-
"""
🧪 [V125.0] Test Cover Generator & Discovery Logic
验证原生文库封面探测、SVG 排版封面生成、风格切换与 DataURL 输出。
"""

import os
import tempfile
import pytest
from core.bindery.cover_generator import CoverGenerator, COVER_STYLES


def test_cover_styles_matrix():
    """验证预设装帧风格矩阵完整性"""
    assert "dark_emerald" in COVER_STYLES
    assert "classic_navy" in COVER_STYLES
    assert "obsidian_gold" in COVER_STYLES
    for k, v in COVER_STYLES.items():
        assert "accent" in v
        assert "bg_top" in v
        assert "border" in v


def test_discover_cover_priority():
    """验证多级自愈探测原生封面"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # 空目录探测为 None
        assert CoverGenerator.discover_cover(tmpdir, "docs") is None

        # 写入全局 assets/cover.png
        assets_dir = os.path.join(tmpdir, "assets")
        os.makedirs(assets_dir, exist_ok=True)
        global_cover = os.path.join(assets_dir, "cover.png")
        with open(global_cover, "wb") as f:
            f.write(b"FAKE_PNG_HEADER")

        found = CoverGenerator.discover_cover(tmpdir, "docs")
        assert found == os.path.abspath(global_cover)

        # 写入栏目特定 cover.jpg，应优先命中
        cat_dir = os.path.join(tmpdir, "docs")
        os.makedirs(cat_dir, exist_ok=True)
        cat_cover = os.path.join(cat_dir, "cover.jpg")
        with open(cat_cover, "wb") as f:
            f.write(b"FAKE_JPG_HEADER")

        found_cat = CoverGenerator.discover_cover(tmpdir, "docs")
        assert found_cat == os.path.abspath(cat_cover)


def test_discover_cover_from_chapters_frontmatter():
    """验证章节 frontmatter 显式声明封面提取"""
    with tempfile.TemporaryDirectory() as tmpdir:
        img_p = os.path.join(tmpdir, "my_art.jpg")
        with open(img_p, "wb") as f:
            f.write(b"FAKE_IMAGE")

        chapters = [
            {"frontmatter": {"title": "Hello"}},
            {"frontmatter": {"title": "World", "cover": "my_art.jpg"}}
        ]
        found = CoverGenerator.discover_cover(tmpdir, chapters=chapters)
        assert found == os.path.abspath(img_p)


def test_generate_svg_cover_and_data_uri():
    """验证 SVG 排版封面生成与 DataURL 输出"""
    svg = CoverGenerator.generate_svg_cover(
        title="深度解析系统架构与工程治理",
        author="Eason & Illacme Team",
        publisher="Illacme Press",
        style_key="obsidian_gold",
        lang="zh"
    )
    assert "<svg" in svg
    assert "深度解析系统架构" in svg
    assert "程治理" in svg
    assert "Eason &amp; Illacme Team" in svg
    assert COVER_STYLES["obsidian_gold"]["accent"] in svg

    data_uri = CoverGenerator.generate_cover_data_uri(
        title="测试作品",
        author="作者",
        style_key="dark_emerald"
    )
    assert data_uri.startswith("data:image/svg+xml;base64,")


def test_render_cover_image_file():
    """验证封面光栅化落盘"""
    with tempfile.TemporaryDirectory() as tmpdir:
        out_p = os.path.join(tmpdir, "rendered_cover.png")
        saved = CoverGenerator.render_cover_image(
            output_path=out_p,
            title="落盘测试全集",
            author="测试署名",
            style_key="classic_navy"
        )
        assert os.path.exists(saved)
        assert os.path.getsize(saved) > 0
