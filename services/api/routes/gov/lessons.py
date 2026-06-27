# -*- coding: utf-8 -*-
"""
🧠 [V50.3] Gov Brain Lessons Learned Routes
职责：提供 AI 翻译及验证失败所沉淀教训的大盘统计与详情接口。
SOP-01: 单文件 300 行限额，逻辑独立分流。
"""
from fastapi import APIRouter, Depends
from typing import Optional
from core.runtime.engine_singleton import get_global_engine
from services.api.routes.system import verify_token

router = APIRouter()

@router.get("/api/governance/lessons/summary", dependencies=[Depends(verify_token)])
def get_lessons_summary() -> dict:
    """获取教训大盘的汇总数据"""
    engine = get_global_engine()
    if not engine:
        return {"error": "Engine not initialized"}
    try:
        lessons = engine.brain.lessons
        category_counts = {}
        for l in lessons:
            cat = l.get("category", "UNKNOWN")
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        labels = engine.brain.USER_LABELS
        return {
            "total": len(lessons),
            "category_counts": category_counts,
            "labels": labels,
            "summary": engine.brain.get_summary()
        }
    except Exception as e:
        return {"error": f"Failed to get lessons summary: {str(e)}"}

@router.get("/api/governance/lessons", dependencies=[Depends(verify_token)])
def get_lessons(category: Optional[str] = None) -> dict:
    """获取教训流水详情列表"""
    engine = get_global_engine()
    if not engine:
        return {"error": "Engine not initialized"}
    try:
        lessons = engine.brain.lessons
        if category and category != "all":
            lessons = [l for l in lessons if l.get("category") == category]
        
        sorted_lessons = sorted(lessons, key=lambda x: x.get("timestamp", ""), reverse=True)
        return {"lessons": sorted_lessons}
    except Exception as e:
        return {"error": f"Failed to fetch lessons: {str(e)}"}
