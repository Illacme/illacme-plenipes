# -*- coding: utf-8 -*-
"""
📂 Illacme Plenipes Content Operations Shard - vault_ops
职责：承载物理稿件与目录的 CRUD 安全核心逻辑、 SQLite 元数据更新及自愈注册。
符合 SOP-02 模块拆分协议与 300 行核心复杂度红线。
"""

import os
import shutil
import datetime
import pathlib
import uuid

from core.utils.text import parse_frontmatter, inject_frontmatter
from services.api.logic.content_ops_shards.safe_ops import resolve_safe_path


def search_vault_logic(engine, q: str = "", page: int = 1, limit: int = 50, folder: str = ""):
    """🚀 [V55.0] 联邦检索入口：服务于 Dashboard Vault 视图"""
    if not engine: return {"error": "Engine not initialized"}
    docs = engine.meta.sqlite.list_documents_paginated(page, limit, query=q, folder=folder)
    total = engine.meta.sqlite.get_documents_count_filtered(query=q, folder=folder)
    return {"items": docs, "total": total}


def get_document_detail_logic(engine, doc_id: str):
    """获取文档详情：查询 SQLite 元数据 + 物理文件读取 + frontmatter 解析"""
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


def update_document_metadata_logic(engine, doc_id: str, req: dict):
    """SQLite 核心元数据更新接口"""
    if not engine: return {"error": "Engine not initialized"}
    result = engine.meta.sqlite.update_document_metadata(doc_id, req)

    # 🛡️ [Slug 冲突透传] 底层检测到 slug 被其他文档占用时，返回冲突 dict 而非 bool。
    # 此处将其转化为 API 层可识别的 error 响应，前端据此弹出有意义的提示。
    if isinstance(result, dict) and result.get("conflict"):
        occupied_by = result.get("occupied_by", "?")
        slug = result.get("slug", "?")
        return {
            "success": False,
            "error": f"Slug 冲突：「{slug}」已被文档 '{occupied_by}' 占用，请更换其他 Slug。",
            "error_code": "SLUG_CONFLICT",
            "occupied_by": occupied_by
        }
    return {"success": bool(result)}


def save_document_logic(engine, doc_id: str, req: dict):
    """原稿保存：frontmatter 注入与物理磁盘写入"""
    if not engine: return {"error": "Engine not initialized"}

    # 🛡️ [安全防线] 拦截非法 doc_id，防止产生物理 'null'/'undefined' 脏资产文件
    if not doc_id or doc_id.strip() in ("", "null", "undefined", "None"):
        return {"success": False, "error": "非法的原稿文件路径名称"}

    content = req.get("content", "")
    metadata = req.get("frontmatter", {})
    title, slug = req.get("title"), req.get("slug")

    # 🛡️ [Slug 唯一性守卫] 物理存盘时也必须通过冲突校验，防止脑裂冲突
    if slug:
        conn = engine.meta.sqlite._get_conn()
        conflict_row = conn.execute(
            "SELECT rel_path FROM documents WHERE slug = ? AND rel_path != ?",
            (slug, doc_id)
        ).fetchone()
        if conflict_row:
            conflict_path = dict(conflict_row).get("rel_path", "?")
            return {
                "success": False,
                "error": f"Slug 冲突：「{slug}」已被文档 '{conflict_path}' 占用，请更换其他 Slug。",
                "error_code": "SLUG_CONFLICT",
                "occupied_by": conflict_path
            }

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

    # 物理计算字数与自愈元数据更新
    import re
    try:
        clean_text = re.sub(r'[\s\n\t]+', ' ', full_content)
        en_words = len(re.findall(r'[a-zA-Z0-9\-\']+', clean_text))
        zh_chars = len(re.findall(r'[\u4e00-\u9fa5]', full_content))
        word_count = en_words + zh_chars
    except Exception:
        word_count = 0

    doc_info = engine.meta.get_doc_info(doc_id) or {}
    seo_data = doc_info.get("seo_data") or {}
    seo_data["word_count"] = word_count

    engine.meta.register_document(
        doc_id,
        title or doc_info.get("title") or os.path.splitext(os.path.basename(doc_id))[0],
        slug=slug,
        seo_data=seo_data
    )

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
            engine.knowledge_graph.save(debounce=False)
    except Exception:
        # 避免在异常时中断正常保存流程，只作静默防抖
        pass

    return {"success": True}


def create_document_logic(engine, req: dict):
    """新建原稿：安全名格式化、创建时间 frontmatter 模板注入与新文件保存注册"""
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


def create_directory_logic(engine, req: dict):
    """物理目录多级安全创建"""
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


def delete_directory_logic(engine, req: dict):
    """空白目录检验及多级安全删除"""
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


def move_document_logic(engine, req: dict):
    """智能相对路径换算、重命名对正、锚定已有目录，物理稿件平移及 SQLite 元数据平滑继承"""
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

def upload_asset_logic(engine, doc_id: str, file_bytes: bytes, filename: str):
    """编辑器物理附件自动归档机制"""
    if not engine: return {"error": "Engine not initialized"}
    
    doc_dir = os.path.dirname(doc_id) if doc_id else ""
    assets_dir = os.path.join(doc_dir, "assets")
    
    base, ext = os.path.splitext(filename)
    unique_filename = f"{base}_{uuid.uuid4().hex[:6]}{ext}"
    rel_path = os.path.join(assets_dir, unique_filename).replace("\\", "/")
    
    abs_path = resolve_safe_path(engine, rel_path)
    if not abs_path:
        return {"error": "权限拒绝：非法的物理存放路径"}
        
    try:
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        with open(abs_path, 'wb') as f:
            f.write(file_bytes)
    except Exception as e:
        return {"error": f"物理磁盘资产写入失败: {e}"}
        
    return {"success": True, "asset_path": rel_path}


def generate_slug_logic(engine, title: str):
    """通过大模型或规则物理计算得出 URL 友好的 Slug，支持多语种转写与拉丁化自愈"""
    if not engine: return {"slug": ""}
    slug = ""
    success = False
    try:
        from core.logic.ai.ai_factory import TranslatorFactory
        translator = TranslatorFactory.create(engine.config.translation)
        if translator:
            slug, success = translator.generate_slug(title)
    except Exception as e:
        from core.utils.tracing import tlog
        tlog.warning(f"⚠️ [Generate Slug] AI 生成失败，降级至规则: {e}")
    if not success or not slug:
        slug = fallback_slugify(title)
    return {"success": True, "slug": slug}


def fallback_slugify(text: str) -> str:
    """非英文国家语种的拉丁化去变音与自愈兜底"""
    import unicodedata
    import re
    clean = unicodedata.normalize('NFKD', text)
    clean = clean.encode('ascii', 'ignore').decode('utf-8')
    clean = clean.lower().strip().replace(" ", "-").replace("_", "-")
    clean = re.sub(r'[^a-z0-9\-]', '', clean)
    clean = re.sub(r'-+', '-', clean).strip('-')
    if not clean:
        clean = text.lower().strip().replace(" ", "-").replace("_", "-")
        clean = re.sub(r'[^\w\-\/]', '', clean)
        clean = re.sub(r'-+', '-', clean).strip('-')
    return clean
