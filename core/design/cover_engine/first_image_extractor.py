# -*- coding: utf-8 -*-
"""
🎨 CoverEngine Shard - Article First Image Extractor
职责：从 Markdown 文稿中提取首张引用的图片并裁切为目标画幅。
特性：
1. 正则解析 Markdown 原生图片语法 `![alt](url)` 与 HTML `<img src="url">`；
2. 本地绝对/相对路径直接读取，网络图床 URL 快速安全拉取；
3. 基于 Pillow 居中安全区裁剪填充为目标比例（16:9 / 2.35:1 / 1:1）；
4. 容错自愈：正文无图或读取失败时优雅返回 None。
🛡️ [SOP-01] 物理行数严格保持在 300 行以内。
"""

import os
import re
import io
import requests
from typing import Optional, Tuple
from PIL import Image
from core.utils.tracing import tlog

IMAGE_MD_PATTERN = re.compile(r'!\[.*?\]\((.+?)\)', re.IGNORECASE)
IMAGE_HTML_PATTERN = re.compile(r'<img\s+[^>]*?src=["\']([^"\']+)["\']', re.IGNORECASE)

def _parse_dimensions(aspect_ratio: str) -> Tuple[int, int]:
    """根据画幅比例换算标准分辨率"""
    dim_map = {
        "2.35:1": (1200, 510),
        "16:9": (1200, 675),
        "1:1": (800, 800),
        "3:4": (750, 1000),
        "4:3": (1000, 750)
    }
    return dim_map.get(aspect_ratio, (1200, 675))

def _crop_and_resize_image(img_bytes: bytes, target_w: int, target_h: int) -> Optional[bytes]:
    """居中裁切并缩放至指定画幅"""
    try:
        img = Image.open(io.BytesIO(img_bytes))
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        orig_w, orig_h = img.size
        target_ratio = target_w / target_h
        orig_ratio = orig_w / orig_h

        if orig_ratio > target_ratio:
            # 原图较宽，左右裁剪
            new_w = int(orig_h * target_ratio)
            left = (orig_w - new_w) // 2
            img = img.crop((left, 0, left + new_w, orig_h))
        else:
            # 原图较高，上下裁剪
            new_h = int(orig_w / target_ratio)
            top = (orig_h - new_h) // 2
            img = img.crop((0, top, orig_w, top + new_h))

        img = img.resize((target_w, target_h), Image.Resampling.LANCZOS)
        out_io = io.BytesIO()
        img.save(out_io, format="JPEG", quality=92)
        return out_io.getvalue()
    except Exception as e:
        tlog.warning(f"⚠️ [FirstImageExtractor] 图片重采样裁切失败: {e}")
        return None

def extract_first_image_from_doc(
    doc_id: str,
    vault_root: str = "",
    aspect_ratio: str = "16:9"
) -> Optional[bytes]:
    """
    定位文稿物理文件并提取首张图片二进制
    """
    if not doc_id:
        return None

    root = vault_root or os.getcwd()
    abs_path = os.path.join(root, doc_id) if not os.path.isabs(doc_id) else doc_id
    if not os.path.isfile(abs_path):
        if not abs_path.endswith(".md"):
            abs_path += ".md"
    if not os.path.isfile(abs_path):
        tlog.info(f"ℹ️ [FirstImageExtractor] 未找到文稿物理文件: {doc_id}")
        return None

    try:
        with open(abs_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except Exception as e:
        tlog.warning(f"⚠️ [FirstImageExtractor] 读取文稿失败: {e}")
        return None

    # 1. 尝试匹配 Markdown 图片语法
    first_url = None
    md_matches = IMAGE_MD_PATTERN.findall(content)
    for m in md_matches:
        raw_url = m.split()[0].strip().strip('"\')')
        if raw_url:
            first_url = raw_url
            break

    # 2. 尝试匹配 HTML img 语法
    if not first_url:
        html_matches = IMAGE_HTML_PATTERN.findall(content)
        for h in html_matches:
            if h.strip():
                first_url = h.strip()
                break

    if not first_url:
        tlog.info(f"ℹ️ [FirstImageExtractor] 文稿正文未引用任何图片: {doc_id}")
        return None

    raw_bytes = None
    # 3. 处理网络图床 URL
    if first_url.startswith(("http://", "https://")):
        try:
            tlog.info(f"🌐 [FirstImageExtractor] 正在拉取正文首图外链: {first_url[:60]}")
            resp = requests.get(first_url, timeout=12, headers={"User-Agent": "Mozilla/5.0"})
            if resp.status_code == 200 and len(resp.content) > 500:
                raw_bytes = resp.content
        except Exception as e:
            tlog.warning(f"⚠️ [FirstImageExtractor] 拉取首图外链超时或失败: {e}")
            return None
    else:
        # 4. 处理本地相对路径
        doc_dir = os.path.dirname(abs_path)
        candidates = [
            os.path.join(doc_dir, first_url),
            os.path.join(root, first_url.lstrip("/")),
            os.path.join(root, "assets", first_url.lstrip("/")),
            os.path.join(root, "images", first_url.lstrip("/"))
        ]
        local_img_path = None
        for c in candidates:
            if os.path.isfile(c):
                local_img_path = c
                break

        if local_img_path:
            try:
                with open(local_img_path, "rb") as img_f:
                    raw_bytes = img_f.read()
            except Exception as e:
                tlog.warning(f"⚠️ [FirstImageExtractor] 读取本地首图失败: {e}")
                return None
        else:
            tlog.info(f"ℹ️ [FirstImageExtractor] 本地图片未命中物理文件: {first_url}")
            return None

    if not raw_bytes:
        return None

    target_w, target_h = _parse_dimensions(aspect_ratio)
    return _crop_and_resize_image(raw_bytes, target_w, target_h)
