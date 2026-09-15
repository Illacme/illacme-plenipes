# -*- coding: utf-8 -*-
"""
🎨 Design Studio - Asset Upload Routes Shard
职责：提供媒体资产本地图片上传、格式安全校验、哈希防冲突落盘与物权账本登记服务。
🛡️ [SOP-01] 物理行数严格保持在 300 行以内。
"""

import os
import hashlib
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Header, UploadFile, File, Form

from core.runtime.engine_singleton import get_global_engine
from core.utils.tracing import tlog

router = APIRouter()

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".svg", ".gif"}


def verify_token(x_token: Optional[str] = Header(None, alias="X-Token")) -> None:
    """验证 API 访问令牌"""
    engine = get_global_engine()
    if not engine or not getattr(engine, 'config', None) or not getattr(engine.config, 'system', None) or not getattr(engine.config.system, 'api_token', None):
        return
    if x_token != engine.config.system.api_token:
        raise HTTPException(status_code=403, detail="Unauthorized")


@router.post("/api/design/assets/upload", dependencies=[Depends(verify_token)])
async def upload_visual_asset(
    file: UploadFile = File(...),
    prompt: Optional[str] = Form(None)
):
    """
    接收本地上传的媒体图片，物理写入缓存目录并登记至 SQLite 物权账本
    """
    engine = get_global_engine()
    if not engine:
        raise HTTPException(status_code=500, detail="引擎离线未初始化")

    original_filename = os.path.basename(file.filename or "uploaded_image.png")
    _, ext = os.path.splitext(original_filename.lower())
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的图片格式 '{ext}'。仅支持 {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

    try:
        read_res = file.read()
        import inspect
        content = await read_res if inspect.isawaitable(read_res) else read_res
        if not content:
            raise HTTPException(status_code=400, detail="上传的文件内容为空")

        # 计算内容哈希，保障唯一性并避免同名覆盖冲突
        content_hash = hashlib.sha256(content).hexdigest()[:12]
        clean_stem = "".join([c for c in os.path.splitext(original_filename)[0] if c.isalnum() or c in ("-", "_")])
        clean_stem = clean_stem[:30] or "asset"
        stored_filename = f"upload_{clean_stem}_{content_hash}{ext}"

        vault_root = getattr(engine, "vault_root", os.getcwd())
        covers_dir = os.path.join(vault_root, ".plenipes", "cache", "covers")
        os.makedirs(covers_dir, exist_ok=True)
        local_file_path = os.path.join(covers_dir, stored_filename)

        with open(local_file_path, "wb") as f:
            f.write(content)

        source_url = f"/api/design/assets/covers/{stored_filename}"
        rel_path = f".plenipes/cache/covers/{stored_filename}"
        prompt_text = (prompt or f"本地上传: {original_filename}").strip()

        # 登记到 SQLite 物权账本
        asset_id = None
        if hasattr(engine, "meta") and getattr(engine.meta, "sqlite", None):
            try:
                conn = engine.meta.sqlite.get_connection()
                with conn:
                    cur = conn.cursor()
                    cur.execute(
                        """
                        INSERT INTO visual_assets (rel_path, asset_type, strategy, source_url, cdn_url, media_id, prompt)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (rel_path, "image", "manual_upload", source_url, "", "", prompt_text)
                    )
                    asset_id = cur.lastrowid
                tlog.info(f"📤 [设计中心] 本地资产成功入库: #{asset_id} -> {stored_filename}")
            except Exception as e:
                tlog.warning(f"⚠️ [设计中心] 写入资产账本异常: {e}")

        return {
            "success": True,
            "message": f"本地资产已成功入库: {original_filename}",
            "asset_id": asset_id,
            "url": source_url,
            "source_url": source_url,
            "filename": stored_filename,
            "rel_path": rel_path
        }
    except HTTPException:
        raise
    except Exception as e:
        tlog.error(f"❌ [设计中心] 上传本地资产失败: {e}")
        raise HTTPException(status_code=500, detail=f"文件保存或入库失败: {str(e)}")
