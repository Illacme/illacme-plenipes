# -*- coding: utf-8 -*-
"""
🛡️ [V74.55] Gov Vault & Asset Discovery Routes
职责：承载物理金库资产枚举、稿件生命周期审计路由。
架构：已从 governance.py 物理降解，实现业务逻辑的原子化隔离。
"""

import os
from fastapi import APIRouter, Depends
from core.runtime.cli_bootstrap import get_global_engine
from ..system import verify_token

router = APIRouter()

@router.get("/api/vault/list", dependencies=[Depends(verify_token)])
async def list_vault_manuscripts():
    """🚀 [V52.12] 资产审计接口：获取物理仓库内所有稿件的全量生命周期快照"""
    engine = get_global_engine()
    if not engine: return {"error": "Engine not initialized"}
    
    docs = engine.meta.get_documents_snapshot()
    vault_list = []
    for rel_path, info in docs.items():
        if not info: continue
        status_map = info.get("publish_status") or {}
        live_channels = [ch for ch, s in status_map.items() if s and s.get("status") == "success"]
        seo_data = info.get("seo_data") or {}
        translations = info.get("translations") or {}
        zh_trans = translations.get("zh") or {}
        
        vault_list.append({
            "id": rel_path,
            "path": rel_path,
            "title": info.get("title") or os.path.basename(rel_path),
            "slug": info.get("slug") or "pending",
            "lang": info.get("source_lang") or zh_trans.get("lang") or "zh",
            "word_count": seo_data.get("word_count") or 0,
            "status": "Live" if live_channels else "Draft",
            "channels": list(status_map.keys()),
            "last_updated": max([s.get("timestamp", 0) for s in status_map.values() if s] + [0])
        })
    vault_list.sort(key=lambda x: x["last_updated"], reverse=True)
    return {"manuscripts": vault_list}
