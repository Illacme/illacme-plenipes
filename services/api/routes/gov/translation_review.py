# -*- coding: utf-8 -*-
"""
🔒 [I5] Translation Human Review Routes
职责：翻译人工校对回流 API 端点注册。
架构：遵循 SOP-02 职责分离，业务逻辑委派至 context_shards/review_ops.py。
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from core.runtime.engine_singleton import get_global_engine

from .context_shards.review_ops import (
    get_translation_snapshot_impl,
    save_human_review_impl,
    unlock_human_review_impl,
)

router = APIRouter(prefix="/api/translation/review", tags=["Translation Review"])


class ParagraphItem(BaseModel):
    index: int
    type: str   # "paragraph" | "callout" | "code"
    text: str


class SaveReviewRequest(BaseModel):
    doc_id: str
    lang_code: str
    paragraphs: List[ParagraphItem]
    title: Optional[str] = None
    desc: Optional[str] = None


class UnlockReviewRequest(BaseModel):
    doc_id: str
    lang_code: str


@router.get("/{doc_id:path}")
async def get_review_snapshot(doc_id: str):
    """
    GET /api/translation/review/{doc_id}
    获取文档所有已翻译语种的快照（含锁定状态、段落分割列表）。
    数据来源：MetadataManager 账本（Q6=B）。
    """
    engine = get_global_engine()
    if not engine:
        raise HTTPException(status_code=503, detail="Engine not initialized")
    
    # 🛡️ [安全拦截] AI 算力关闭时，禁止访问译文校对接口
    enable_ai = getattr(engine.config.translation, "enable_ai", False) if engine.config.translation else False
    if not enable_ai:
        raise HTTPException(status_code=400, detail="🛡️ [主权拦截] AI 算力当前处于关闭状态，译文校对工作台不可用。")

    result = get_translation_snapshot_impl(engine, doc_id)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result


@router.post("/save")
async def save_review(req: SaveReviewRequest):
    """
    POST /api/translation/review/save
    保存人工校对结果并上锁（语种级，Q2=A）。
    存储 SSG 渲染前中间态 Markdown（Q4=A）。
    """
    engine = get_global_engine()
    if not engine:
        raise HTTPException(status_code=503, detail="Engine not initialized")
    
    # 🛡️ [安全拦截] AI 算力关闭时，禁止访问译文校对接口
    enable_ai = getattr(engine.config.translation, "enable_ai", False) if engine.config.translation else False
    if not enable_ai:
        raise HTTPException(status_code=400, detail="🛡️ [主权拦截] AI 算力当前处于关闭状态，译文校对工作台不可用。")

    result = save_human_review_impl(
        engine,
        doc_id=req.doc_id,
        lang_code=req.lang_code,
        paragraphs=[p.dict() for p in req.paragraphs],
        title=req.title,
        desc=req.desc,
    )
    if not result.get("ok"):
        raise HTTPException(status_code=500, detail=result.get("error", "Save failed"))
    return result


@router.post("/unlock")
async def unlock_review(req: UnlockReviewRequest):
    """
    POST /api/translation/review/unlock
    手动解除校对锁（用户主动操作，重置为 AI 重译）。
    """
    engine = get_global_engine()
    if not engine:
        raise HTTPException(status_code=503, detail="Engine not initialized")
    
    enable_ai = getattr(engine.config.translation, "enable_ai", False) if engine.config.translation else False
    if not enable_ai:
        raise HTTPException(status_code=400, detail="🛡️ [主权拦截] AI 算力当前处于关闭状态，译文校对工作台不可用。")

    result = unlock_human_review_impl(engine, doc_id=req.doc_id, lang_code=req.lang_code)
    if not result.get("ok"):
        raise HTTPException(status_code=500, detail=result.get("error", "Unlock failed"))
    return result


class RetranslateParagraphRequest(BaseModel):
    doc_id: str
    lang_code: str
    para_index: int
    source_text: str


@router.post("/retranslate-paragraph")
async def retranslate_paragraph(req: RetranslateParagraphRequest):
    """
    POST /api/translation/review/retranslate-paragraph
    微粒度单段落 AI 重译接口。
    """
    engine = get_global_engine()
    if not engine:
        raise HTTPException(status_code=503, detail="Engine not initialized")
    
    enable_ai = getattr(engine.config.translation, "enable_ai", False) if engine.config.translation else False
    if not enable_ai:
        raise HTTPException(status_code=400, detail="🛡️ [主权拦截] AI 算力当前处于关闭状态。")

    from .context_shards.review_ops import retranslate_paragraph_impl
    result = retranslate_paragraph_impl(
        engine,
        doc_id=req.doc_id,
        lang_code=req.lang_code,
        para_index=req.para_index,
        source_text=req.source_text
    )
    if not result.get("ok"):
        raise HTTPException(status_code=500, detail=result.get("error", "Retranslation failed"))
    return result
