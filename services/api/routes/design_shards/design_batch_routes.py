# -*- coding: utf-8 -*-
"""
🎨 Design Studio - Batch Cover Operations Routes Shard
职责：提供文库全量原稿封面巡检、覆盖率统计与一键批量智能配图回填。
🛡️ [SOP-01] 物理行数严格保持在 300 行以内。
"""

import os
from typing import Optional, List, Any
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel

from core.runtime.engine_singleton import get_global_engine
from core.design.image_hub import image_hub
from core.utils.tracing import tlog
from core.utils.text import parse_frontmatter, inject_frontmatter
from services.api.logic.content_ops_shards.safe_ops import resolve_safe_path

router = APIRouter()

def verify_token(x_token: Optional[str] = Header(None, alias="X-Token")) -> None:
    """验证 API 访问令牌"""
    engine = get_global_engine()
    if not engine or not getattr(engine, 'config', None) or not getattr(engine.config, 'system', None) or not getattr(engine.config.system, 'api_token', None):
        return
    if x_token != engine.config.system.api_token:
        raise HTTPException(status_code=403, detail="Unauthorized")

class BatchGenerateRequest(BaseModel):
    doc_ids: List[str]
    strategy: Optional[str] = "og_card"
    aspect_ratio: Optional[str] = "16:9"

def _is_valid_cover(cover_val: Any) -> bool:
    """判断封面属性是否有效存在"""
    if not cover_val:
        return False
    s = str(cover_val).strip().lower()
    return s not in ("", "null", "none", "undefined", "false")

@router.get("/api/design/batch/uncovered-docs", dependencies=[Depends(verify_token)])
async def get_uncovered_docs_report():
    """
    🔍 文库全量原稿封面巡检端点：
    返回全库文档总数、已配图数、待配图清单与整体覆盖率。
    """
    engine = get_global_engine()
    if not engine:
        raise HTTPException(status_code=500, detail="系统引擎未初始化")

    vault_root = getattr(engine, "vault_root", os.getcwd())
    if not os.path.isdir(vault_root):
        return {
            "total_count": 0,
            "covered_count": 0,
            "uncovered_count": 0,
            "coverage_rate": "0.0%",
            "uncovered_docs": []
        }

    total_docs = 0
    covered_docs = 0
    uncovered_items = []

    for root, dirs, files in os.walk(vault_root):
        # 排除系统级与隐藏目录
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("node_modules", "dist", "build")]
        for f in sorted(files):
            if not f.endswith(".md"):
                continue
            fp = os.path.join(root, f)
            rel_path = os.path.relpath(fp, vault_root)
            total_docs += 1

            try:
                with open(fp, "r", encoding="utf-8", errors="ignore") as s:
                    raw = s.read()
                meta, pure_text, _ = parse_frontmatter(raw)
                cover_val = meta.get("cover") or meta.get("banner") or meta.get("image") or ""
                
                if _is_valid_cover(cover_val):
                    covered_docs += 1
                else:
                    # 提取简短首段作为摘要
                    snippet = ""
                    lines = [ln.strip() for ln in pure_text.splitlines() if ln.strip() and not ln.strip().startswith("#")]
                    if lines:
                        snippet = lines[0][:100]

                    uncovered_items.append({
                        "doc_id": rel_path,
                        "title": meta.get("title") or os.path.splitext(f)[0],
                        "category": meta.get("category") or "General",
                        "tags": meta.get("tags") or [],
                        "snippet": snippet
                    })
            except Exception as e:
                tlog.warning(f"⚠️ [BatchCover] 解析文档元数据失败: {rel_path} ({e})")

    uncovered_count = len(uncovered_items)
    rate = f"{(covered_docs / total_docs * 100):.1f}%" if total_docs > 0 else "100.0%"

    return {
        "total_count": total_docs,
        "covered_count": covered_docs,
        "uncovered_count": uncovered_count,
        "coverage_rate": rate,
        "uncovered_docs": uncovered_items
    }

@router.post("/api/design/batch/generate-and-apply", dependencies=[Depends(verify_token)])
async def batch_generate_and_apply_covers(req: BatchGenerateRequest):
    """
    ⚡ 批量生成并应用封面端点：
    根据指定策略为一批文档快速生成封面，自动落盘、写回 Frontmatter 并同步账本。
    """
    engine = get_global_engine()
    if not engine:
        raise HTTPException(status_code=500, detail="系统引擎未初始化")

    target_ids = req.doc_ids or []
    if not target_ids:
        return {"success": True, "applied_count": 0, "failed_count": 0, "items": []}

    vault_root = getattr(engine, "vault_root", os.getcwd())
    image_hub.vault_root = vault_root
    image_hub.cache_dir = os.path.join(vault_root, ".plenipes", "cache", "covers")
    os.makedirs(image_hub.cache_dir, exist_ok=True)

    brand_id = getattr(engine, "imprint_id", "default") or "default"
    brand_name = getattr(engine, "brand_name", "ILLACME SOVEREIGN") or "ILLACME SOVEREIGN"

    applied_items = []
    failed_items = []

    for doc_id in target_ids:
        abs_path = resolve_safe_path(engine, doc_id)
        if not abs_path or not os.path.isfile(abs_path):
            if not doc_id.endswith(".md"):
                abs_path = resolve_safe_path(engine, doc_id + ".md")
        
        if not abs_path or not os.path.isfile(abs_path):
            failed_items.append({"doc_id": doc_id, "reason": "原稿物理文件不存在"})
            continue

        rel_path = os.path.relpath(abs_path, vault_root)

        try:
            with open(abs_path, "r", encoding="utf-8") as f:
                raw_content = f.read()

            metadata, pure_content, _ = parse_frontmatter(raw_content)
            title = metadata.get("title") or os.path.splitext(os.path.basename(rel_path))[0]
            slug = metadata.get("slug") or os.path.splitext(os.path.basename(rel_path))[0]
            author = metadata.get("author") or "Illacme Plenipes"
            category = metadata.get("category") or "Engineering"

            # 1. 调用图像中枢生成封面
            rel_url, img_bytes, used_strat = image_hub.generate_cover_for_document(
                doc_id=rel_path,
                title=title,
                slug=slug,
                author=author,
                category=category,
                brand_id=brand_id,
                brand_name=brand_name,
                strategy=req.strategy or "og_card",
                aspect_ratio=req.aspect_ratio or "16:9"
            )

            # 2. 注入原稿 Frontmatter
            metadata["cover"] = rel_url
            new_content = inject_frontmatter(pure_content, metadata)

            with open(abs_path, "w", encoding="utf-8") as f:
                f.write(new_content)

            # 3. 实时同步 SQLite 数据库元数据缓存
            if hasattr(engine, "meta") and getattr(engine.meta, "sqlite", None):
                try:
                    engine.meta.sqlite.update_document_metadata(rel_path, {"cover": rel_url})
                except Exception as se:
                    tlog.warning(f"⚠️ [BatchCover] 同步 SQLite 缓存异常 (已跳过): {se}")

            # 4. 登记视觉资产物权记录
            image_hub.record_visual_asset(
                meta_manager=getattr(engine, "meta", None),
                rel_path=rel_url,
                asset_type="cover",
                strategy=used_strat,
                source_url=rel_url,
                prompt=f"Auto batch cover for {title}"
            )

            applied_items.append({
                "doc_id": rel_path,
                "title": title,
                "cover_url": rel_url,
                "strategy": used_strat
            })
            tlog.info(f"✨ [BatchCover] 成功装配封面: 《{title}》 -> {rel_url} ({used_strat})")

        except Exception as e:
            tlog.error(f"🛑 [BatchCover] 装配封面失败: {rel_path} ({e})")
            failed_items.append({"doc_id": rel_path, "reason": str(e)})

    return {
        "success": True,
        "applied_count": len(applied_items),
        "failed_count": len(failed_items),
        "strategy": req.strategy or "og_card",
        "items": applied_items,
        "failed_items": failed_items,
        "message": f"批量装配完成：成功 {len(applied_items)} 篇，失败 {len(failed_items)} 篇"
    }

@router.post("/api/design/batch/heal-missing-covers", dependencies=[Depends(verify_token)])
async def heal_missing_covers_endpoint():
    """
    🩹 文库破损与缺失封面批量自愈修复端点：
    自动扫描全库 Markdown 原稿，为所有引用的本地封面缺失文件 JIT 生成并落盘补齐。
    """
    from .cover_asset_healer import heal_missing_covers_in_vault
    engine = get_global_engine()
    vault_root = getattr(engine, "vault_root", os.getcwd()) if engine else os.getcwd()
    result = heal_missing_covers_in_vault(vault_root)
    return {
        "success": True,
        **result,
        "message": f"封面自愈扫描完成：共扫描 {result['scanned']} 篇文章，成功补齐自愈 {result['healed_count']} 个缺失封面"
    }

