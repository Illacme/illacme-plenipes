# -*- coding: utf-8 -*-
"""
📂 Illacme Plenipes Content Operations Shard - vault_file_ops
职责：承载物理目录创建、删除、文档搬迁移动、附件上传及 Slug 生成等文件系统级原子操作。
符合 SOP-02 模块拆分协议与 300 行核心复杂度红线。
"""

import os
import shutil
import datetime
import pathlib
import uuid
import re
import unicodedata

from core.utils.text import inject_frontmatter
from services.api.logic.content_ops_shards.safe_ops import resolve_safe_path


def create_document_logic(engine, req: dict):
    """新建原稿：安全名格式化、创建时间 frontmatter 模板注入与新文件保存注册"""
    if not engine:
        return {"error": "Engine not initialized"}

    doc_id = req.get("doc_id", "").strip()
    title = req.get("title", "").strip()
    if not doc_id:
        return {"error": "物理路径不能为空"}

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
    if not engine:
        return {"error": "Engine not initialized"}

    dir_id = req.get("dir_id", "").strip()
    if not dir_id:
        return {"error": "物理目录路径不能为空"}

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
    if not engine:
        return {"error": "Engine not initialized"}

    dir_id = req.get("dir_id", "").strip()
    if not dir_id:
        return {"error": "物理目录路径不能为空"}
    if dir_id in [".", "/", ""]:
        return {"error": "权限拒绝：不允许删除文库根目录"}

    abs_path = resolve_safe_path(engine, dir_id)
    if not abs_path:
        return {"error": "权限拒绝：检测到非法的物理路径穿越指令"}

    if not os.path.exists(abs_path):
        return {"error": "删除失败：目标物理目录不存在"}
    if not os.path.isdir(abs_path):
        return {"error": "删除失败：目标路径不是一个有效的目录"}

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
    if not engine:
        return {"error": "Engine not initialized"}

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
    if not engine:
        return {"error": "Engine not initialized"}

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
    if not engine:
        return {"slug": ""}
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
