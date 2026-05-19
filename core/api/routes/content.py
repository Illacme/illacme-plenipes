"""
📝 内容路由 — RESTful API 内容管理端点。
提供文章/资产的 CRUD 操作接口，服务于 TerritoryWizard 与外部集成。
"""
# -*- coding: utf-8 -*-
import os
import shutil
import datetime
import pathlib
import urllib.parse
from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from core.runtime.engine_singleton import get_global_engine
from .system import verify_token
from core.utils.text import parse_frontmatter, inject_frontmatter

router = APIRouter()

def resolve_safe_path(engine, rel_path: str) -> str:
    """🛡️ L3 级绝对路径穿越防御与物理路径安全收拢"""
    if not rel_path: return ""
    vault_root_abs = os.path.abspath(engine.vault_root)
    abs_path = os.path.abspath(os.path.join(vault_root_abs, rel_path.strip()))
    if not abs_path.startswith(vault_root_abs) or abs_path == vault_root_abs:
        return ""
    return abs_path

@router.get("/api/vault/search", dependencies=[Depends(verify_token)])
def search_vault(q: str = "", page: int = 1, limit: int = 50, folder: str = ""):
    """🚀 [V55.0] 联邦检索入口：服务于 Dashboard Vault 视图"""
    engine = get_global_engine()
    if not engine: return {"error": "Engine not initialized"}
    docs = engine.meta.sqlite.list_documents_paginated(page, limit, query=q, folder=folder)
    return {"items": docs}

@router.get("/ledger/document/{doc_id:path}", dependencies=[Depends(verify_token)])
def get_document_detail(doc_id: str):
    engine = get_global_engine()
    if not engine: return {"error": "Engine not initialized"}
    doc = engine.meta.sqlite.get_document(doc_id)
    if not doc: return {"error": "Document not found"}
    
    abs_path = resolve_safe_path(engine, doc_id)
    content = ""
    if abs_path and os.path.exists(abs_path):
        try:
            with open(abs_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception: pass

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
    title, slug = req.get("title"), req.get("slug")
    
    if title: metadata["title"] = title
    if slug: metadata["slug"] = slug
    full_content = inject_frontmatter(content, metadata)

    abs_path = resolve_safe_path(engine, doc_id)
    if not abs_path:
        return {"error": "权限拒绝：检测到非法的物理路径穿越指令"}
        
    try:
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        with open(abs_path, 'w', encoding='utf-8') as f:
            f.write(full_content)
    except Exception as e:
        return {"error": f"Failed to write physical file: {e}"}
        
    if title is not None or slug is not None:
        engine.meta.register_document(doc_id, title, slug=slug)
    return {"success": True}

@router.post("/ledger/document/create", dependencies=[Depends(verify_token)])
async def create_document(req: dict):
    engine = get_global_engine()
    if not engine: return {"error": "Engine not initialized"}
    
    doc_id = req.get("doc_id", "").strip()
    title = req.get("title", "").strip()
    if not doc_id: return {"error": "物理路径不能为空"}
        
    ext = os.path.splitext(doc_id)[1].lower()
    if ext not in [".md", ".mdx", ".markdown"]:
        doc_id += ".md"
        
    abs_path = resolve_safe_path(engine, doc_id)
    if not abs_path:
        return {"error": "权限拒绝：检测到非法的物理路径穿越指令"}
        
    if os.path.exists(abs_path):
        return {"error": "创建失败：该物理路径下已存在同名原稿文件"}
        
    default_slug = pathlib.Path(doc_id).stem
    now_str = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
    
    metadata = {"title": title or "未命名原稿", "date": now_str, "slug": default_slug}
    initial_content = inject_frontmatter(f"# {title or '未命名原稿'}\n\n在此输入原稿内容...", metadata)
    
    try:
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        with open(abs_path, 'w', encoding='utf-8') as f:
            f.write(initial_content)
    except Exception as e:
        return {"error": f"物理磁盘写入失败: {e}"}
        
    engine.meta.register_document(doc_id, title or "未命名原稿", slug=default_slug)
    return {"success": True, "doc_id": doc_id}

@router.post("/ledger/directory/create", dependencies=[Depends(verify_token)])
async def create_directory(req: dict):
    engine = get_global_engine()
    if not engine: return {"error": "Engine not initialized"}
    
    dir_id = req.get("dir_id", "").strip()
    if not dir_id: return {"error": "物理目录路径不能为空"}
        
    abs_path = resolve_safe_path(engine, dir_id)
    if not abs_path:
        return {"error": "权限拒绝：检测到非法的物理路径穿越指令"}
        
    if os.path.exists(abs_path):
        return {"error": "创建失败：该物理路径已存在"}
        
    try:
        os.makedirs(abs_path, exist_ok=True)
    except Exception as e:
        return {"error": f"物理磁盘目录创建失败: {e}"}
    return {"success": True, "dir_id": dir_id}

@router.post("/ledger/directory/delete", dependencies=[Depends(verify_token)])
async def delete_directory(req: dict):
    engine = get_global_engine()
    if not engine: return {"error": "Engine not initialized"}
    
    dir_id = req.get("dir_id", "").strip()
    if not dir_id: return {"error": "物理目录路径不能为空"}
    if dir_id in [".", "/", ""]: return {"error": "权限拒绝：不允许删除文库根目录"}
        
    abs_path = resolve_safe_path(engine, dir_id)
    if not abs_path:
        return {"error": "权限拒绝：检测到非法的物理路径穿越指令"}
        
    if not os.path.exists(abs_path): return {"error": "删除失败：目标物理目录不存在"}
    if not os.path.isdir(abs_path): return {"error": "删除失败：目标路径不是一个有效的目录"}
        
    try:
        children = os.listdir(abs_path)
        if len(children) > 0:
            return {"error": "删除失败：该目录下包含原稿或子目录，请先清空或转移其中的资产"}
    except Exception as e:
        return {"error": f"物理目录读取失败: {e}"}
        
    try:
        os.rmdir(abs_path)
    except Exception as e:
        return {"error": f"物理磁盘目录删除失败: {e}"}
    return {"success": True, "dir_id": dir_id}

@router.post("/ledger/document/{doc_id:path}/metadata", dependencies=[Depends(verify_token)])
async def update_document_metadata(doc_id: str, req: dict):
    engine = get_global_engine()
    if not engine: return {"error": "Engine not initialized"}
    success = engine.meta.sqlite.update_document_metadata(doc_id, req)
    return {"success": success}

@router.post("/ledger/document/move", dependencies=[Depends(verify_token)])
async def move_document(req: dict):
    engine = get_global_engine()
    if not engine: return {"error": "Engine not initialized"}
    
    doc_id = req.get("doc_id", "").strip()
    new_path = req.get("new_path", "").strip()
    if not doc_id or not new_path:
        return {"error": "原稿路径与新目标路径均不能为空"}
        
    if "/" not in new_path and "\\" not in new_path:
        old_dir = os.path.dirname(doc_id)
        new_path = os.path.join(old_dir, new_path) if old_dir else new_path
        
    new_path = new_path.replace("\\", "/")
    src_abs = resolve_safe_path(engine, doc_id)
    dest_abs = resolve_safe_path(engine, new_path)
    
    if not src_abs or not dest_abs:
        return {"error": "权限拒绝：检测到非法的物理路径穿越指令"}
        
    if not os.path.exists(src_abs):
        return {"error": f"重命名失败：原物理稿件不存在 ({doc_id})"}
    if os.path.exists(dest_abs):
        return {"error": f"重命名失败：目标路径已有同名物理原稿存在，请更换名称以防覆盖损失 ({new_path})"}
        
    doc_info = engine.meta.get_doc_info(doc_id)
    if not doc_info:
        doc_info = {"title": os.path.basename(new_path), "slug": "pending", "source_lang": "zh"}
    else:
        if doc_info.get("title") == os.path.basename(doc_id):
            doc_info["title"] = os.path.basename(new_path)
            
    try:
        os.makedirs(os.path.dirname(dest_abs), exist_ok=True)
        shutil.move(src_abs, dest_abs)
    except Exception as e:
        return {"error": f"物理磁盘稿件搬迁失败: {e}"}
        
    try:
        engine.meta.remove_document(doc_id)
        doc_info_clean = {k: v for k, v in doc_info.items() if k != "title"}
        engine.meta.register_document(new_path, doc_info.get("title") or os.path.basename(new_path), **doc_info_clean)
    except Exception as e:
        return {"success": True, "doc_id": doc_id, "new_path": new_path, "warning": f"SQLite 元数据平滑继承时出现细微抖动: {e}"}
        
    return {"success": True, "doc_id": doc_id, "new_path": new_path}

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
    engine = get_global_engine()
    if not engine: return {"error": "Engine not initialized"}
        
    vault_root_abs = os.path.abspath(engine.vault_root)
    decoded_asset_path = urllib.parse.unquote(asset_path).split('?')[0].split('#')[0]
    decoded_relative_to = urllib.parse.unquote(relative_to) if relative_to else None
    
    full_asset_path = decoded_asset_path
    if decoded_relative_to:
        doc_dir = os.path.dirname(decoded_relative_to)
        full_asset_path = os.path.join(doc_dir, decoded_asset_path)
        
    abs_path = os.path.abspath(os.path.join(vault_root_abs, full_asset_path))
    if not abs_path.startswith(vault_root_abs):
        return {"error": "Access denied"}
        
    if not os.path.exists(abs_path) or os.path.isdir(abs_path):
        filename = os.path.basename(decoded_asset_path)
        found = False
        for root, _, files in os.walk(vault_root_abs):
            if filename in files:
                abs_path = os.path.join(root, filename)
                found = True
                break
        if not found: return {"error": "Asset file not found"}
            
    return FileResponse(abs_path)
