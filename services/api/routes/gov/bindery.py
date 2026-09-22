# -*- coding: utf-8 -*-
"""
📚 [V125.0] Gov Bindery & EBook Export Routes
职责：承载文库数字出版物（EPUB 3.0）装订编排、范围勘测与安全防越权下载。
架构：遵循工业主权架构，单文件行数严格 ≤ 300 行。
"""

import os
import base64
import mimetypes
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel

from core.runtime.engine_singleton import get_global_engine
from core.bindery.book_assembler import BookAssembler
from core.bindery.cover_generator import CoverGenerator, COVER_STYLES
from core.adapters.egress.ebook import EBookRegistry
from ..system import verify_token

router = APIRouter()


class BinderyBuildPayload(BaseModel):
    """数字装订编排请求载荷"""
    format: str = "epub"
    scope: str = "all"
    lang: str = "zh"
    languages: Optional[List[str]] = None
    polyglot_mode: bool = False
    title: Optional[str] = None
    author: Optional[str] = None
    cover_mode: str = "auto"
    cover_style: str = "dark_emerald"
    output_dir: str = "dist/books"


class CoverPreviewPayload(BaseModel):
    """封面实时预览请求载荷"""
    title: Optional[str] = None
    author: Optional[str] = None
    scope: str = "all"
    style: str = "dark_emerald"
    lang: str = "zh"
    cover_mode: str = "auto"


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
    styles_list = [{"id": k, "name": v["name"], "accent": v["accent"]} for k, v in COVER_STYLES.items()]

    # 5. 勘测多语言资产覆盖矩阵
    avail_langs = [{"code": default_lang, "name": "简体中文", "icon": "🇨🇳", "count": 0, "is_source": True}]
    if os.path.exists(vault_abs):
        c_cnt = 0
        for _, ds, fs in os.walk(vault_abs):
            ds[:] = [d for d in ds if not d.startswith('.')]
            c_cnt += sum(1 for f in fs if f.endswith('.md') and not f.startswith('.'))
        avail_langs[0]["count"] = c_cnt
    db_p = os.path.join(vault_abs, ".plenipes/cache/ledger.db")
    L_META = {"en": ("English", "🇬🇧"), "ja": ("日本語", "🇯🇵"), "fr": ("Français", "🇫🇷"), "de": ("Deutsch", "🇩🇪"), "es": ("Español", "🇪🇸"), "ru": ("Русский", "🇷🇺"), "ko": ("한국어", "🇰🇷")}
    if os.path.exists(db_p):
        try:
            import sqlite3
            with sqlite3.connect(db_p) as c:
                for lc, cnt in c.execute("SELECT lang_code, count(*) FROM translations WHERE status = 'DONE' GROUP BY lang_code"):
                    if lc != default_lang:
                        nm, ic = L_META.get(lc, (lc.upper(), "🌐"))
                        avail_langs.append({"code": lc, "name": nm, "icon": ic, "count": cnt, "is_source": False})
        except Exception: pass

    return {
        "success": True,
        "site_name": site_name,
        "default_author": default_author,
        "default_lang": default_lang,
        "available_languages": avail_langs,
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
                mime, _ = mimetypes.guess_type(native_p)
                with open(native_p, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode("ascii")
                return {"success": True, "mode": "native", "filename": os.path.basename(native_p), "data_uri": f"data:{mime or 'image/jpeg'};base64,{b64}"}
            except Exception: pass

    data_uri = CoverGenerator.generate_cover_data_uri(
        title=title, author=author, publisher=pub_name,
        style_key=payload.style, lang=payload.lang
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

    target_langs = payload.languages if (payload.languages and len(payload.languages) > 0) else [payload.lang]

    if payload.polyglot_mode and len(target_langs) >= 2:
        out_p = assembler.assemble_and_bind(
            category=scope_cat, format_type=payload.format, target_lang=target_langs[0],
            custom_title=payload.title, custom_author=payload.author,
            cover_mode=payload.cover_mode, cover_style=payload.cover_style,
            output_dir=payload.output_dir, polyglot_langs=target_langs
        )
        if not out_p or not os.path.exists(out_p):
            raise HTTPException(status_code=500, detail="多语平行对照典籍装订失败，未生成有效产物。")
        fn, fs = os.path.basename(out_p), os.path.getsize(out_p)
        return {
            "success": True, "mode": "polyglot", "filename": fn, "file_size": fs, "format": payload.format,
            "languages": target_langs, "download_url": f"/api/bindery/download?file={fn}",
            "message": f"🎉 多语平行对照典籍装订完成！涵盖 {len(target_langs)} 门语言平行矩阵，已封装为高质感 {payload.format.upper()} 出版物。"
        }

    if len(target_langs) == 1:
        s_lang = target_langs[0]
        out_path = assembler.assemble_and_bind(
            category=scope_cat, format_type=payload.format, target_lang=s_lang,
            custom_title=payload.title, custom_author=payload.author,
            cover_mode=payload.cover_mode, cover_style=payload.cover_style, output_dir=payload.output_dir
        )
        if not out_path or not os.path.exists(out_path):
            raise HTTPException(status_code=500, detail="电子书装订合成失败，未发现有效产物。")

        filename, file_size = os.path.basename(out_path), os.path.getsize(out_path)
        chapters = assembler._collect_chapters(category=scope_cat, target_lang=s_lang)
        return {
            "success": True, "filename": filename, "file_size": file_size, "chapter_count": len(chapters),
            "format": payload.format, "download_url": f"/api/bindery/download?file={filename}",
            "message": f"数字装订完成！共收录 {len(chapters)} 篇章节，已封装为标准 {payload.format.upper()} 出版物。"
        }

    # 多语种矩阵模式：批量装订套系丛书
    matrix_results = []
    for l_code in target_langs:
        out_p = assembler.assemble_and_bind(
            category=scope_cat, format_type=payload.format, target_lang=l_code,
            custom_title=payload.title, custom_author=payload.author,
            cover_mode=payload.cover_mode, cover_style=payload.cover_style, output_dir=payload.output_dir
        )
        if out_p and os.path.exists(out_p):
            fn, fs = os.path.basename(out_p), os.path.getsize(out_p)
            chs = assembler._collect_chapters(category=scope_cat, target_lang=l_code)
            matrix_results.append({
                "lang": l_code, "language": l_code, "filename": fn, "file_size": fs, "size_bytes": fs,
                "chapter_count": len(chs), "format": payload.format, "download_url": f"/api/bindery/download?file={fn}"
            })

    if not matrix_results:
        raise HTTPException(status_code=500, detail="多语种矩阵出版装订失败，未生成有效产物。")

    return {
        "success": True, "mode": "matrix", "total_built": len(matrix_results), "results": matrix_results,
        "format": payload.format, "message": f"🎉 多语种典籍矩阵出版完成！共生成 {len(matrix_results)} 册出版物。"
    }


def _get_safe_book_path(file: str) -> str:
    """提取纯文件名并严格断言物理锚定在 dist/books 目录之内"""
    safe_name = os.path.basename(file.strip())
    if not safe_name or safe_name != file:
        raise HTTPException(status_code=400, detail="非法的请求参数。")
    base_dir = os.path.abspath("dist/books")
    target_path = os.path.abspath(os.path.join(base_dir, safe_name))
    if not target_path.startswith(base_dir + os.sep) or not os.path.isfile(target_path):
        raise HTTPException(status_code=404, detail="请求的出版物文件未找到或已被清理。")
    return target_path


@router.get("/api/bindery/download")
async def download_ebook_publication(file: str = Query(..., description="待下载文件名")):
    target = _get_safe_book_path(file)
    ext = os.path.splitext(file)[1].lower()
    media_map = {".epub": "application/epub+zip", ".html": "text/html", ".pdf": "application/pdf"}
    return FileResponse(path=target, media_type=media_map.get(ext, "application/octet-stream"), filename=file)


@router.get("/api/bindery/view")
async def view_ebook_webbook(file: str = Query(...)):
    target = _get_safe_book_path(file)
    if not file.lower().endswith(".html"): raise HTTPException(status_code=400, detail="仅支持 WebBook HTML 在线翻阅。")
    with open(target, "r", encoding="utf-8") as f:
        return Response(
            content=f.read(),
            media_type="text/html; charset=utf-8",
            headers={"Cache-Control": "no-cache, no-store, must-revalidate", "Pragma": "no-cache"}
        )


@router.get("/api/bindery/shelf", dependencies=[Depends(verify_token)])
async def get_bindery_shelf() -> Dict[str, Any]:
    """📚 出版典籍货架：扫描并返回已编译的所有装订产物"""
    base_dir, books = os.path.abspath("dist/books"), []
    if os.path.exists(base_dir):
        for fname in sorted(os.listdir(base_dir)):
            p = os.path.join(base_dir, fname)
            if os.path.isfile(p) and fname.endswith(('.epub', '.html', '.pdf')):
                st = os.stat(p)
                fmt = "webbook" if fname.endswith(".html") else ("epub" if fname.endswith(".epub") else "other")
                sz_str = f"{st.st_size / 1024:.1f} KB" if st.st_size < 1024 * 1024 else f"{st.st_size / (1024*1024):.2f} MB"
                books.append({
                    "filename": fname, "format": fmt, "size_bytes": st.st_size, "size_display": sz_str, "mtime": st.st_mtime,
                    "download_url": f"/api/bindery/download?file={fname}", "preview_url": f"/api/bindery/view?file={fname}" if fmt == "webbook" else None
                })
        books.sort(key=lambda x: x["mtime"], reverse=True)
    return {"success": True, "books": books, "count": len(books)}


@router.post("/api/bindery/delete", dependencies=[Depends(verify_token)])
async def delete_ebook_from_shelf(payload: Dict[str, str] = Body(...)) -> Dict[str, Any]:
    """🪓 从出版货架中归档删除指定书籍产物"""
    target = _get_safe_book_path(payload.get("filename", ""))
    try:
        os.remove(target)
        return {"success": True, "message": "出版物已成功移除。"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除失败: {e}")

