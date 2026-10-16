# -*- coding: utf-8 -*-
"""
🧪 [V126.0] Test Local OG Provider Prompt Sanitization & Defensive Typography
验证本地 OG 技术卡片引擎面对 AI 提示词与长文本时的防御性清洗与标题提取。
"""

from core.design.providers.local_og_provider import LocalOGProvider


def test_sanitize_prompt_extracts_book_title():
    """验证从文章《...》模式中提取纯净标题"""
    prompt = "文章《多语言矩阵与内容治理实战》：多语言矩阵与内容治理实战。极简现代科技意境，电影级光影构图，8k 高清细节，现代装帧质感"
    title = LocalOGProvider.sanitize_prompt_for_title(prompt)
    assert title == "多语言矩阵与内容治理实战"


def test_sanitize_prompt_extracts_creative_prefix():
    """验证从为文章《xxx》创作模式中提取纯净标题"""
    prompt = "为文章《核心特性与设计哲学》创作科技现代风格封面，视觉震撼，极简光影，高分辨率，富有未来感"
    title = LocalOGProvider.sanitize_prompt_for_title(prompt)
    assert title == "核心特性与设计哲学"


def test_sanitize_prompt_strips_ai_noise():
    """验证剔除 AI 生图修饰词缀"""
    prompt = "分布式全域流控架构实战，极简科技意境，电影级光影，8k高清细节"
    title = LocalOGProvider.sanitize_prompt_for_title(prompt)
    assert title == "分布式全域流控架构实战"


def test_sanitize_prompt_fallback_on_empty():
    """验证空提示词优雅保底"""
    assert LocalOGProvider.sanitize_prompt_for_title("") == "Illacme Plenipes 技术出版"
    assert LocalOGProvider.sanitize_prompt_for_title("   ") == "Illacme Plenipes 技术出版"
    assert LocalOGProvider.sanitize_prompt_for_title(None) == "Illacme Plenipes 技术出版"


def test_local_og_provider_generates_image_safely():
    """验证防御性清洗后成功生成 OG 技术卡片二进制数据"""
    provider = LocalOGProvider()
    dirty_prompt = "文章《自动化测试与架构合规》：系统治理方案。极简现代科技意境，8k 高清"
    data, err = provider.generate_image(dirty_prompt, aspect_ratio="16:9")
    assert err is None
    assert data is not None
    assert len(data) > 100


def test_local_og_provider_supports_palette_offset():
    """验证通过 offset 参数实现 8 大极光配色轮巡相移"""
    import hashlib
    provider = LocalOGProvider()
    data1, _ = provider.generate_image("架构设计与模式", offset=0)
    data2, _ = provider.generate_image("架构设计与模式", offset=1)
    assert hashlib.md5(data1).hexdigest() != hashlib.md5(data2).hexdigest()
