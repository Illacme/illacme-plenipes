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
        
    # 🚀 [V100.0] 双层物理一致性自愈：即时重塑物理索引与语义知识图谱节点，确保 3D 图谱完美同步刷新
    try:
        from core.editorial.vault_indexer import VaultIndexer
        from core.ingress.language_sentinel import LanguageSentinel
        
        # 解析最新物理文件索引
        mtime = os.path.getmtime(abs_path)
        detected_lang = LanguageSentinel.detect_language(full_content, os.path.basename(doc_id))
        links = VaultIndexer.extract_links(full_content)
        meta = VaultIndexer._quick_parse_meta(full_content)
        meta["size"] = len(full_content)
        meta["mtime"] = mtime
        meta["lang"] = detected_lang
        
        if hasattr(engine, "link_graph"):
            engine.link_graph[doc_id] = {"links": links, "metadata": meta}
            
        if hasattr(engine, "knowledge_graph"):
            actual_title = title or meta.get("title") or os.path.splitext(os.path.basename(doc_id))[0]
            engine.knowledge_graph.upsert_node(doc_id, actual_title)
            engine.knowledge_graph.save()
    except Exception as ex:
        # 避免在异常时中断正常保存流程，只作静默防抖
        pass

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
        
    # 智能相对路径解析：若新路径包含相对上一级等跳转符号 (..)，以当前原稿所属文件夹为基准进行寻址换算
    is_relative_resolved = False
    if ".." in new_path:
        old_dir = os.path.dirname(doc_id)
        new_path = os.path.normpath(os.path.join(old_dir, new_path))
        is_relative_resolved = True
        
    # 智能对正：如果 new_path 只是一个纯文件名（不含斜杠），默认重命名到旧文件的同级文件夹下
    if not is_relative_resolved and "/" not in new_path and "\\" not in new_path:
        old_dir = os.path.dirname(doc_id)
        new_path = os.path.join(old_dir, new_path) if old_dir else new_path
        
    new_path = new_path.replace("\\", "/")
    
    # 智能目录锚定：若规范化后的 new_path 指向文库中已有的一个物理目录文件夹，则自动附加原文件名作为目标
    vault_root_abs = os.path.abspath(engine.vault_root)
    dest_temp_abs = os.path.abspath(os.path.join(vault_root_abs, new_path))
    if os.path.exists(dest_temp_abs) and os.path.isdir(dest_temp_abs):
        new_path = os.path.join(new_path, os.path.basename(doc_id)).replace("\\", "/")
        
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
def get_galaxy_graph(mode: str = "full"):
    engine = get_global_engine()
    if not engine:
        return {"nodes": [], "links": []}
    
    # 🪐 [混合渐进式] 静态骨架模式
    if mode == "skeleton":
        nodes_list = []
        links_list = []
        seen_links = set()
        
        if not hasattr(engine, "link_graph") or not engine.link_graph:
            return {"nodes": [], "links": []}
            
        for rel_path, data in engine.link_graph.items():
            meta = data.get("metadata", {})
            nodes_list.append({
                "id": rel_path,
                "title": meta.get("title") or os.path.splitext(os.path.basename(rel_path))[0],
                "val": 1.0,
                "group": "document",
                "is_skeleton": True
            })
            for target in data.get("links", []):
                resolved = engine.meta.resolve_link(target)
                if resolved:
                    target_key = resolved
                else:
                    target_key = target
                    if target not in engine.link_graph:
                        for k in engine.link_graph:
                            if os.path.basename(k) == target or os.path.splitext(os.path.basename(k))[0] == target:
                                target_key = k
                                break
                link_id = tuple(sorted([rel_path, target_key]))
                if link_id not in seen_links:
                    seen_links.add(link_id)
                    links_list.append({
                        "source": rel_path,
                        "target": target_key,
                        "strength": 1.0,
                        "type": "wikilink",
                        "is_manual": False,
                        "is_skeleton": True
                    })
        return {"nodes": nodes_list, "links": links_list}
        
    # 🪐 [混合渐进式] 全量高维图模式 (合并物理 WikiLinks 与 AI 语义/用户手动连线)
    else:
        if not hasattr(engine, "knowledge_graph"):
            return {"nodes": [], "links": []}
            
        kg_graph = engine.knowledge_graph.get_galaxy_graph()
        nodes_map = {n["id"]: n for n in kg_graph.get("nodes", [])}
        for n in nodes_map.values():
            n["is_skeleton"] = False
            n["group"] = "document"
            
        # 合并物理节点
        if hasattr(engine, "link_graph") and engine.link_graph:
            for rel_path, data in engine.link_graph.items():
                meta = data.get("metadata", {})
                title = meta.get("title") or os.path.splitext(os.path.basename(rel_path))[0]
                if rel_path not in nodes_map:
                    nodes_map[rel_path] = {
                        "id": rel_path,
                        "title": title,
                        "val": 1.0,
                        "group": "document",
                        "is_skeleton": True
                    }
                else:
                    nodes_map[rel_path]["is_skeleton"] = True
                    # 🚀 [V100.0] 双重对齐保险：强制对齐最新物理 title 属性，打破缓存在 full 模式下的遮蔽缺陷
                    nodes_map[rel_path]["title"] = title
                    
        # 合并连线：物理优先 (wikilink 青色优先，避免被 weak semantic 紫色连线遮蔽)
        links_list = []
        seen_links = set()
        
        # 1. 先合并物理 Wikilink 连线
        if hasattr(engine, "link_graph") and engine.link_graph:
            for rel_path, data in engine.link_graph.items():
                for target in data.get("links", []):
                    resolved = engine.meta.resolve_link(target)
                    if resolved:
                        target_key = resolved
                    else:
                        target_key = target
                        if target not in engine.link_graph:
                            for k in engine.link_graph:
                                if os.path.basename(k) == target or os.path.splitext(os.path.basename(k))[0] == target:
                                    target_key = k
                                    break
                    if rel_path in nodes_map and target_key in nodes_map:
                        link_id = tuple(sorted([rel_path, target_key]))
                        if link_id not in seen_links:
                            seen_links.add(link_id)
                            links_list.append({
                                "source": rel_path,
                                "target": target_key,
                                "strength": 1.0,
                                "type": "wikilink",
                                "is_manual": False,
                                "is_skeleton": True
                            })
                            
        # 2. 再合并语义与用户手动连线 (如果尚未存在物理连线的话)
        for l in kg_graph.get("links", []):
            src = l["source"]
            tgt = l["target"]
            link_id = tuple(sorted([src, tgt]))
            if link_id not in seen_links:
                seen_links.add(link_id)
                links_list.append({
                    "source": src,
                    "target": tgt,
                    "strength": l.get("strength", 0.5),
                    "type": l.get("type", "semantic"),
                    "is_manual": l.get("is_manual", False),
                    "is_skeleton": False
                })
        return {"nodes": list(nodes_map.values()), "links": links_list}

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
