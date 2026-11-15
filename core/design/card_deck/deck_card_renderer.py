# -*- coding: utf-8 -*-
"""
🎨 CardDeck Core - Multi-Ratio High-Aesthetic Card Renderer
职责：基于 Pillow 渲染具备赛博极光、毛玻璃拟态质感的多画幅社交卡片海报 (3:4 竖屏 / 1:1 方形 / 16:9 宽屏)。
特性：
1. 原生支持 3:4 (900x1200), 1:1 (1080x1080), 16:9 (1200x675)；
2. 弹性比例因子 (scale)，字号与边距自适应不同画幅；
3. 状态栏顶部进度槽：[分类/品牌] 与 [02 / 05] 页码指示；
4. 动态多态排版：针对 Cover（封面）、Content（要点切片）、Closing（收束总结）专项布局；
🛡️ [SOP-01] 物理行数严格保持在 300 行以内。
"""

import io
from typing import Optional, List
from PIL import Image, ImageDraw, ImageFont

from core.design.cover_engine.og_card_renderer import (
    _get_best_font,
    _clean_text_for_rendering,
    _wrap_text_to_lines,
    _render_aurora_background,
    AURORA_PALETTES
)
from .deck_segmenter import DeckCardData

CARD_DIMENSION_MAP = {
    "3:4": (900, 1200),
    "1:1": (1080, 1080),
    "16:9": (1200, 675),
}


def render_deck_card(data: DeckCardData, offset: int = 0, aspect_ratio: str = "3:4") -> bytes:
    """根据指定画幅比例 (3:4, 1:1, 16:9) 将 DeckCardData 渲染为高清 JPEG 图片"""
    clean_ratio = str(aspect_ratio or "3:4").strip().lower()
    width, height = CARD_DIMENSION_MAP.get(clean_ratio, (900, 1200))
    scale = max(0.55, min(1.15, height / 1200.0))

    # 1. 渲染极光弥散与科技微点阵底板
    img, accent_color = _render_aurora_background(width, height, offset=offset)

    # 2. 毛玻璃主卡片容器
    margin_x = int(width * 0.05)
    margin_y = int(height * 0.045)
    card_w = width - margin_x * 2
    card_h = height - margin_y * 2
    radius = int(20 * scale)

    panel = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    p_draw = ImageDraw.Draw(panel)
    p_draw.rounded_rectangle(
        [margin_x, margin_y, margin_x + card_w, margin_y + card_h],
        radius=radius,
        fill=(10, 15, 29, 185),
        outline=(255, 255, 255, 32),
        width=1
    )
    p_draw.line([margin_x + radius, margin_y, margin_x + card_w - radius, margin_y], fill=accent_color, width=2)
    p_draw.line([margin_x + 14, margin_y + 14, margin_x + 36, margin_y + 14], fill=accent_color, width=3)
    p_draw.line([margin_x + 14, margin_y + 14, margin_x + 14, margin_y + 36], fill=accent_color, width=3)

    img.paste(panel, (0, 0), panel)
    draw = ImageDraw.Draw(img)

    # 3. 顶部 Header 状态栏
    _render_header(draw, data, margin_x, margin_y, card_w, accent_color, scale)

    # 4. 根据卡片类型分流渲染主体内容
    if data.card_type == "cover":
        _render_cover_body(draw, data, margin_x, margin_y, card_w, card_h, accent_color, scale)
    elif data.card_type == "closing":
        _render_closing_body(draw, data, margin_x, margin_y, card_w, card_h, accent_color, scale)
    else:
        _render_content_body(draw, data, margin_x, margin_y, card_w, card_h, accent_color, scale)

    # 5. 底部 Footer 栏
    _render_footer(draw, data, margin_x, margin_y, card_w, card_h, accent_color, scale)

    # 6. 保存导出为高品质 JPEG
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=92)
    return buf.getvalue()


def _render_header(draw: ImageDraw.ImageDraw, data: DeckCardData, mx: int, my: int, cw: int, accent: tuple, scale: float):
    hdr_font = _get_best_font(int(24 * scale))
    brand_text = f"{str(data.brand_name).upper()[:16]} · {data.category[:10]}"
    px, py = mx + int(32 * scale), my + int(32 * scale)

    badge_w = int(280 * scale)
    badge_h = int(36 * scale)
    draw.rounded_rectangle([px - 8, py - 4, px + badge_w, py + badge_h], radius=6, fill=(16, 24, 44), outline=(255, 255, 255, 24), width=1)
    draw.ellipse([px, py + int(8 * scale), px + int(8 * scale), py + int(16 * scale)], fill=accent)
    draw.text((px + int(16 * scale), py + 2), brand_text, fill=(226, 232, 240), font=hdr_font)

    page_text = f"{data.index:02d} / {data.total:02d}"
    pg_bbox = draw.textbbox((0, 0), page_text, font=hdr_font)
    pg_w = pg_bbox[2] - pg_bbox[0]
    pg_x = mx + cw - pg_w - int(44 * scale)
    draw.rounded_rectangle([pg_x - 10, py - 4, pg_x + pg_w + 10, py + badge_h], radius=6, fill=(16, 24, 44), outline=accent, width=1)
    draw.text((pg_x, py + 2), page_text, fill=accent, font=hdr_font)


def _render_cover_body(draw: ImageDraw.ImageDraw, data: DeckCardData, mx: int, my: int, cw: int, ch: int, accent: tuple, scale: float):
    title_font = _get_best_font(int(54 * scale))
    title_text = _clean_text_for_rendering(data.title)
    lines = _wrap_text_to_lines(draw, title_text, title_font, max_width=cw - int(100 * scale), max_lines=2 if scale < 0.8 else 3)

    line_h = int(74 * scale)
    start_y = my + int(140 * scale)
    for i, line in enumerate(lines):
        ly = start_y + i * line_h
        draw.text((mx + int(46 * scale), ly + 3), line, fill=(0, 0, 0, 200), font=title_font)
        draw.text((mx + int(44 * scale), ly), line, fill=(255, 255, 255), font=title_font)

    sub_y = start_y + len(lines) * line_h + int(40 * scale)
    sub_font = _get_best_font(int(26 * scale))
    sub_lines = _wrap_text_to_lines(draw, data.subtitle or "一文读懂核心精要", sub_font, max_width=cw - int(160 * scale), max_lines=2 if scale < 0.8 else 3)
    card_h = max(int(100 * scale), len(sub_lines) * int(38 * scale) + int(40 * scale))

    draw.rounded_rectangle([mx + int(40 * scale), sub_y, mx + cw - int(40 * scale), sub_y + card_h], radius=10, fill=(15, 23, 42, 210), outline=(255, 255, 255, 20), width=1)
    draw.line([mx + int(40 * scale), sub_y + 10, mx + int(40 * scale), sub_y + card_h - 10], fill=accent, width=4)
    for j, s_line in enumerate(sub_lines):
        draw.text((mx + int(65 * scale), sub_y + int(20 * scale) + j * int(38 * scale)), s_line, fill=(203, 213, 225), font=sub_font)

    guide_y = my + ch - int(140 * scale)
    draw.rounded_rectangle([mx + int(45 * scale), guide_y, mx + cw - int(45 * scale), guide_y + int(56 * scale)], radius=28, fill=(24, 34, 60), outline=accent, width=1)
    g_font = _get_best_font(int(22 * scale))
    draw.text((mx + int(90 * scale), guide_y + int(15 * scale)), "👉 左右滑动查看卡片详解 · 持续更新硬核干货", fill=(241, 245, 249), font=g_font)


def _render_content_body(draw: ImageDraw.ImageDraw, data: DeckCardData, mx: int, my: int, cw: int, ch: int, accent: tuple, scale: float):
    title_font = _get_best_font(int(42 * scale))
    clean_title = _clean_text_for_rendering(data.title)
    t_lines = _wrap_text_to_lines(draw, clean_title, title_font, max_width=cw - int(100 * scale), max_lines=2)

    start_y = my + int(115 * scale)
    for i, line in enumerate(t_lines):
        draw.text((mx + int(44 * scale), start_y + i * int(56 * scale)), line, fill=(255, 255, 255), font=title_font)

    curr_y = start_y + len(t_lines) * int(56 * scale) + int(28 * scale)

    if data.quote:
        q_font = _get_best_font(int(24 * scale))
        q_lines = _wrap_text_to_lines(draw, f"“ {data.quote} ”", q_font, max_width=cw - int(160 * scale), max_lines=2)
        q_h = len(q_lines) * int(36 * scale) + int(30 * scale)
        draw.rounded_rectangle([mx + int(40 * scale), curr_y, mx + cw - int(40 * scale), curr_y + q_h], radius=8, fill=(20, 28, 48), outline=(255, 255, 255, 18), width=1)
        draw.line([mx + int(40 * scale), curr_y + 6, mx + int(40 * scale), curr_y + q_h - 6], fill=accent, width=3)
        for qi, ql in enumerate(q_lines):
            draw.text((mx + int(60 * scale), curr_y + int(14 * scale) + qi * int(36 * scale)), ql, fill=(248, 250, 252), font=q_font)
        curr_y += q_h + int(22 * scale)

    if data.points:
        p_font = _get_best_font(int(25 * scale))
        max_pts = 2 if scale < 0.75 else 4
        for p_idx, pt in enumerate(data.points[:max_pts], start=1):
            pt_lines = _wrap_text_to_lines(draw, pt, p_font, max_width=cw - int(200 * scale), max_lines=2)
            item_h = max(int(64 * scale), len(pt_lines) * int(34 * scale) + int(30 * scale))
            draw.rounded_rectangle([mx + int(40 * scale), curr_y, mx + cw - int(40 * scale), curr_y + item_h], radius=8, fill=(15, 23, 42, 190), outline=(255, 255, 255, 16), width=1)
            draw.rounded_rectangle([mx + int(52 * scale), curr_y + int(14 * scale), mx + int(90 * scale), curr_y + int(46 * scale)], radius=4, fill=(30, 41, 59), outline=accent, width=1)
            draw.text((mx + int(58 * scale), curr_y + int(18 * scale)), f"{p_idx:02d}", fill=accent, font=_get_best_font(int(18 * scale)))
            for li, line in enumerate(pt_lines):
                draw.text((mx + int(106 * scale), curr_y + int(14 * scale) + li * int(34 * scale)), line, fill=(226, 232, 240), font=p_font)
            curr_y += item_h + int(16 * scale)


def _render_closing_body(draw: ImageDraw.ImageDraw, data: DeckCardData, mx: int, my: int, cw: int, ch: int, accent: tuple, scale: float):
    title_font = _get_best_font(int(44 * scale))
    draw.text((mx + int(44 * scale), my + int(120 * scale)), data.title or "核心总结 · 记忆速记", fill=(255, 255, 255), font=title_font)

    curr_y = my + int(195 * scale)
    p_font = _get_best_font(int(24 * scale))
    max_pts = 2 if scale < 0.75 else 3
    for p_idx, pt in enumerate(data.points[:max_pts], start=1):
        pt_lines = _wrap_text_to_lines(draw, pt, p_font, max_width=cw - int(160 * scale), max_lines=2)
        item_h = max(int(60 * scale), len(pt_lines) * int(34 * scale) + int(24 * scale))
        draw.rounded_rectangle([mx + int(40 * scale), curr_y, mx + cw - int(40 * scale), curr_y + item_h], radius=8, fill=(18, 26, 46), outline=(255, 255, 255, 18), width=1)
        draw.text((mx + int(60 * scale), curr_y + int(14 * scale)), "✓", fill=accent, font=_get_best_font(int(22 * scale)))
        for li, line in enumerate(pt_lines):
            draw.text((mx + int(98 * scale), curr_y + int(12 * scale) + li * int(34 * scale)), line, fill=(241, 245, 249), font=p_font)
        curr_y += item_h + int(18 * scale)

    cta_y = my + ch - int(180 * scale)
    draw.rounded_rectangle([mx + int(40 * scale), cta_y, mx + cw - int(40 * scale), cta_y + int(95 * scale)], radius=12, fill=(15, 23, 42, 230), outline=accent, width=1)
    draw.text((mx + int(70 * scale), cta_y + int(20 * scale)), "💡 持续输出高质量深度原创与架构洞察", fill=(255, 255, 255), font=_get_best_font(int(24 * scale)))
    draw.text((mx + int(70 * scale), cta_y + int(56 * scale)), "点赞 · 收藏 · 关注，不错过每一次技术进阶", fill=(148, 163, 184), font=_get_best_font(int(20 * scale)))


def _render_footer(draw: ImageDraw.ImageDraw, data: DeckCardData, mx: int, my: int, cw: int, ch: int, accent: tuple, scale: float):
    divider_y = my + ch - int(56 * scale)
    draw.line([mx + int(36 * scale), divider_y, mx + cw - int(36 * scale), divider_y], fill=(255, 255, 255, 20), width=1)
    f_font = _get_best_font(int(19 * scale))
    draw.text((mx + int(44 * scale), divider_y + int(16 * scale)), f"AUTHOR: {str(data.author).upper()[:20]}", fill=(148, 163, 184), font=f_font)
    wm_text = "SOVEREIGN KNOWLEDGE DECK"
    wm_bbox = draw.textbbox((0, 0), wm_text, font=f_font)
    wm_w = wm_bbox[2] - wm_bbox[0]
    draw.text((mx + cw - wm_w - int(44 * scale), divider_y + int(16 * scale)), wm_text, fill=(129, 140, 248), font=f_font)
