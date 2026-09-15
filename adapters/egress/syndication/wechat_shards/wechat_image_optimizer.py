#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes - WeChat Image Optimizer Shard
模块职责：针对微信公众号图片体积限制（封面永久素材 <= 2MB，正文图片 <= 2MB 保证移动端秒开），
提供内存级智能无损/等比阶梯压缩引擎。
安全底线：全程在内存中进行，绝对不修改或覆盖创作者文库中的物理原始图片。
严格遵守 SOP-01 规范 (< 300 行)。
"""

import io
import os
from typing import Tuple
from core.utils.tracing import tlog

def optimize_image_for_wechat(
    image_bytes: bytes,
    filename: str,
    max_size_bytes: int = 2 * 1024 * 1024,
    max_dimension: int = 1920
) -> Tuple[bytes, str]:
    """
    智能检测并压缩超限图片至微信规定阈值内 (默认 2MB)。
    返回 (优化后的 bytes, 文件名)。
    """
    if not image_bytes:
        return image_bytes, filename

    curr_len = len(image_bytes)
    if curr_len <= max_size_bytes:
        return image_bytes, filename

    tlog.info(f"🔍 [微信图片预检] 图片 {filename} 体积为 {curr_len / 1024:.1f}KB，超出微信安全限额 (2048KB)，启动智能等比压缩...")

    try:
        from PIL import Image, ImageOps
        img = Image.open(io.BytesIO(image_bytes))
        
        # 保持 EXIF 旋转对齐
        try:
            img = ImageOps.exif_transpose(img)
        except Exception:
            pass

        # 1. 尺寸等比缩放
        orig_w, orig_h = img.size
        target_w, target_h = orig_w, orig_h
        if max(orig_w, orig_h) > max_dimension:
            scale = max_dimension / float(max(orig_w, orig_h))
            target_w = max(1, int(orig_w * scale))
            target_h = max(1, int(orig_h * scale))
            resample_filter = getattr(Image, "Resampling", Image).LANCZOS
            img = img.resize((target_w, target_h), resample=resample_filter)

        # 2. 模式转换 (RGBA/P -> RGB)，兼容透明背景转为白底
        if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
            bg = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode != "RGBA":
                img = img.convert("RGBA")
            bg.paste(img, mask=img.split()[3]) # alpha mask
            img = bg
        elif img.mode != "RGB":
            img = img.convert("RGB")

        # 3. 阶梯质量迭代保存，直至体积 <= max_size_bytes - 100KB (留出安全余量)
        target_threshold = max_size_bytes - (100 * 1024)
        qualities = [85, 75, 65, 50]
        result_bytes = None
        new_filename = os.path.splitext(filename)[0] + ".jpg"

        for q in qualities:
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=q, optimize=True)
            candidate = buf.getvalue()
            if len(candidate) <= target_threshold:
                result_bytes = candidate
                break
            result_bytes = candidate

        # 4. 如果仍然超限，执行二级分辨率等比下采样 (0.75x)
        if result_bytes and len(result_bytes) > max_size_bytes:
            resample_filter = getattr(Image, "Resampling", Image).LANCZOS
            img = img.resize((max(1, int(img.width * 0.75)), max(1, int(img.height * 0.75))), resample=resample_filter)
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=65, optimize=True)
            result_bytes = buf.getvalue()

        if result_bytes and len(result_bytes) < curr_len:
            tlog.info(f"✨ [微信图片压缩完成] {filename} 体积已自愈降级: {curr_len / 1024:.1f}KB -> {len(result_bytes) / 1024:.1f}KB")
            return result_bytes, new_filename

    except Exception as e:
        tlog.warning(f"⚠️ [微信图片压缩异常] 无法压缩图片 {filename}: {e}，回退使用原图")

    return image_bytes, filename
