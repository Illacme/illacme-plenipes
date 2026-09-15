#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes - Cover Asset Self-Healing Engine Shard
模块职责：封面静态资源 JIT 智能自愈、默认占位图供给与文库缺失封面批量修复。
彻底根除 /api/design/assets/covers/*.jpg 404 Not Found 异常与浏览器破图。
严格遵守 SOP-01 规范 (< 300 行)。
"""

import os
import re
from typing import Tuple, Dict, Any, List
from fastapi import Response
from fastapi.responses import FileResponse
from core.utils.tracing import tlog
from core.design.cover_engine.og_card_renderer import render_og_card

def _find_doc_title_by_cover_filename(clean_fn: str, vault_root: str) -> Tuple[str, str]:
    """遍历文库 Markdown 区域，反查引用该封面文件名的文档标题与分类"""
    try:
        for root, _, files in os.walk(vault_root):
            if any(p in root for p in [".git", ".plenipes", "node_modules", "dist", "themes"]):
                continue
            for f in files:
                if f.endswith(".md"):
                    full_p = os.path.join(root, f)
                    try:
                        with open(full_p, "r", encoding="utf-8", errors="ignore") as mf:
                            head = mf.read(2048)
                            if clean_fn in head:
                                title_match = re.search(r"^title:\s*[\"']?(.*?)[\"']?\s*$", head, re.MULTILINE)
                                title = title_match.group(1).strip() if title_match else ""
                                cat_match = re.search(r"^category:\s*[\"']?(.*?)[\"']?\s*$", head, re.MULTILINE)
                                cat = cat_match.group(1).strip() if cat_match else ""
                                if title:
                                    return title, cat or "Knowledge"
                    except Exception:
                        pass
    except Exception:
        pass

    raw_name = os.path.splitext(clean_fn)[0].replace("cover_", "").replace("gen_", "").replace("_", " ").title()
    fallback_title = f"Document Overview - {raw_name}" if raw_name else "Knowledge Archive"
    return fallback_title, "Engineering"

def serve_cover_asset_or_heal(filename: str, vault_root: str = "") -> Response:
    """
    静态文件供给接口（JIT 自愈双保险）：
    1. 物理文件存在 -> 直接返回 FileResponse；
    2. 物理文件缺失 -> 动态反查标题、即时生成极光 OG 封面、自愈写盘并返回 200 OK，0 次 404。
    """
    clean_fn = os.path.basename(filename)
    if not clean_fn.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
        clean_fn += ".jpg"

    root = vault_root or os.getcwd()
    cache_dir = os.path.join(root, ".plenipes", "cache", "covers")
    os.makedirs(cache_dir, exist_ok=True)
    file_path = os.path.join(cache_dir, clean_fn)

    # 1. 优先命中物理文件
    if os.path.isfile(file_path):
        return FileResponse(file_path, media_type="image/jpeg", headers={"Cache-Control": "public, max-age=86400"})

    # 兼容当前工作目录
    alt_path = os.path.join(os.getcwd(), ".plenipes", "cache", "covers", clean_fn)
    if os.path.isfile(alt_path):
        return FileResponse(alt_path, media_type="image/jpeg", headers={"Cache-Control": "public, max-age=86400"})

    # 2. 🛡️ JIT 即时自愈生成防线
    try:
        title, cat = _find_doc_title_by_cover_filename(clean_fn, root)
        img_bytes = render_og_card(
            title=title,
            author="Illacme Plenipes",
            category=cat,
            brand_name="ILLACME SOVEREIGN",
            aspect_ratio="16:9"
        )
        if img_bytes:
            # 自动写盘完成物理自愈
            with open(file_path, "wb") as f:
                f.write(img_bytes)
            tlog.info(f"✨ [CoverHealer] 缺失封面已 JIT 动态自愈并写盘: {clean_fn} (《{title}》)")
            return Response(content=img_bytes, media_type="image/jpeg", headers={
                "Cache-Control": "public, max-age=86400",
                "X-Cover-Healed": "true"
            })
    except Exception as e:
        tlog.warning(f"⚠️ [CoverHealer] JIT 自愈生成异常: {e}")

    # 3. 终极兜底默认占位图
    return serve_default_cover(vault_root=root)

def serve_default_cover(vault_root: str = "") -> Response:
    """提供统一标准的官方科技感极光毛玻璃默认封面"""
    root = vault_root or os.getcwd()
    cache_dir = os.path.join(root, ".plenipes", "cache", "covers")
    os.makedirs(cache_dir, exist_ok=True)
    default_path = os.path.join(cache_dir, "default_placeholder.jpg")

    if os.path.isfile(default_path):
        return FileResponse(default_path, media_type="image/jpeg", headers={"Cache-Control": "public, max-age=604800"})

    img_bytes = render_og_card(
        title="Illacme Plenipes",
        author="Sovereign Publishing",
        category="Universal Archive",
        brand_name="ILLACME SOVEREIGN",
        aspect_ratio="16:9"
    )
    if img_bytes:
        try:
            with open(default_path, "wb") as f:
                f.write(img_bytes)
        except Exception:
            pass
        return Response(content=img_bytes, media_type="image/jpeg", headers={"Cache-Control": "public, max-age=604800"})

    return Response(status_code=204)

def heal_missing_covers_in_vault(vault_root: str = "") -> Dict[str, Any]:
    """扫描文库中所有 Markdown 文档，批量为缺失的本地封面物理生成并落盘"""
    root = vault_root or os.getcwd()
    cache_dir = os.path.join(root, ".plenipes", "cache", "covers")
    os.makedirs(cache_dir, exist_ok=True)

    scanned_count = 0
    healed_files: List[str] = []

    for dirpath, _, filenames in os.walk(root):
        if any(p in dirpath for p in [".git", ".plenipes", "node_modules", "dist", "themes"]):
            continue
        for fn in filenames:
            if fn.endswith(".md"):
                scanned_count += 1
                full_path = os.path.join(dirpath, fn)
                try:
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read(4096)
                    # 匹配 cover: /api/design/assets/covers/cover_xxx.jpg
                    match = re.search(r"^cover:\s*[\"']?(/api/design/assets/covers/([^\"'\s]+))[\"']?", content, re.MULTILINE)
                    if match:
                        cover_fn = os.path.basename(match.group(2).split("?")[0])
                        target_file = os.path.join(cache_dir, cover_fn)
                        if not os.path.isfile(target_file):
                            # 提取文章标题
                            title_m = re.search(r"^title:\s*[\"']?(.*?)[\"']?\s*$", content, re.MULTILINE)
                            title = title_m.group(1).strip() if title_m else os.path.splitext(fn)[0]
                            cat_m = re.search(r"^category:\s*[\"']?(.*?)[\"']?\s*$", content, re.MULTILINE)
                            cat = cat_m.group(1).strip() if cat_m else "Knowledge"

                            img_bytes = render_og_card(
                                title=title,
                                author="Illacme Plenipes",
                                category=cat,
                                brand_name="ILLACME SOVEREIGN",
                                aspect_ratio="16:9"
                            )
                            if img_bytes:
                                with open(target_file, "wb") as out_f:
                                    out_f.write(img_bytes)
                                healed_files.append(cover_fn)
                except Exception as e:
                    tlog.warning(f"⚠️ [CoverHealer] 扫描文章自愈异常 {full_path}: {e}")

    tlog.info(f"✨ [CoverHealer] 文库封面批量自愈扫描完成: 扫描 {scanned_count} 篇，自愈补齐 {len(healed_files)} 个封面")
    return {
        "scanned": scanned_count,
        "healed_count": len(healed_files),
        "healed_files": healed_files
    }
