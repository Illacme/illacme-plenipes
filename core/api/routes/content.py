"""
📝 内容路由 — RESTful API 内容管理端点。
提供文章/资产的 CRUD 操作接口，服务于 TerritoryWizard 与外部集成。
"""
# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends
from core.runtime.engine_singleton import get_global_engine
from .system import verify_token

router = APIRouter()

@router.get("/api/vault/search", dependencies=[Depends(verify_token)])
def search_vault(q: str = "", page: int = 1, limit: int = 50):
    """🚀 [V55.0] 联邦检索入口：服务于 Dashboard Vault 视图"""
    engine = get_global_engine()
    if not engine: return {"error": "Engine not initialized"}
    # 🛡️ [V74.10] 物理契约对正：前端 dashboard.vault.js 依赖 res.items 结构
    docs = engine.meta.sqlite.list_documents_paginated(page, limit, query=q)
    return {"items": docs}

@router.get("/ledger/document/{doc_id:path}", dependencies=[Depends(verify_token)])
def get_document_detail(doc_id: str):
    engine = get_global_engine()
    if not engine: return {"error": "Engine not initialized"}
    # 🚀 [V52.1] 支持带斜杠的物理路径 ID
    doc = engine.meta.sqlite.get_document(doc_id)
    if not doc:
        return {"error": "Document not found"}
    
    # 物理读取
    import os
    abs_path = os.path.join(engine.vault_root, doc_id)
    content = ""
    if os.path.exists(abs_path):
        try:
            with open(abs_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception:
            pass
    doc["content"] = content
    return doc

@router.post("/ledger/document/{doc_id:path}/save", dependencies=[Depends(verify_token)])
async def save_document(doc_id: str, req: dict):
    engine = get_global_engine()
    if not engine: return {"error": "Engine not initialized"}
    
    content = req.get("content")
    if content is None: return {"error": "Missing content"}

    import os
    abs_path = os.path.join(engine.vault_root, doc_id)
    
    # 真实保存到物理文件
    try:
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        with open(abs_path, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        return {"error": f"Failed to write physical file: {e}"}
        
    # 保存标题和slug等属性
    title = req.get("title")
    slug = req.get("slug")
    if title is not None or slug is not None:
        # 触发 metadata_json 的更新
        engine.meta.register_document(doc_id, title, slug=slug)
    
    # 🚀 [V51.0] 闭环审计：物理保存与元数据注册已完成
    return {"success": True}

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
