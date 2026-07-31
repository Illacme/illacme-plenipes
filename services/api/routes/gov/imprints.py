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
        vault_exists = True
        vault_path = ""
        if os.path.exists(config_path):
            try:
                import yaml
                with open(config_path, 'r', encoding='utf-8') as f:
                    c = yaml.safe_load(f) or {}
                    active_theme = c.get("active_theme", "default")
                    vault_path = c.get("vault_root", "")
                    if vault_path:
                        abs_v = os.path.abspath(os.path.expanduser(vault_path))
                        vault_exists = os.path.exists(abs_v)
            except: pass

        from core.config.config import METADATA_DIR
        meta_db = os.path.join(actual_imp_path, METADATA_DIR, "themes", active_theme, "ledger.db")
        doc_count = 0
        if os.path.exists(meta_db):
            import sqlite3
            try:
                conn = sqlite3.connect(meta_db, timeout=5.0)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM documents")
                doc_count = cursor.fetchone()[0]
                conn.close()
            except: pass
            
        health = sentry.check_isolation_health(actual_imp_path, theme=active_theme)
        
        # 🛡️ 物理真理对正：只有当工具链健全且原稿文库路径在物理磁盘真实存在时，健康状态才为 True
        is_healthy = bool(health.get("has_local_toolchain", True) and vault_exists)

        stats[imp_id] = {
            "doc_count": doc_count,
            "isolation": health.get("isolation_level", "NORMAL"),
            "healthy": is_healthy,
            "vault_exists": vault_exists,
            "vault_path": vault_path
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
    if success:
        engine = get_global_engine()
        if engine and hasattr(engine, "ledger") and engine.ledger:
            engine.ledger.log(
                event_type="PUBLISH_LAYOUT_CHANGED",
                details=f"创建了新的出版版图 (Imprint): {name}，物理路径为 {path}",
                severity="INFO",
                actor="APIAdmin",
                metadata={"name": name, "path": path, "press_name": press_name}
            )
    return {"success": success}

@router.post("/api/imprints/switch", dependencies=[Depends(verify_token)])
async def switch_imprint(req: dict):
    from core.governance.imprint_manager import im
    from core.runtime.cli_bootstrap import deep_reload_imprint
    
    # 🛡️ [Sync Lock] 检查当前是否在进行全域同步
    engine = get_global_engine()
    if engine and getattr(engine, "is_syncing", False):
        return {"success": False, "error": "🛑 品牌当前正处于【全域同步】状态，为了防止数据账本损坏和输出路径污染，已拦截切换品牌操作。请等待当前同步任务完成后再试。"}

    imprint_id = req.get("imprint_id")
    if not imprint_id: return {"error": "Missing imprint_id"}
    
    try:
        success = deep_reload_imprint(imprint_id)
    except (ValueError, SystemExit) as e:
        msg = str(e)
        if not msg or msg == "1":
            msg = f"版图 [{imprint_id}] 预检或路径校验未通过"
        return {"success": False, "error": f"版图预检未通过: {msg}"}
    except Exception as e:
        return {"success": False, "error": f"引擎深度重载异常: {e}"}

    if success:
        im.switch(imprint_id)
        if engine and hasattr(engine, "ledger") and engine.ledger:
            engine.ledger.log(
                event_type="PUBLISH_LAYOUT_CHANGED",
                details=f"切换当前出版版图至: {imprint_id}",
                severity="INFO",
                actor="APIAdmin",
                metadata={"imprint_id": imprint_id}
            )
        return {"success": True, "active": imprint_id}
    else:
        return {"success": False, "error": "引擎深度重载失败，请检查终端日志。"}

@router.post("/api/imprints/delete", dependencies=[Depends(verify_token)])
async def delete_imprint(req: dict):
    from core.governance.imprint_manager import im
    name = req.get("name")
    if not name: return {"error": "Missing name"}
    
    success = im.delete_imprint(name)
    if success:
        engine = get_global_engine()
        if engine and hasattr(engine, "ledger") and engine.ledger:
            engine.ledger.log(
                event_type="PUBLISH_LAYOUT_CHANGED",
                details=f"删除了出版版图 (Imprint): {name}",
                severity="WARNING",
                actor="APIAdmin",
                metadata={"name": name}
            )
    return {"success": success}
