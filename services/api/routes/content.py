"""
📝 内容路由 — RESTful API 内容管理端点。
提供文章/资产的 CRUD 操作接口，服务于 TerritoryWizard 与外部集成。
🔗 [SOP-02] 业务逻辑已物理降解至 core.api.logic.content_ops，本文件仅保留路由映射与依赖注入。
"""
# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import FileResponse
from core.runtime.engine_singleton import get_global_engine
from .system import verify_token
from services.api.logic.content_ops import (search_vault_logic,
    get_document_detail_logic, update_document_metadata_logic,
    save_document_logic, create_document_logic,
    create_directory_logic, delete_directory_logic,
    move_document_logic, get_galaxy_graph_logic, get_vault_asset_logic,
    upload_asset_logic, rebuild_node_semantics_logic, generate_slug_logic)

router = APIRouter()

# 🔗 [SOP-02] resolve_safe_path 已物理迁移至 core.api.logic.content_ops
# 通过顶部 import 桥接引入，此处不再重复定义

@router.get("/api/vault/search", dependencies=[Depends(verify_token)])
def search_vault(q: str = "", page: int = 1, limit: int = 50, folder: str = ""):
    """🚀 [V55.0] 联邦检索入口：服务于 Dashboard Vault 视图"""
    engine = get_global_engine()
    return search_vault_logic(engine, q, page, limit, folder)

@router.get("/ledger/document/{doc_id:path}", dependencies=[Depends(verify_token)])
def get_document_detail(doc_id: str):
    engine = get_global_engine()
    return get_document_detail_logic(engine, doc_id)

@router.post("/ledger/document/{doc_id:path}/save", dependencies=[Depends(verify_token)])
async def save_document(doc_id: str, req: dict):
    engine = get_global_engine()
    return save_document_logic(engine, doc_id, req)

@router.post("/ledger/document/create", dependencies=[Depends(verify_token)])
async def create_document(req: dict):
    engine = get_global_engine()
    return create_document_logic(engine, req)

@router.post("/api/vault/generate-slug", dependencies=[Depends(verify_token)])
async def generate_slug_route(req: dict):
    engine = get_global_engine()
    title = req.get("title", "").strip()
    return generate_slug_logic(engine, title)

@router.post("/ledger/directory/create", dependencies=[Depends(verify_token)])
async def create_directory(req: dict):
    engine = get_global_engine()
    return create_directory_logic(engine, req)

@router.post("/ledger/directory/delete", dependencies=[Depends(verify_token)])
async def delete_directory(req: dict):
    engine = get_global_engine()
    return delete_directory_logic(engine, req)

@router.post("/ledger/document/{doc_id:path}/metadata", dependencies=[Depends(verify_token)])
async def update_document_metadata(doc_id: str, req: dict):
    engine = get_global_engine()
    return update_document_metadata_logic(engine, doc_id, req)

@router.post("/ledger/document/move", dependencies=[Depends(verify_token)])
async def move_document(req: dict):
    engine = get_global_engine()
    return move_document_logic(engine, req)

@router.post("/ledger/assets/upload", dependencies=[Depends(verify_token)])
async def upload_asset(doc_id: str = Form(""), file: UploadFile = File(...)):
    engine = get_global_engine()
    file_bytes = await file.read()
    return upload_asset_logic(engine, doc_id, file_bytes, file.filename)

@router.get("/api/galaxy/graph", dependencies=[Depends(verify_token)])
def get_galaxy_graph(mode: str = "full"):
    engine = get_global_engine()
    return get_galaxy_graph_logic(engine, mode)

@router.get("/api/vault-assets/{asset_path:path}", dependencies=[Depends(verify_token)])
def get_vault_asset(asset_path: str, relative_to: str = None):
    """
    🖼️ 物理文库原件资产服务网关
    支持图片、PDF 等各类本地多媒体附件的安全分发，集成库内平铺检索自愈以支持 Obsidian 缩写链。
    """
    engine = get_global_engine()
    result = get_vault_asset_logic(engine, asset_path, relative_to)
    if isinstance(result, dict):
        return result
    return FileResponse(result)


@router.post("/api/galaxy/link", dependencies=[Depends(verify_token)])
async def add_manual_link_route(req: dict):
    engine = get_global_engine()
    src = req.get("src")
    target = req.get("target")
    if not src or not target:
        return {"status": "error", "message": "Missing src or target"}
    if not hasattr(engine, "knowledge_graph"):
        return {"status": "error", "message": "Knowledge graph not initialized"}
    engine.knowledge_graph.add_manual_link(src, target)
    return {"status": "success"}


@router.post("/api/galaxy/unlink", dependencies=[Depends(verify_token)])
async def remove_manual_link_route(req: dict):
    engine = get_global_engine()
    src = req.get("src")
    target = req.get("target")
    if not src or not target:
        return {"status": "error", "message": "Missing src or target"}
    if not hasattr(engine, "knowledge_graph"):
        return {"status": "error", "message": "Knowledge graph not initialized"}
    
    if hasattr(engine.knowledge_graph, "remove_link"):
        engine.knowledge_graph.remove_link(src, target)
    else:
        with engine.knowledge_graph._lock:
            for p, c in [(src, target), (target, src)]:
                if p in engine.knowledge_graph.nodes:
                    node = engine.knowledge_graph.nodes[p]
                    if "connections" in node and c in node["connections"]:
                        del node["connections"][c]
                    if "manual_connections" in node and c in node["manual_connections"]:
                        del node["manual_connections"][c]
            engine.knowledge_graph.save()
    return {"status": "success"}


@router.post("/api/galaxy/rebuild-node", dependencies=[Depends(verify_token)])
async def rebuild_node_semantics_route(req: dict):
    engine = get_global_engine()
    doc_id = req.get("doc_id")
    if not doc_id:
        return {"status": "error", "message": "Missing doc_id"}
    return rebuild_node_semantics_logic(engine, doc_id)

