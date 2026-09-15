# -*- coding: utf-8 -*-
"""
🎨 CoverEngine Shard - Minimalist Typographic Badge Renderer
职责：极简首字 / 单字符徽章式排版渲染器 (对标 Notion / GitLab / Slack 默认徽章)。
特性：
1. 提取标题首字符 (中文汉字、英文字母或核心数字)；
2. 基于字符哈希在 HSL 色环上生成高雅深色底板与高对比度荧光互补徽标；
3. 适合技术参考手册、API 规格文档与极简主义出版风格；
🛡️ [SOP-01] 物理行数保持在 300 行以内。
"""

import io
import colorsys
import hashlib
from PIL import Image, ImageDraw, ImageFont
from core.design.cover_engine.og_card_renderer import _get_best_font, _clean_text_for_rendering

def _get_char_colors(text: str, offset: int = 0) -> tuple:
    """根据文字哈希与偏移量计算 HSL 高饱和度对比色与暗黑底色，支持换一张色彩轮巡"""
    seed_hash = int(hashlib.md5(text.encode("utf-8")).hexdigest()[:6], 16)
    hue = ((seed_hash + offset * 45) % 360) / 360.0
    
    # 荧光徽标色 (高饱和度、高亮度)
    r, g, b = colorsys.hsv_to_rgb(hue, 0.75, 0.98)
    fg_color = (int(r * 255), int(g * 255), int(b * 255))
    
    # 极深暗黑底色 (低亮度、微弱同色相)
    br, bg, bb = colorsys.hsv_to_rgb(hue, 0.45, 0.12)
    bg_color = (int(br * 255), int(bg * 255), int(bb * 255))
    
    return bg_color, fg_color

def render_minimal_badge(
    title: str,
    brand_name: str = "ILLACME",
    width: int = 1200,
    height: int = 675,
    aspect_ratio: str = "16:9",
    offset: int = 0
) -> bytes:
    """渲染极简首字徽章封面卡片"""
    if aspect_ratio in ("2.35:1", "wechat"):
        width, height = 900, 383
    elif aspect_ratio in ("3:4", "portrait"):
        width, height = 900, 1200
    elif aspect_ratio in ("1:1", "square"):
        width, height = 900, 900

    clean_t = _clean_text_for_rendering(title or "Publication")
    
    # 提取首字（优先跳过开头的特殊标点与 Emoji）
    primary_char = "P"
    for ch in clean_t:
        if ch.isalnum() or '\u4e00' <= ch <= '\u9fff':
            primary_char = ch
            break

    bg_color, fg_color = _get_char_colors(clean_t, offset=offset)

    img = Image.new("RGB", (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)

    cx, cy = width // 2, height // 2
    badge_radius = int(min(width, height) * 0.28)

    # 1. 绘制中央外围极细双圆环
    draw.ellipse(
        [cx - badge_radius, cy - badge_radius, cx + badge_radius, cy + badge_radius],
        outline=fg_color,
        width=2
    )
    inner_r = badge_radius - 8
    draw.ellipse(
        [cx - inner_r, cy - inner_r, cx + inner_r, cy + inner_r],
        outline=(fg_color[0], fg_color[1], fg_color[2], 80),
        width=1
    )

    # 2. 绘制中央巨幅单字符
    char_font_size = int(badge_radius * 1.1)
    char_font = _get_best_font(char_font_size)
    
    bbox = draw.textbbox((0, 0), primary_char, font=char_font)
    char_w = bbox[2] - bbox[0]
    char_h = bbox[3] - bbox[1]
    
    # 视觉几何居中补偿
    draw.text((cx - char_w // 2, cy - char_h // 2 - bbox[1]), primary_char, fill=fg_color, font=char_font)

    # 3. 底部极简品牌徽标
    meta_font = _get_best_font(int(height * 0.032))
    meta_text = f"• {str(brand_name).upper()} SPECIFICATION •"
    m_bbox = draw.textbbox((0, 0), meta_text, font=meta_font)
    m_w = m_bbox[2] - m_bbox[0]
    draw.text((cx - m_w // 2, height - int(height * 0.12)), meta_text, fill=(180, 190, 205), font=meta_font)

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=92)
    return buf.getvalue()
