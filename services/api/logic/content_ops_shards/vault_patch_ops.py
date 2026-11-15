# -*- coding: utf-8 -*-
"""
📝 Illacme Plenipes Content Operations Shard - vault_patch_ops
职责：原稿 Frontmatter 轻量级原子 Patch 与物理回写，同步 SQLite 账本。
符合 SOP-02 模块拆分协议与 300 行核心复杂度红线。
"""

import os
from typing import Dict, Any
from core.utils.text import parse_frontmatter, inject_frontmatter
from core.utils.tracing import tlog
from services.api.logic.content_ops_shards.safe_ops import resolve_safe_path


def patch_frontmatter_logic(engine, req: Dict[str, Any]) -> Dict[str, Any]:
    """
    🚀 物理原子更新原稿 Frontmatter 字段并同步 SQLite 账本
    入参：
        req = {
            "rel_path": "docs/guide.md",
            "patch": {"podcast": False, "draft": True, "featured": True}
        }
    """
    if not engine:
        return {"success": False, "error": "Engine not initialized"}

    rel_path = req.get("rel_path")
    patch = req.get("patch")
    if not rel_path or not isinstance(patch, dict):
        return {"success": False, "error": "缺少 rel_path 或 patch 字典"}

    abs_path = resolve_safe_path(engine, rel_path)
    if not abs_path or not os.path.isfile(abs_path):
        return {"success": False, "error": f"未找到原稿文件: {rel_path}"}

    try:
        with open(abs_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return {"success": False, "error": f"读取原稿文件失败: {e}"}

    old_meta, pure_content, _ = parse_frontmatter(content)
    merged_meta = dict(old_meta)

    for k, v in patch.items():
        if v is None:
            merged_meta.pop(k, None)
        else:
            merged_meta[k] = v

    full_content = inject_frontmatter(pure_content, merged_meta)

    try:
        with open(abs_path, "w", encoding="utf-8") as f:
            f.write(full_content)
    except Exception as e:
        return {"success": False, "error": f"写入物理原稿文件失败: {e}"}

    # 同步更新 SQLite 账本 (完整对齐 frontmatter 中的核心元数据字段)
    try:
        if hasattr(engine, "meta") and hasattr(engine.meta, "sqlite"):
            db_updates = dict(patch)
            if "cover" in merged_meta and merged_meta["cover"]:
                db_updates["cover"] = merged_meta["cover"]
            if "title" in merged_meta and merged_meta["title"]:
                db_updates["title"] = merged_meta["title"]
            if "slug" in merged_meta and merged_meta["slug"]:
                db_updates["slug"] = merged_meta["slug"]
            engine.meta.sqlite.update_document_metadata(rel_path, db_updates)
    except Exception as e:
        tlog.warning(f"同步 SQLite 元数据异常: {e}")

    return {
        "success": True,
        "rel_path": rel_path,
        "patch": patch,
        "frontmatter": merged_meta
    }

