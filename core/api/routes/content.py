"""
📝 内容路由 — RESTful API 内容管理端点。
提供文章/资产的 CRUD 操作接口，服务于 TerritoryWizard 与外部集成。
"""
# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends
from core.runtime.engine_singleton import get_global_engine
from .system import verify_token
from core.utils.text import parse_frontmatter, inject_frontmatter

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
        except Exception: pass

    # 🌓 [V68.0] 原子化拆解：分离元数据与纯正文
    metadata, pure_content, has_fm = parse_frontmatter(content)
    doc["content"] = pure_content
    doc["frontmatter"] = metadata
    doc["has_frontmatter"] = has_fm
    
    return doc

@router.post("/ledger/document/{doc_id:path}/save", dependencies=[Depends(verify_token)])
async def save_document(doc_id: str, req: dict):
    engine = get_global_engine()
    if not engine: return {"error": "Engine not initialized"}
    
    content = req.get("content", "")
    metadata = req.get("frontmatter", {})
    
    # 🚀 [V68.0] 主权注入逻辑
    # 场景 1 & 2 闭环处理：确保物理文件的 YAML 头部与右侧表单对齐
    title = req.get("title")
    slug = req.get("slug")
    
    if title: metadata["title"] = title
    if slug: metadata["slug"] = slug
    
    # 执行缝合
    full_content = inject_frontmatter(content, metadata)

    import os
    abs_path = os.path.join(engine.vault_root, doc_id)
    
    # 真实保存到物理文件
    try:
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        with open(abs_path, 'w', encoding='utf-8') as f:
            f.write(full_content)
    except Exception as e:
        return {"error": f"Failed to write physical file: {e}"}
        
    # 同步更新索引库
    if title is not None or slug is not None:
        engine.meta.register_document(doc_id, title, slug=slug)
    
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

@router.get("/api/vault-assets/{asset_path:path}", dependencies=[Depends(verify_token)])
def get_vault_asset(asset_path: str, relative_to: str = None):
    """
    🖼️ 物理文库原件资产服务网关
    支持图片、PDF 等各类本地多媒体附件的安全分发，集成库内平铺检索自愈以支持 Obsidian 缩写链。
    """
    from fastapi.responses import FileResponse
    import os
    import urllib.parse
    
    engine = get_global_engine()
    if not engine:
        return {"error": "Engine not initialized"}
        
    vault_root_abs = os.path.abspath(engine.vault_root)
    
    # 🚀 高能对齐：物理原件名称 Percent-Decoding 并剥离可能存在的 Query/Hash 伪指令
    decoded_asset_path = urllib.parse.unquote(asset_path).split('?')[0].split('#')[0]
    decoded_relative_to = urllib.parse.unquote(relative_to) if relative_to else None
    
    # 1. 尝试以相对路径计算物理定位
    full_asset_path = decoded_asset_path
    if decoded_relative_to:
        doc_dir = os.path.dirname(decoded_relative_to)
        full_asset_path = os.path.join(doc_dir, decoded_asset_path)
        
    abs_path = os.path.abspath(os.path.join(vault_root_abs, full_asset_path))
    
    # 2. 安全合规审计：防止路径穿越 (Directory Traversal Bypass)
    if not abs_path.startswith(vault_root_abs):
        return {"error": "Access denied"}
        
    # 3. 自愈探测：如果相对寻址落空，在全库（Vault Root）中执行文件名自愈搜索
    if not os.path.exists(abs_path) or os.path.isdir(abs_path):
        filename = os.path.basename(decoded_asset_path)
        found = False
        for root, _, files in os.walk(vault_root_abs):
            if filename in files:
                abs_path = os.path.join(root, filename)
                found = True
                break
        if not found:
            return {"error": "Asset file not found"}
            
    return FileResponse(abs_path)
