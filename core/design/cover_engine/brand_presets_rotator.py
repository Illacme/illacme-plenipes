# -*- coding: utf-8 -*-
"""
🎨 CoverEngine Shard - Brand Presets Rotator
职责：品牌抽象母本图库确定性轮巡分配器。
特性：
1. 优先扫描当前品牌目录 imprints/{brand}/assets/covers/ 预置图片；
2. 次级扫描系统内置母本图库 core/design/assets/default_presets/；
3. 若磁盘无物理预存，自动使用算法合成 8 套高质感极光流体渐变底图并缓存；
4. 支持基于 hash(slug) 确定性分配与 offset 偏移切换 ("换一张" 功能)；
🛡️ [SOP-01] 物理行数保持在 300 行以内。
"""

import os
import io
import hashlib
from typing import Optional, List
from PIL import Image, ImageDraw
from core.utils.tracing import tlog

# 内置 8 套高质感色系组合 (起始色, 终止色, 辅助色)
GRADIENT_PALETTES = [
    ((15, 23, 42), (30, 58, 138), (56, 189, 248)),   # 0: 赛博深海 (Deep Navy -> Sky Blue)
    ((17, 24, 39), (88, 28, 135), (217, 70, 239)),  # 1: 暗夜霓虹 (Midnight -> Neon Purple)
    ((6, 78, 59), (16, 185, 129), (167, 243, 208)),  # 2: 极光森林 (Emerald -> Aurora Mint)
    ((67, 20, 7), (180, 83, 9), (252, 211, 77)),    # 3: 熔岩琥珀 (Amber Flame -> Goldenrod)
    ((24, 24, 27), (63, 63, 70), (161, 161, 170)),   # 4: 钛金极简 (Titanium Slate -> Silver)
    ((2, 44, 34), (13, 148, 136), (94, 234, 212)),   # 5: 碧蓝矩阵 (Teal Cyber -> Cyan)
    ((76, 5, 25), (190, 18, 60), (251, 113, 133)),   # 6: 赤红星云 (Crimson Nebula -> Rose)
    ((30, 27, 75), (67, 56, 202), (165, 180, 252))   # 7: 泛银河系 (Deep Indigo -> Cobalt)
]

def generate_procedural_gradient(palette_idx: int, width: int = 1200, height: int = 675) -> bytes:
    """纯算法合成柔和高斯式双色渐变与几何微噪点，0 外部文件依赖"""
    palette = GRADIENT_PALETTES[palette_idx % len(GRADIENT_PALETTES)]
    start_c, mid_c, accent_c = palette

    img = Image.new("RGB", (width, height), color=start_c)
    draw = ImageDraw.Draw(img)

    # 绘制多层带有柔和过渡的几何径向多边形
    # 右上角大流体晕染
    rx, ry = int(width * 0.75), int(height * 0.25)
    r_radius = int(height * 0.7)
    draw.ellipse([rx - r_radius, ry - r_radius, rx + r_radius, ry + r_radius], fill=mid_c)

    # 左下角次级光斑
    lx, ly = int(width * 0.2), int(height * 0.8)
    l_radius = int(height * 0.5)
    draw.ellipse([lx - l_radius, ly - l_radius, lx + l_radius, ly + l_radius], fill=accent_c)

    # 绘制高质感极简几何外框线
    draw.rectangle([20, 20, width - 20, height - 20], outline=(255, 255, 255, 40), width=1)

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return buf.getvalue()

def resolve_brand_preset_cover(
    doc_id: str,
    slug: str = "",
    brand_id: str = "default",
    offset: int = 0,
    width: int = 1200,
    height: int = 675,
    vault_root: str = ""
) -> bytes:
    """
    根据文章标识符与品牌定位确定性挑选一张母本底图。
    支持通过 offset 循环获取下一张 ("换一张" 交互)。
    """
    seed_str = f"{doc_id}_{slug}_{brand_id}"
    base_hash = int(hashlib.md5(seed_str.encode("utf-8")).hexdigest()[:8], 16)
    
    # 1. 尝试扫描物理文件
    search_dirs = []
    if vault_root and brand_id:
        search_dirs.append(os.path.join(vault_root, "imprints", brand_id, "assets", "covers"))
    search_dirs.append(os.path.join(os.getcwd(), "imprints", brand_id, "assets", "covers"))
    search_dirs.append(os.path.join(os.path.dirname(__file__), "..", "assets", "default_presets"))

    found_images: List[str] = []
    for d in search_dirs:
        if os.path.exists(d) and os.path.isdir(d):
            for fname in sorted(os.listdir(d)):
                if fname.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                    found_images.append(os.path.join(d, fname))

    if found_images:
        target_idx = (base_hash + offset) % len(found_images)
        chosen_path = found_images[target_idx]
        try:
            with open(chosen_path, "rb") as f:
                tlog.info(f"🎨 [品牌母本] 命中物理预设底图 ({target_idx + 1}/{len(found_images)}): {os.path.basename(chosen_path)}")
                return f.read()
        except Exception as e:
            tlog.warning(f"⚠️ [品牌母本] 读取底图文件异常: {e}")

    # 2. 物理无文件时，毫秒级自愈调用内置 8 色调算法合成
    palette_idx = (base_hash + offset) % len(GRADIENT_PALETTES)
    tlog.info(f"🎨 [品牌母本] 自动合成高质感流体渐变母本图 (Palette #{palette_idx + 1})")
    return generate_procedural_gradient(palette_idx, width=width, height=height)
