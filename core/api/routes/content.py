"""
📝 内容路由 — RESTful API 内容管理端点。
提供文章/资产的 CRUD 操作接口，服务于 TerritoryWizard 与外部集成。
"""
# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends
from core.runtime.cli_bootstrap import get_global_engine
from .system import verify_token

router = APIRouter()

@router.get("/ledger/documents", dependencies=[Depends(verify_token)])
def list_documents(page: int = 1, limit: int = 20):
    engine = get_global_engine()
    if not engine: return {"error": "Engine not initialized"}
    return engine.meta.sqlite.list_documents_paginated(page, limit)

@router.get("/api/galaxy/graph", dependencies=[Depends(verify_token)])
def get_galaxy_graph():
    engine = get_global_engine()
    if not engine or not hasattr(engine, "knowledge_graph"):
        return {"nodes": [], "links": []}
    
    return engine.knowledge_graph.get_galaxy_graph()
