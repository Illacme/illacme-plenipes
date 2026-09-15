#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🖼️ [V1.0] Illacme Plenipes - Polymorphic Cover Deriver
模块职责：社媒渠道画幅画像映射、焦点智能居中裁切与多态封面物理派生落盘。
🛡️ [SOP-01 / 单文件 ≤ 300 行]
"""

import os
import io
import hashlib
from typing import Tuple, Optional
from PIL import Image
import requests
from core.utils.tracing import tlog

CHANNEL_ASPECT_MAP = {
    "wechat": "2.35:1",
    "xiaohongshu": "3:4",
    "rednote": "3:4",
    "instagram": "1:1",
    "zhihu": "16:9",
    "bilibili": "16:9",
    "toutiao": "16:9",
    "juejin": "16:9",
    "csdn": "16:9",
    "devto": "16:9",
    "hashnode": "16:9",
    "medium": "16:9",
    "substack": "16:9",
    "ghost": "16:9",
    "wordpress": "16:9",
}

DIMENSION_MAP = {
    "2.35:1": (1200, 510),
    "16:9": (1200, 675),
    "3:4": (900, 1200),
    "1:1": (800, 800),
    "4:3": (1000, 750),
}


def get_channel_aspect_ratio(channel_id: str) -> str:
    """获取指定分发渠道的官方推荐画幅比例"""
    clean_id = str(channel_id or "").lower().strip()
    return CHANNEL_ASPECT_MAP.get(clean_id, "16:9")


def crop_image_bytes(
    img_bytes: bytes,
    aspect_ratio: str,
    focal_x: float = 0.5,
    focal_y: float = 0.5,
    zoom: float = 1.0
) -> Optional[bytes]:
    """基于缩放倍率（zoom: 1.0~2.5）与焦点锚点（focal_x, focal_y: 0.0~1.0）执行智能裁切与重采样"""
    if not img_bytes:
        return None
    try:
        img = Image.open(io.BytesIO(img_bytes))
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        orig_w, orig_h = img.size
        target_w, target_h = DIMENSION_MAP.get(aspect_ratio, (1200, 675))
        target_ratio = target_w / target_h
        orig_ratio = orig_w / orig_h

        clamped_x = max(0.0, min(1.0, float(focal_x)))
        clamped_y = max(0.0, min(1.0, float(focal_y)))
        clamped_z = max(1.0, min(3.0, float(zoom or 1.0)))

        if orig_ratio > target_ratio:
            base_w = int(orig_h * target_ratio)
            base_h = orig_h
        else:
            base_w = orig_w
            base_h = int(orig_w / target_ratio)

        crop_w = max(10, int(base_w / clamped_z))
        crop_h = max(10, int(base_h / clamped_z))

        max_left = max(0, orig_w - crop_w)
        max_top = max(0, orig_h - crop_h)

        left = int(max_left * clamped_x)
        top = int(max_top * clamped_y)

        img = img.crop((left, top, left + crop_w, top + crop_h))
        img = img.resize((target_w, target_h), Image.Resampling.LANCZOS)
        out_io = io.BytesIO()
        img.save(out_io, format="JPEG", quality=92)
        return out_io.getvalue()
    except Exception as e:
        tlog.warning(f"⚠️ [CoverDeriver] 图像焦点裁切异常: {e}")
        return None


def read_cover_source_bytes(source_cover: str, vault_root: str = "") -> Optional[bytes]:
    """多源读取封面图片二进制（支持本地相对路径、绝对路径、缓存路径与公网外链）"""
    if not source_cover:
        return None
    clean_src = str(source_cover).split("?")[0].split("#")[0].strip()

    # 1. 外部 HTTP/HTTPS 链接
    if clean_src.startswith(("http://", "https://")):
        try:
            resp = requests.get(clean_src, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            if resp.status_code == 200 and len(resp.content) > 200:
                return resp.content
        except Exception as e:
            tlog.warning(f"⚠️ [CoverDeriver] 拉取外链封面失败: {e}")
            return None

    # 2. 本地文件系统候选路径定位
    root = vault_root or os.getcwd()
    candidates = [
        clean_src,
        os.path.join(root, clean_src.lstrip("/")),
        os.path.join(root, ".plenipes", "cache", "covers", os.path.basename(clean_src)),
        os.path.join(os.getcwd(), ".plenipes", "cache", "covers", os.path.basename(clean_src)),
        os.path.join(root, "assets", clean_src.lstrip("/")),
        os.path.join(root, "images", clean_src.lstrip("/"))
    ]
    for c in candidates:
        if os.path.isfile(c):
            try:
                with open(c, "rb") as f:
                    return f.read()
            except Exception:
                continue
    return None


def derive_cover_asset(
    source_cover: str,
    target_ratio: str,
    focal_y: float = 0.5,
    focal_x: float = 0.5,
    zoom: float = 1.0,
    vault_root: str = "",
    cache_dir: str = ""
) -> Tuple[Optional[str], Optional[bytes]]:
    """
    给定源封面，根据目标画幅、缩放倍率与焦点坐标派生物理图片并落盘缓存。
    返回元组: (派生后的本地相对 URL, 图片二进制 bytes)
    """
    raw_bytes = read_cover_source_bytes(source_cover, vault_root=vault_root)
    if not raw_bytes:
        return None, None

    derived_bytes = crop_image_bytes(
        img_bytes=raw_bytes,
        aspect_ratio=target_ratio,
        focal_x=focal_x,
        focal_y=focal_y,
        zoom=zoom
    )
    if not derived_bytes:
        return None, None

    clean_fn = os.path.basename(source_cover.split("?")[0])
    hash_seed = f"{clean_fn}_{target_ratio}_{round(focal_y, 2)}_{round(focal_x, 2)}_{round(zoom, 2)}_{len(derived_bytes)}"
    file_hash = hashlib.md5(hash_seed.encode("utf-8")).hexdigest()[:12]
    filename = f"derived_{file_hash}_{target_ratio.replace(':', 'x')}.jpg"

    out_dir = cache_dir or (os.path.join(vault_root, ".plenipes", "cache", "covers") if vault_root else os.path.join(os.getcwd(), ".plenipes", "cache", "covers"))
    os.makedirs(out_dir, exist_ok=True)
    save_path = os.path.join(out_dir, filename)

    try:
        with open(save_path, "wb") as f:
            f.write(derived_bytes)
        rel_url = f"/api/design/assets/covers/{filename}"
        tlog.info(f"✨ [CoverDeriver] 多态封面已成功物理派生落盘: {filename} ({target_ratio}, zoom={zoom}, fx={focal_x}, fy={focal_y})")
        return rel_url, derived_bytes
    except Exception as e:
        tlog.error(f"🛑 [CoverDeriver] 派生图片写盘失败: {e}")
        return None, derived_bytes
