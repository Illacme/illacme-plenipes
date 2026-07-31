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
        lessons = engine.brain.lessons if isinstance(engine.brain.lessons, list) else []
        category_counts = {}
        for l in lessons:
            if isinstance(l, dict):
                cat = l.get("category", "UNKNOWN")
                category_counts[cat] = category_counts.get(cat, 0) + 1
        
        labels = getattr(engine.brain, "USER_LABELS", {})
        return {
            "total": len(lessons),
            "category_counts": category_counts,
            "labels": labels,
            "summary": engine.brain.get_summary() if hasattr(engine.brain, 'get_summary') else {}
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
        lessons = engine.brain.lessons if isinstance(engine.brain.lessons, list) else []
        if category and category != "all":
            lessons = [l for l in lessons if isinstance(l, dict) and l.get("category") == category]
        
        valid_lessons = [l for l in lessons if isinstance(l, dict)]
        sorted_lessons = sorted(valid_lessons, key=lambda x: x.get("timestamp", ""), reverse=True)
        return {"lessons": sorted_lessons}
    except Exception as e:
        return {"error": f"Failed to fetch lessons: {str(e)}"}

@router.delete("/api/governance/lessons/clear", dependencies=[Depends(verify_token)])
def clear_lessons() -> dict:
    """一键清空自愈教训历史库"""
    engine = get_global_engine()
    if not engine:
        return {"error": "Engine not initialized"}
    try:
        if hasattr(engine.brain, 'lessons') and isinstance(engine.brain.lessons, list):
            engine.brain.lessons.clear()
        if hasattr(engine.brain, 'save_lessons'):
            engine.brain.save_lessons()
        return {"success": True, "message": "自愈教训库已成功清空"}
    except Exception as e:
        return {"error": f"Failed to clear lessons: {str(e)}"}

@router.post("/api/governance/lessons/seed", dependencies=[Depends(verify_token)])
def seed_lessons() -> dict:
    """生成测试模拟 AI 自愈教训条目并记录入库"""
    import datetime
    engine = get_global_engine()
    if not engine:
        return {"error": "Engine not initialized"}
    try:
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        sample_lessons = [
            {
                "category": "SOVEREIGNTY_SHIELD",
                "error": "探测到未公开配置的本地私有文库凭据路径",
                "context": {"path": "vault/secret/keys.yaml", "action": "自动屏蔽落盘，降级隔离"},
                "timestamp": now_iso
            },
            {
                "category": "LINK_REPAIR",
                "error": "发现坏链超链接 (404/Relative Anchor Mismatch)",
                "context": {"path": "tech/guide/install.md", "action": "智能自愈映射至规范 Slug"},
                "timestamp": now_iso
            },
            {
                "category": "MASK_INTEGRITY",
                "error": "Markdown 代码块标签缺失未闭合",
                "context": {"path": "journal/2026/dev.md", "action": "自动补全闭合语法标点"},
                "timestamp": now_iso
            }
        ]
        
        if hasattr(engine.brain, 'lessons') and isinstance(engine.brain.lessons, list):
            engine.brain.lessons.extend(sample_lessons)
        if hasattr(engine.brain, 'save_lessons'):
            engine.brain.save_lessons()
            
        return {"success": True, "added": len(sample_lessons), "message": f"成功注入 {len(sample_lessons)} 条测试自愈教训"}
    except Exception as e:
        return {"error": f"Failed to seed lessons: {str(e)}"}
