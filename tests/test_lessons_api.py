# -*- coding: utf-8 -*-
import pytest
from unittest.mock import MagicMock
from services.api.routes.gov.lessons import get_lessons_summary, get_lessons

@pytest.mark.anyio
async def test_get_lessons_summary_api(monkeypatch):
    """测试获取教训大盘汇总 API"""
    engine = MagicMock()
    brain = MagicMock()
    
    brain.lessons = [
        {"category": "MASK_INTEGRITY", "error": "test mask err"},
        {"category": "SOVEREIGNTY_SHIELD", "error": "test sovereignty err"},
        {"category": "MASK_INTEGRITY", "error": "another mask err"},
    ]
    brain.USER_LABELS = {
        "MASK_INTEGRITY": "AI 幻觉拦截 & 格式自愈",
        "SOVEREIGNTY_SHIELD": "核心资产/品牌标签保护"
    }
    brain.get_summary.return_value = {
        "total_lessons": 3,
        "recent_failures": ["another mask err"],
        "categories": ["MASK_INTEGRITY", "SOVEREIGNTY_SHIELD"]
    }
    engine.brain = brain
    
    monkeypatch.setattr("services.api.routes.gov.lessons.get_global_engine", lambda: engine)
    
    res = get_lessons_summary()
    assert "total" in res
    assert res["total"] == 3
    assert res["category_counts"]["MASK_INTEGRITY"] == 2
    assert res["category_counts"]["SOVEREIGNTY_SHIELD"] == 1
    assert "labels" in res
    assert res["labels"]["MASK_INTEGRITY"] == "AI 幻觉拦截 & 格式自愈"

@pytest.mark.anyio
async def test_get_lessons_api(monkeypatch):
    """测试获取教训列表详情 API"""
    engine = MagicMock()
    brain = MagicMock()
    brain.lessons = [
        {"category": "MASK_INTEGRITY", "error": "test mask err", "timestamp": "2026-06-27T10:00:00"},
        {"category": "SOVEREIGNTY_SHIELD", "error": "test sovereignty err", "timestamp": "2026-06-27T11:00:00"},
    ]
    engine.brain = brain
    
    monkeypatch.setattr("services.api.routes.gov.lessons.get_global_engine", lambda: engine)
    
    res_all = get_lessons()
    assert len(res_all["lessons"]) == 2
    assert res_all["lessons"][0]["category"] == "SOVEREIGNTY_SHIELD"
    
    res_filtered = get_lessons(category="MASK_INTEGRITY")
    assert len(res_filtered["lessons"]) == 1
    assert res_filtered["lessons"][0]["error"] == "test mask err"
