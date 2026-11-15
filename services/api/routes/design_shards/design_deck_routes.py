# -*- coding: utf-8 -*-
"""
📑 Design Studio - Multi-Ratio Knowledge Card Deck REST API Shard
职责：提供知识卡片海报多画幅生成 (3:4 / 1:1 / 16:9)、查询、资产分发与一键 ZIP 打包接口。
🛡️ [SOP-01] 物理行数严格保持在 300 行以内。
"""

import os
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel

from core.runtime.engine_singleton import get_global_engine
from core.utils.tracing import tlog
from core.utils.text import parse_frontmatter
from core.design.card_deck.deck_generator import DeckGenerator
from services.api.logic.content_ops_shards.safe_ops import resolve_safe_path
from services.api.routes.system import verify_token

router = APIRouter(tags=["Knowledge Card Deck"])


class CardDeckGenerateRequest(BaseModel):
    rel_path: str
    offset: Optional[int] = 0
    max_cards: Optional[int] = 6
    aspect_ratio: Optional[str] = "3:4"
    brand_name: Optional[str] = None


@router.post("/api/design/cards/generate", dependencies=[Depends(verify_token)])
async def generate_knowledge_card_deck(req: CardDeckGenerateRequest) -> Dict[str, Any]:
    """生成指定文档与指定画幅 (3:4/1:1/16:9) 的知识卡片海报图集与全套 ZIP 压缩包"""
    engine = get_global_engine()
    vault_root = getattr(engine, "vault_root", os.getcwd()) if engine else os.getcwd()

    if engine:
        safe_abs_path = resolve_safe_path(engine, req.rel_path)
    else:
        safe_abs_path = os.path.join(vault_root, req.rel_path)

    if not safe_abs_path or not os.path.isfile(safe_abs_path):
        raise HTTPException(status_code=404, detail=f"未找到指定的稿件: {req.rel_path}")

    try:
        with open(safe_abs_path, "r", encoding="utf-8") as f:
            raw_content = f.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取稿件失败: {e}")

    fm_dict, body, _ = parse_frontmatter(raw_content)

    doc_meta = engine.meta.get_doc_info(req.rel_path) if (engine and hasattr(engine, "meta")) else {}
    doc_meta = doc_meta or {}

    title = fm_dict.get("title") or doc_meta.get("title") or os.path.splitext(os.path.basename(req.rel_path))[0]
    author = fm_dict.get("author") or doc_meta.get("author") or "创作者"
    category = fm_dict.get("category") or doc_meta.get("category") or "深度干货"
    slug = fm_dict.get("slug") or doc_meta.get("slug") or os.path.splitext(os.path.basename(req.rel_path))[0]
    clean_slug = "".join([c if c.isalnum() or c in ("-", "_") else "_" for c in slug])

    brand_name = req.brand_name or fm_dict.get("brand_name") or (getattr(engine, "imprint_id", "SOVEREIGN") if engine else "SOVEREIGN")

    try:
        result = DeckGenerator.generate_deck(
            content=raw_content,
            slug=clean_slug,
            metadata={
                "title": title,
                "author": author,
                "category": category,
                "brand_name": brand_name,
                "description": fm_dict.get("description") or fm_dict.get("digest") or ""
            },
            offset=req.offset or 0,
            max_cards=req.max_cards or 6,
            aspect_ratio=req.aspect_ratio or "3:4",
            vault_root=vault_root
        )
        return result
    except Exception as e:
        tlog.error(f"❌ [CardDeck] 生成卡片图集失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"生成卡片海报失败: {e}")


@router.get("/api/design/cards/info", dependencies=[Depends(verify_token)])
async def get_knowledge_card_deck_info(rel_path: str, aspect_ratio: Optional[str] = "3:4") -> Dict[str, Any]:
    """查询指定稿件与指定画幅是否已生成过卡片海报及其元数据"""
    engine = get_global_engine()
    vault_root = getattr(engine, "vault_root", os.getcwd()) if engine else os.getcwd()

    slug = ""
    safe_abs_path = resolve_safe_path(engine, rel_path) if engine else os.path.join(vault_root, rel_path)
    if safe_abs_path and os.path.isfile(safe_abs_path):
        try:
            with open(safe_abs_path, "r", encoding="utf-8") as f:
                fm, _, _ = parse_frontmatter(f.read())
                slug = fm.get("slug") or ""
        except Exception:
            pass

    if not slug:
        slug = os.path.splitext(os.path.basename(rel_path))[0]

    safe_slug = "".join([c if c.isalnum() or c in ("-", "_") else "_" for c in slug])
    base_slug = "".join([c if c.isalnum() or c in ("-", "_") else "_" for c in os.path.splitext(os.path.basename(rel_path))[0]])
    ratio_tag = str(aspect_ratio or "3:4").replace(":", "x").lower()

    candidates = [f"{safe_slug}_{ratio_tag}", safe_slug, f"{base_slug}_{ratio_tag}", base_slug]

    target_dir_name = None
    deck_dir = None
    for cand in candidates:
        d = os.path.join(vault_root, ".plenipes", "cache", "cards", cand)
        if os.path.isdir(d):
            target_dir_name = cand
            deck_dir = d
            break

    if not deck_dir:
        return {"exists": False, "slug": safe_slug, "aspect_ratio": aspect_ratio, "cards": [], "total": 0}

    cards: List[Dict[str, Any]] = []
    files = sorted(os.listdir(deck_dir))
    for f in files:
        if f.startswith("card_") and f.endswith(".jpg"):
            idx_str = f.replace("card_", "").replace(".jpg", "")
            idx = int(idx_str) if idx_str.isdigit() else 1
            cards.append({
                "index": idx,
                "filename": f,
                "url": f"/api/design/assets/cards/{target_dir_name}/{f}"
            })

    zip_filename = f"deck_{safe_slug}_{ratio_tag}.zip"
    zip_path = os.path.join(deck_dir, zip_filename)
    if not os.path.isfile(zip_path):
        # 兼容未带比例标签的旧 zip
        fallback_zip = f"deck_{safe_slug}.zip"
        if os.path.isfile(os.path.join(deck_dir, fallback_zip)):
            zip_filename = fallback_zip

    zip_url = f"/api/design/assets/cards/{target_dir_name}/{zip_filename}" if os.path.isfile(os.path.join(deck_dir, zip_filename)) else None

    return {
        "exists": len(cards) > 0,
        "slug": safe_slug,
        "dir_name": target_dir_name,
        "aspect_ratio": aspect_ratio,
        "total": len(cards),
        "zip_url": zip_url,
        "zip_filename": zip_filename,
        "cards": cards
    }


@router.get("/api/design/assets/cards/{folder}/{filename}")
async def serve_card_asset(folder: str, filename: str):
    """静态文件分发接口：向前端或外部客户端安全返回卡片海报与 ZIP 归档"""
    engine = get_global_engine()
    vault_root = getattr(engine, "vault_root", os.getcwd()) if engine else os.getcwd()

    clean_folder = "".join([c if c.isalnum() or c in ("-", "_") else "_" for c in folder])
    clean_fn = os.path.basename(filename)

    target_path = os.path.join(vault_root, ".plenipes", "cache", "cards", clean_folder, clean_fn)
    if not os.path.isfile(target_path):
        raise HTTPException(status_code=404, detail="卡片文件不存在或已被清理")

    media_type = "application/zip" if clean_fn.endswith(".zip") else "image/jpeg"
    return FileResponse(target_path, media_type=media_type)
