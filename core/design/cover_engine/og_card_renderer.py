# -*- coding: utf-8 -*-
"""
🎨 CoverEngine Shard - Modern Cyber OG Card Renderer (V2.0 High Aesthetic)
职责：基于 Pillow 渲染具备极光弥散发光、科技微网格与毛玻璃拟态质感的高级 OG 封面卡片。
特性：
1. 柔和极光光斑 (Aurora Mesh Glow: Cyan & Purple 双重径向柔光衰减)；
2. 科技微等距点阵网格 (Tech Dot Grid)；
3. 现代圆角毛玻璃卡片内衬与顶边缘光反射 (Glass Container)；
4. 黄金 60% 中央安全区弹性排版，自适应双行折行与抗锯齿保护；
🛡️ [SOP-01] 物理行数严格保持在 300 行以内。
"""

import os
import io
import math
from typing import Optional, Tuple, List
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FONT_CANDIDATES = [
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/Library/Fonts/Arial Unicode.ttf",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
    "C:\\Windows\\Fonts\\msyh.ttc",
    "C:\\Windows\\Fonts\\simhei.ttf"
]

def _get_best_font(size: int) -> ImageFont.ImageFont:
    """自愈加载可用无衬线字体，优先粗体现代字形"""
    for font_path in FONT_CANDIDATES:
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, size)
            except Exception:
                continue
    try:
        return ImageFont.load_default()
    except Exception:
        return None

def _clean_text_for_rendering(text: str) -> str:
    if not text:
        return ""
    return " ".join(str(text).split())

def _wrap_text_to_lines(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int, max_lines: int = 2) -> List[str]:
    words = list(text)
    lines, curr = [], ""
    for char in words:
        test = curr + char
        bbox = draw.textbbox((0, 0), test, font=font)
        w = bbox[2] - bbox[0]
        if w > max_width and curr:
            lines.append(curr)
            curr = char
            if len(lines) >= max_lines:
                break
        else:
            curr = test
    if curr and len(lines) < max_lines:
        lines.append(curr)
    if len(lines) == max_lines:
        last_line = lines[-1]
        test_ellipsis = last_line + "..."
        while draw.textbbox((0, 0), test_ellipsis, font=font)[2] > max_width and len(last_line) > 1:
            last_line = last_line[:-1]
            test_ellipsis = last_line + "..."
        lines[-1] = test_ellipsis
    return lines

AURORA_PALETTES = [
    ((0, 242, 254, 75), (124, 58, 237, 70), (0, 242, 254, 200)),   # 0: 赛博青 + 霓虹紫
    ((16, 185, 129, 75), (59, 130, 246, 70), (16, 185, 129, 200)),   # 1: 翡翠绿 + 深海蓝
    ((245, 158, 11, 75), (239, 68, 68, 70), (245, 158, 11, 200)),    # 2: 日落金 + 炽热红
    ((56, 189, 248, 75), (224, 231, 255, 60), (56, 189, 248, 200)),  # 3: 冰川蓝 + 钛白冷月
    ((236, 72, 153, 75), (139, 92, 246, 70), (236, 72, 153, 200)),  # 4: 幻彩星云 + 魅惑洋红
    ((251, 146, 60, 75), (79, 70, 229, 70), (251, 146, 60, 200)),    # 5: 琥珀流光 + 曜石深紫
    ((132, 204, 22, 75), (6, 182, 212, 70), (132, 204, 22, 200)),    # 6: 矩阵涌动 + 电光石灰
    ((99, 102, 241, 75), (244, 114, 182, 70), (99, 102, 241, 200))   # 7: 幽蓝深空 + 极光幽粉
]

def _render_aurora_background(w: int, h: int, offset: int = 0) -> tuple[Image.Image, tuple]:
    """渲染深邃星空底板与赛博双极光弥散发光光斑，支持 8 档配色相移"""
    base = Image.new("RGB", (w, h), color=(7, 10, 19))
    draw_base = ImageDraw.Draw(base)
    for y in range(h):
        factor = y / float(h)
        r = int(8 * (1 - factor) + 4 * factor)
        g = int(14 * (1 - factor) + 7 * factor)
        b = int(28 * (1 - factor) + 14 * factor)
        draw_base.line([(0, y), (w, y)], fill=(r, g, b))

    palette = AURORA_PALETTES[offset % len(AURORA_PALETTES)]
    prim_color, sec_color, accent_color = palette

    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    cyan_cx, cyan_cy = int(w * 0.82), int(h * 0.18)
    cyan_rx, cyan_ry = int(w * 0.38), int(h * 0.42)
    glow_draw.ellipse([cyan_cx - cyan_rx, cyan_cy - cyan_ry, cyan_cx + cyan_rx, cyan_cy + cyan_ry], fill=prim_color)

    purple_cx, purple_cy = int(w * 0.16), int(h * 0.84)
    purple_rx, purple_ry = int(w * 0.35), int(h * 0.40)
    glow_draw.ellipse([purple_cx - purple_rx, purple_cy - purple_ry, purple_cx + purple_rx, purple_cy + purple_ry], fill=sec_color)

    glow = glow.filter(ImageFilter.GaussianBlur(radius=int(w * 0.08)))
    base.paste(glow, (0, 0), glow)

    grid_overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    grid_draw = ImageDraw.Draw(grid_overlay)
    grid_step = 36
    dot_fill = (255, 255, 255, 22)
    for gx in range(grid_step // 2, w, grid_step):
        for gy in range(grid_step // 2, h, grid_step):
            grid_draw.rectangle([gx, gy, gx + 1, gy + 1], fill=dot_fill)
    base.paste(grid_overlay, (0, 0), grid_overlay)

    return base, accent_color

def render_og_card(
    title: str,
    author: str = "Illacme Plenipes",
    category: str = "Engineering",
    brand_name: str = "ILLACME SOVEREIGN",
    width: int = 1200,
    height: int = 675,
    aspect_ratio: str = "16:9",
    offset: int = 0
) -> bytes:
    """渲染一张极具现代数字出版质感、赛博极光与毛玻璃拟态的 OG 技术封面卡片"""
    if aspect_ratio in ("2.35:1", "wechat"):
        width, height = 900, 383
    elif aspect_ratio in ("3:4", "portrait"):
        width, height = 900, 1200
    elif aspect_ratio in ("1:1", "square"):
        width, height = 900, 900

    # 1. 渲染极光弥散与科技网格底板
    img, accent_color = _render_aurora_background(width, height, offset=offset)

    # 2. 毛玻璃拟态主卡片容器 (Glass Card Panel with Rounded Corners)
    margin_x = int(width * 0.06)
    margin_y = int(height * 0.08)
    card_w = width - margin_x * 2
    card_h = height - margin_y * 2
    radius = 18

    panel = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    p_draw = ImageDraw.Draw(panel)

    p_draw.rounded_rectangle(
        [margin_x, margin_y, margin_x + card_w, margin_y + card_h],
        radius=radius,
        fill=(10, 15, 29, 175),
        outline=(255, 255, 255, 30),
        width=1
    )

    # 顶部极光微光反射边与角标
    p_draw.line([margin_x + radius, margin_y, margin_x + card_w - radius, margin_y], fill=accent_color, width=2)
    p_draw.line([margin_x + 14, margin_y + 14, margin_x + 36, margin_y + 14], fill=accent_color, width=3)
    p_draw.line([margin_x + 14, margin_y + 14, margin_x + 14, margin_y + 36], fill=accent_color, width=3)

    img.paste(panel, (0, 0), panel)
    draw = ImageDraw.Draw(img)

    # 3. 顶部品牌与分类标签胶囊 (Tag Pill)
    pill_font = _get_best_font(int(height * 0.038))
    safe_brand = str(brand_name).upper()[:22]
    safe_cat = str(category).upper()[:16]
    pill_text = f"{safe_brand}  //  {safe_cat}"

    # 绘制胶囊背景
    pill_bbox = draw.textbbox((0, 0), pill_text, font=pill_font)
    pill_tw = pill_bbox[2] - pill_bbox[0]
    pill_th = pill_bbox[3] - pill_bbox[1]
    px, py = margin_x + 36, margin_y + int(height * 0.052)
    pill_pad_x, pill_pad_y = 14, 6

    draw.rounded_rectangle(
        [px - pill_pad_x, py - pill_pad_y, px + pill_tw + pill_pad_x + 16, py + pill_th + pill_pad_y],
        radius=8,
        fill=(12, 28, 48),
        outline=(0, 242, 254),
        width=1
    )
    # 胶囊内部左侧极光发光微指示标
    dot_r = 3
    dot_cy = py + pill_th // 2
    draw.ellipse([px - 4, dot_cy - dot_r, px - 4 + dot_r * 2, dot_cy + dot_r], fill=(0, 242, 254))
    draw.text((px + 10, py - 2), pill_text, fill=(0, 242, 254), font=pill_font)

    # 4. 标题排版 (居中黄金视觉区，支持微光文字阴影与自适应折行)
    safe_title = _clean_text_for_rendering(title or "Untitled Document")
    title_size = int(height * 0.105) if len(safe_title) < 22 else int(height * 0.082)
    title_font = _get_best_font(title_size)

    max_text_w = card_w - int(width * 0.12)
    lines = _wrap_text_to_lines(draw, safe_title, title_font, max_width=max_text_w, max_lines=2)

    line_spacing = int(title_size * 0.38)
    total_text_h = len(lines) * title_size + (len(lines) - 1) * line_spacing
    start_y = margin_y + (card_h - total_text_h) // 2 - int(height * 0.015)

    for i, line in enumerate(lines):
        line_y = start_y + i * (title_size + line_spacing)
        line_x = margin_x + int(width * 0.055)
        # 文字阴影营造层次感
        draw.text((line_x + 2, line_y + 3), line, fill=(0, 0, 0, 180), font=title_font)
        draw.text((line_x, line_y), line, fill=(255, 255, 255), font=title_font)

    # 5. 底部精致元信息栏与分割线
    divider_y = margin_y + card_h - int(height * 0.11)
    draw.line(
        [margin_x + int(width * 0.04), divider_y, margin_x + card_w - int(width * 0.04), divider_y],
        fill=(255, 255, 255, 22),
        width=1
    )

    meta_font = _get_best_font(int(height * 0.034))
    meta_y = divider_y + int(height * 0.03)

    # 左侧作者标识
    safe_author = f"BY {str(author).upper()[:24]}"
    draw.text((margin_x + int(width * 0.05), meta_y), safe_author, fill=(148, 163, 184), font=meta_font)

    # 右侧安全出版矩阵水印
    wm_text = "SOVEREIGN PUBLISHING MATRIX"
    wm_bbox = draw.textbbox((0, 0), wm_text, font=meta_font)
    wm_w = wm_bbox[2] - wm_bbox[0]
    draw.text((margin_x + card_w - wm_w - int(width * 0.05), meta_y), wm_text, fill=(129, 140, 248), font=meta_font)

    # 6. 保存导出为高品质 JPEG 字节流
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=93)
    return buf.getvalue()
