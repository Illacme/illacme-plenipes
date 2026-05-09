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
def list_documents(page: int = 1, limit: int = 50, query: str = None):
    engine = get_global_engine()
    if not engine: return {"error": "Engine not initialized"}
    # 🚀 [V52.0] 增强型搜索与分页
    return engine.meta.sqlite.list_documents_paginated(page, limit, query=query)

@router.get("/ledger/document/{doc_id:path}", dependencies=[Depends(verify_token)])
def get_document_detail(doc_id: str):
    engine = get_global_engine()
    if not engine: return {"error": "Engine not initialized"}
    # 🚀 [V52.1] 支持带斜杠的物理路径 ID
    return engine.meta.sqlite.get_document(doc_id)

@router.post("/ledger/document/{doc_id:path}/save", dependencies=[Depends(verify_token)])
async def save_document(doc_id: str, req: dict):
    engine = get_global_engine()
    if not engine: return {"error": "Engine not initialized"}
    
    content = req.get("content")
    if content is None: return {"error": "Missing content"}
    
    # 🚀 [V51.0] 闭环审计：保存并立即触发语义重新索引
    success = engine.meta.sqlite.update_document_content(doc_id, content)
    if success:
        # 触发后台异步审计任务 (此处简化，实际会加入队列)
        from core.logic.orchestration.task_orchestrator import global_executor
        global_executor.submit_task("audit", doc_id=doc_id)
        
    return {"success": success}

@router.post("/ledger/document/{doc_id:path}/metadata", dependencies=[Depends(verify_token)])
async def update_document_metadata(doc_id: str, req: dict):
    engine = get_global_engine()
    if not engine: return {"error": "Engine not initialized"}
    
    # 🚀 [V52.0] 局部元数据注入
    success = engine.meta.sqlite.update_document_metadata(doc_id, req)
    return {"success": success}

@router.get("/api/galaxy/graph", dependencies=[Depends(verify_token)])
def get_galaxy_graph():
    engine = get_global_engine()
    if not engine or not hasattr(engine, "knowledge_graph"):
        return {"nodes": [], "links": []}
    
    return engine.knowledge_graph.get_galaxy_graph()
