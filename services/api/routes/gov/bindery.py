# -*- coding: utf-8 -*-
"""
📚 [V125.0] Gov Bindery & EBook Export Routes
职责：承载文库数字出版物（EPUB 3.0）装订编排、范围勘测与安全防越权下载。
架构：遵循工业主权架构，单文件行数严格 ≤ 300 行。
"""

import os
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from core.runtime.engine_singleton import get_global_engine
from core.bindery.book_assembler import BookAssembler
from core.bindery.cover_generator import CoverGenerator, COVER_STYLES
from core.adapters.egress.ebook import EBookRegistry
from ..system import verify_token

router = APIRouter()


class BinderyBuildPayload(BaseModel):
    """数字装订编排请求载荷"""
    format: str = Field(default="epub", description="装订输出格式")
    scope: str = Field(default="all", description="合卷范围：all 或 具体栏目子目录")
    lang: str = Field(default="zh", description="目标语言代码")
    title: Optional[str] = Field(default=None, description="自定义书名")
    author: Optional[str] = Field(default=None, description="自定义作者/出版署名")
    cover_mode: str = Field(default="auto", description="封面策略: auto, generated, none")
    cover_style: str = Field(default="dark_emerald", description="装帧封面风格")
    output_dir: str = Field(default="dist/books", description="物理落盘相对目录")


class CoverPreviewPayload(BaseModel):
    """封面实时预览请求载荷"""
    title: Optional[str] = Field(default=None, description="书名")
    author: Optional[str] = Field(default=None, description="作者")
    scope: str = Field(default="all", description="栏目范围")
    style: str = Field(default="dark_emerald", description="风格ID")
    lang: str = Field(default="zh", description="语种代码")
    cover_mode: str = Field(default="auto", description="封面模式")


@router.get("/api/bindery/scopes", dependencies=[Depends(verify_token)])
async def get_bindery_scopes() -> Dict[str, Any]:
    """🚀 [V125.0] 装订范围勘测：获取当前文库可供合订的目录栏目与默认出版元数据"""
    engine = get_global_engine()
    vault_root = getattr(engine, "vault_root", "vault") if engine else "vault"
    vault_abs = os.path.abspath(vault_root)

    # 1. 勘测一级物理子目录栏目
    categories: List[Dict[str, str]] = [{"id": "all", "name": "全部原稿 (全库总集)"}]
    if os.path.exists(vault_abs):
        for item in sorted(os.listdir(vault_abs)):
            p = os.path.join(vault_abs, item)
            if os.path.isdir(p) and not item.startswith("."):
                has_md = any(f.endswith(".md") for _, _, files in os.walk(p) for f in files)
                if has_md:
                    categories.append({"id": item, "name": f"{item} (独立栏目册)"})

    # 2. 提取支持的格式
    formats = []
    for fmt_id in EBookRegistry.get_all_names():
        cls_ = EBookRegistry.get_adapter(fmt_id)
        name = getattr(cls_, "DISPLAY_NAME", fmt_id.upper())
        ext = getattr(cls_, "OUTPUT_EXTENSION", f".{fmt_id}")
        formats.append({"id": fmt_id, "name": name, "ext": ext, "recommended": (fmt_id == "epub")})

    # 3. 提取品牌预设出版元数据
    site_name = "Illacme Plenipes"
    default_author = "Illacme Editorial Team"
    default_lang = "zh"
    if engine and hasattr(engine, "config"):
        site_name = getattr(engine.config, "site_name", site_name)
        author_cfg = getattr(engine.config, "author", None)
        if isinstance(author_cfg, dict):
            default_author = author_cfg.get("name") or default_author
        elif isinstance(author_cfg, str) and author_cfg:
            default_author = author_cfg

    # 4. 探测文库是否有原生封面图片及风格预设
    has_native_cover = bool(CoverGenerator.discover_cover(vault_abs))
    styles_list = [
        {"id": k, "name": v["name"], "accent": v["accent"]}
        for k, v in COVER_STYLES.items()
    ]

    return {
        "success": True,
        "site_name": site_name,
        "default_author": default_author,
        "default_lang": default_lang,
        "has_native_cover": has_native_cover,
        "cover_styles": styles_list,
        "categories": categories,
        "formats": formats
    }


@router.post("/api/bindery/cover-preview", dependencies=[Depends(verify_token)])
async def get_cover_preview(payload: CoverPreviewPayload) -> Dict[str, Any]:
    """🚀 [V125.0] 封面实时预览：毫秒级生成排版封面或提取文库原生封面 DataURL"""
    engine = get_global_engine()
    vault_root = getattr(engine, "vault_root", "vault") if engine else "vault"
    vault_abs = os.path.abspath(vault_root)

    site_name = "Illacme Plenipes"
    if engine and hasattr(engine, "config"):
        site_name = getattr(engine.config, "site_name", site_name)

    cat_scope = "" if payload.scope == "all" else payload.scope
    title = payload.title or f"{site_name} · 数字出版集"
    author = payload.author or "Illacme Editorial Team"
    pub_name = f"{site_name} Global Private Press"

    if payload.cover_mode == "none":
        return {"success": True, "mode": "none", "data_uri": None}

    # 尝试原生封面
    if payload.cover_mode == "auto":
        native_p = CoverGenerator.discover_cover(vault_abs, category=cat_scope)
        if native_p and os.path.exists(native_p):
            try:
                import mimetypes
                import base64
                mime, _ = mimetypes.guess_type(native_p)
                mime = mime or "image/jpeg"
                with open(native_p, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode("ascii")
                return {
                    "success": True,
                    "mode": "native",
                    "filename": os.path.basename(native_p),
                    "data_uri": f"data:{mime};base64,{b64}"
                }
            except Exception:
                pass

    # 降级或指定生成排版艺术封面
    data_uri = CoverGenerator.generate_cover_data_uri(
        title=title,
        author=author,
        publisher=pub_name,
        style_key=payload.style,
        lang=payload.lang
    )
    return {
        "success": True,
        "mode": "generated",
        "style": payload.style,
        "data_uri": data_uri
    }


@router.post("/api/bindery/build", dependencies=[Depends(verify_token)])
async def build_ebook_publication(payload: BinderyBuildPayload) -> Dict[str, Any]:
    """🚀 [V125.0] 执行合卷装订：生成标准数字出版物实体并返回下载信息"""
    engine = get_global_engine()
    vault_root = getattr(engine, "vault_root", "vault") if engine else "vault"
    vault_abs = os.path.abspath(vault_root)

    if not os.path.exists(vault_abs):
        raise HTTPException(status_code=400, detail="文库目录不存在，无法执行装订。")

    assembler = BookAssembler(engine=engine, vault_dir=vault_abs)
    scope_cat = "" if payload.scope == "all" else payload.scope

    out_path = assembler.assemble_and_bind(
        category=scope_cat,
        format_type=payload.format,
        target_lang=payload.lang,
        custom_title=payload.title,
        custom_author=payload.author,
        cover_mode=payload.cover_mode,
        cover_style=payload.cover_style,
        output_dir=payload.output_dir
    )

    if not out_path or not os.path.exists(out_path):
        raise HTTPException(status_code=500, detail="电子书装订合成失败，未发现有效产物。")

    filename = os.path.basename(out_path)
    file_size = os.path.getsize(out_path)

    # 统计章节数
    chapters = assembler._collect_chapters(category=scope_cat, target_lang=payload.lang)
    chapter_count = len(chapters)

    return {
        "success": True,
        "filename": filename,
        "file_size": file_size,
        "chapter_count": chapter_count,
        "format": payload.format,
        "download_url": f"/api/bindery/download?file={filename}",
        "message": f"数字装订完成！共收录 {chapter_count} 篇章节，已封装为标准 {payload.format.upper()} 出版物。"
    }


@router.get("/api/bindery/download")
async def download_ebook_publication(file: str = Query(..., description="待下载的装订文件名")):
    """
    🚀 [V125.0] 数字出版物安全下载通道
    🛡️ SOP-04 安全红线：严格防范目录穿越 (Directory Traversal) 与非受权读取。
    """
    # 1. 提取纯文件名，杜绝任何路径分割符与 .. 攻击
    safe_filename = os.path.basename(file.strip())
    if not safe_filename or safe_filename != file:
        raise HTTPException(status_code=400, detail="非法的下载请求参数。")

    # 2. 物理锚定产物白名单目录 (dist/books)
    base_books_dir = os.path.abspath("dist/books")
    target_abs_path = os.path.abspath(os.path.join(base_books_dir, safe_filename))

    # 3. 严格断言目标必须在 base_books_dir 之内
    if not target_abs_path.startswith(base_books_dir + os.sep):
        raise HTTPException(status_code=403, detail="主权防御：拒绝越权访问。")

    if not os.path.isfile(target_abs_path):
        raise HTTPException(status_code=404, detail="请求的出版物文件未找到或已被清理。")

    # 4. 根据文件扩展名映射 media_type
    ext = os.path.splitext(safe_filename)[1].lower()
    media_map = {
        ".epub": "application/epub+zip",
        ".pdf": "application/pdf",
        ".mobi": "application/x-mobipocket-ebook",
        ".azw3": "application/vnd.amazon.ebook"
    }
    media_type = media_map.get(ext, "application/octet-stream")

    return FileResponse(
        path=target_abs_path,
        media_type=media_type,
        filename=safe_filename
    )
