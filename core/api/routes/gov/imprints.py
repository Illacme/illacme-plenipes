# -*- coding: utf-8 -*-
"""
🛡️ [V74.55] Gov Imprint Management Routes
职责：承载出版版图 (Imprint) 的枚举、切换、创建与删除等核心治理逻辑。
架构：已从 governance.py 物理降解，实现业务逻辑的原子化隔离。
"""

import os
from fastapi import APIRouter, Depends
from core.runtime.engine_singleton import get_global_engine
from ..system import verify_token
from core.config.config import CONFIG_DIR, CONFIG_IMPRINT_NAME

router = APIRouter()

@router.get("/api/imprints", dependencies=[Depends(verify_token)])
def list_imprints():
    from core.governance.imprint_manager import im
    return {"imprints": im.list_imprints(), "active": im.get_active_imprint()}

@router.get("/api/imprints/stats", dependencies=[Depends(verify_token)])
def get_imprints_stats():
    """🚀 [V52.22] 跨品牌资产大盘与环境健康统计"""
    engine = get_global_engine()
    if not engine: return {"error": "Engine not initialized"}
    
    from core.governance.imprint_manager import im
    from core.governance.env_sentry import sentry
    imprints = im.list_imprints()
    
    stats = {}
    for imp in imprints:
        imp_id = imp["id"]
        from core.config.config import IMPRINT_DIR
        actual_imp_path = os.path.join(os.getcwd(), IMPRINT_DIR, imp_id) if imp_id != "default" else os.getcwd()
        
        active_theme = "default"
        config_path = os.path.join(actual_imp_path, CONFIG_DIR, CONFIG_IMPRINT_NAME)
        if os.path.exists(config_path):
            try:
                import yaml
                with open(config_path, 'r', encoding='utf-8') as f:
                    c = yaml.safe_load(f) or {}
                    active_theme = c.get("active_theme", "default")
            except: pass

        from core.config.config import METADATA_DIR
        meta_db = os.path.join(actual_imp_path, METADATA_DIR, "themes", active_theme, "ledger.db")
        doc_count = 0
        if os.path.exists(meta_db):
            import sqlite3
            try:
                conn = sqlite3.connect(meta_db)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM documents")
                doc_count = cursor.fetchone()[0]
                conn.close()
            except: pass
            
        health = sentry.check_isolation_health(actual_imp_path, theme=active_theme)
        
        stats[imp_id] = {
            "doc_count": doc_count,
            "isolation": health["isolation_level"],
            "healthy": health["has_local_toolchain"]
        }
    return stats

@router.post("/api/imprints/add", dependencies=[Depends(verify_token)])
async def add_imprint(req: dict):
    from core.governance.imprint_manager import im
    name = req.get("name")
    path = req.get("path")
    press_name = req.get("press_name")
    bootstrap_vault = req.get("bootstrap_vault", False)
    if not name or not path: return {"error": "Missing name or path"}
    
    success = im.init_sovereign_imprint(name, path, press_name, bootstrap_vault)
    return {"success": success}

@router.post("/api/imprints/switch", dependencies=[Depends(verify_token)])
async def switch_imprint(req: dict):
    from core.governance.imprint_manager import im
    from core.runtime.cli_bootstrap import deep_reload_imprint
    
    imprint_id = req.get("imprint_id")
    if not imprint_id: return {"error": "Missing imprint_id"}
    
    success = deep_reload_imprint(imprint_id)
    if success:
        im.switch(imprint_id)
        return {"success": True, "active": imprint_id}
    else:
        return {"success": False, "error": "引擎深度重载失败，请检查终端日志。"}

@router.post("/api/imprints/delete", dependencies=[Depends(verify_token)])
async def delete_imprint(req: dict):
    from core.governance.imprint_manager import im
    name = req.get("name")
    if not name: return {"error": "Missing name"}
    
    success = im.delete_imprint(name)
    return {"success": success}
