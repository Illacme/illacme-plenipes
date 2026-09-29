# -*- coding: utf-8 -*-
"""
📚 [V125.5] Gov Bindery Archive & Batch ZIP Export Route
职责：承载文库数字出版物（EPUB, PDF, WebBook, Markdown, DOCX）批量打包与 ZIP 归档直传。
架构：严格遵循工业主权架构与防路径遍历安全红线，单文件行数严格 ≤ 300 行。
"""

import os
import io
import zipfile
import datetime
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from fastapi.responses import StreamingResponse

from core.runtime.engine_singleton import get_global_engine
from ..system import verify_token

router = APIRouter()

SUPPORTED_EXTS = {".epub", ".pdf", ".html", ".md", ".docx", ".txt"}


def _get_safe_book_path(file: str) -> str:
    """严格断言文件名物理锚定在 dist/books 目录之内"""
    safe_name = os.path.basename(file.strip())
    if not safe_name or safe_name != file:
        raise HTTPException(status_code=400, detail=f"非法的书籍文件名: {file}")
    ext = os.path.splitext(safe_name)[1].lower()
    if ext not in SUPPORTED_EXTS:
        raise HTTPException(status_code=400, detail=f"不支持打包的文件格式: {ext}")
    base_dir = os.path.abspath("dist/books")
    target_path = os.path.abspath(os.path.join(base_dir, safe_name))
    if not target_path.startswith(base_dir + os.sep) or not os.path.isfile(target_path):
        raise HTTPException(status_code=404, detail=f"出版物文件未找到: {safe_name}")
    return target_path


def _generate_manifest_text(files_with_paths: List[tuple], publisher: str) -> str:
    """生成正式出版级归档清单 MANIFEST.txt"""
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        "=" * 80,
        "ILLACME PLENIPES · DIGITAL PUBLICATION ARCHIVE BUNDLE",
        "=" * 80,
        f"Exported At : {now_str}",
        f"Publisher   : {publisher}",
        f"Total Books : {len(files_with_paths)} item(s)",
        "",
        "-" * 80,
        "INCLUDED PUBLICATIONS & VOLUMES:",
        "-" * 80,
    ]
    total_bytes = 0
    for idx, (fn, full_p) in enumerate(files_with_paths, 1):
        sz = os.path.getsize(full_p) if os.path.exists(full_p) else 0
        total_bytes += sz
        sz_str = f"{sz / 1024:.1f} KB" if sz < 1024 * 1024 else f"{sz / (1024*1024):.2f} MB"
        lines.append(f"{idx:2d}. {fn} ({sz_str})")

    tot_sz_str = f"{total_bytes / 1024:.1f} KB" if total_bytes < 1024 * 1024 else f"{total_bytes / (1024*1024):.2f} MB"
    lines.extend([
        "",
        f"Total Archive Size: {tot_sz_str}",
        "",
        "Generated via Illacme Plenipes Sovereign Publishing Engine.",
        "=" * 80,
    ])
    return "\n".join(lines) + "\n"


def _create_zip_stream(files_with_paths: List[tuple], publisher: str) -> io.BytesIO:
    """将书籍物理文件与 Manifest 打包至内存 ZIP 流"""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        # 1. 写入 MANIFEST.txt
        manifest_content = _generate_manifest_text(files_with_paths, publisher)
        zf.writestr("MANIFEST.txt", manifest_content.encode("utf-8"))

        # 2. 依次归档书籍产物
        for fname, full_path in files_with_paths:
            zf.write(full_path, arcname=fname)

    buffer.seek(0)
    return buffer


def _resolve_books_to_pack(filenames: Optional[List[str]], scope: Optional[str]) -> List[tuple]:
    """统一解析待打包的书籍列表"""
    base_dir = os.path.abspath("dist/books")
    if not os.path.exists(base_dir):
        raise HTTPException(status_code=400, detail="出版物存储目录 dist/books 尚不存在。")

    resolved: List[tuple] = []
    if scope == "all" or (not filenames and not scope):
        # 打包当前目录下的所有合法电子书
        for f in sorted(os.listdir(base_dir)):
            p = os.path.join(base_dir, f)
            if os.path.isfile(p) and os.path.splitext(f)[1].lower() in SUPPORTED_EXTS:
                resolved.append((f, p))
    elif filenames:
        for fn in filenames:
            if not isinstance(fn, str) or not fn.strip():
                continue
            path = _get_safe_book_path(fn.strip())
            resolved.append((os.path.basename(path), path))

    if not resolved:
        raise HTTPException(status_code=400, detail="未指定有效的出版物，或所选出版物均不存在。")

    return resolved


@router.post("/api/bindery/export-zip", dependencies=[Depends(verify_token)])
async def export_books_batch_zip(payload: Dict[str, Any] = Body(...)):
    """📦 批量打包已选出版物为 ZIP 合辑 (POST)"""
    filenames = payload.get("filenames")
    scope = payload.get("scope")
    if not filenames and not scope:
        raise HTTPException(status_code=400, detail="请传入待导出的文件名列表 filenames 或 scope='all'。")

    books = _resolve_books_to_pack(filenames, scope)
    engine = get_global_engine()
    site_name = "Illacme Plenipes"
    if engine and hasattr(engine, "config"):
        site_name = getattr(engine.config, "site_name", site_name)
    pub_name = f"{site_name} Sovereign Bindery"

    zip_buffer = _create_zip_stream(books, pub_name)
    now_tag = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    bundle_name = f"illacme-books-bundle-{now_tag}.zip"

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="{bundle_name}"',
            "Cache-Control": "no-cache, no-store",
            "X-Bundle-Count": str(len(books))
        }
    )


@router.get("/api/bindery/export-zip")
async def export_books_batch_zip_get(
    files: Optional[str] = Query(None, description="逗号分隔的文件名列表"),
    scope: Optional[str] = Query(None, description="scope=all 表示全选"),
    token: Optional[str] = Query(None, description="认证 Token")
):
    """📦 批量打包已选出版物为 ZIP 合辑 (GET 直链下载)"""
    filenames = [f.strip() for f in files.split(",") if f.strip()] if files else None
    books = _resolve_books_to_pack(filenames, scope)

    engine = get_global_engine()
    site_name = "Illacme Plenipes"
    if engine and hasattr(engine, "config"):
        site_name = getattr(engine.config, "site_name", site_name)
    pub_name = f"{site_name} Sovereign Bindery"

    zip_buffer = _create_zip_stream(books, pub_name)
    now_tag = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    bundle_name = f"illacme-books-bundle-{now_tag}.zip"

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="{bundle_name}"',
            "Cache-Control": "no-cache, no-store",
            "X-Bundle-Count": str(len(books))
        }
    )
