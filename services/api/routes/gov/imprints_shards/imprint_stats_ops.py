# -*- coding: utf-8 -*-
"""
🛡️ [V74.55] Gov Imprints Shard: Stats & Vault Check Operations
职责：承载出版品牌文库绑定探测与跨品牌资产大盘及健康统计。
"""

import os
import sqlite3
import yaml


def _get_engine():
    """获取全局引擎实例，优先兼容外部对主模块的动态 patch / mock"""
    try:
        import services.api.routes.gov.imprints as parent_mod
        if hasattr(parent_mod, "get_global_engine"):
            return parent_mod.get_global_engine()
    except Exception:
        pass
    from core.runtime.engine_singleton import get_global_engine
    return get_global_engine()


def check_vault_binding_logic(path: str = "") -> dict:
    """
    🔍 检查所选原稿文库路径是否已被其他出版品牌绑定。
    仅用于页面感知与友情提示，不拦截或阻断用户继续创建新品牌。
    """
    from core.governance.imprint_manager import im
    if not path or not path.strip():
        return {"bound": False, "imprints": []}

    clean_path = path.strip()
    try:
        target_norm = os.path.normcase(os.path.normpath(os.path.abspath(os.path.expanduser(clean_path))))
    except Exception:
        target_norm = clean_path

    bound_imprints = []
    for imp in im.list_imprints():
        v_raw = imp.get("vault_root", "")
        v_abs = imp.get("vault_abs", "")
        
        match = False
        if v_abs:
            try:
                if os.path.normcase(os.path.normpath(v_abs)) == target_norm:
                    match = True
            except Exception:
                pass
        if not match and v_raw and v_raw != "Unknown Vault":
            try:
                if os.path.normcase(os.path.normpath(os.path.abspath(os.path.expanduser(v_raw)))) == target_norm:
                    match = True
            except Exception:
                pass

        if match:
            bound_imprints.append({
                "id": imp["id"],
                "name": imp["name"],
                "vault_root": v_raw
            })

    return {
        "bound": len(bound_imprints) > 0,
        "imprints": bound_imprints,
        "path": clean_path
    }


def get_imprints_stats_logic() -> dict:
    """🚀 [V52.22] 跨品牌资产大盘与环境健康统计"""
    engine = _get_engine()
    if not engine:
        return {"error": "Engine not initialized"}
    
    from core.governance.imprint_manager import im
    from core.governance.env_sentry import sentry
    from core.config.config import CONFIG_DIR, CONFIG_IMPRINT_NAME, IMPRINT_DIR, METADATA_DIR
    imprints = im.list_imprints()
    
    stats = {}
    for imp in imprints:
        imp_id = imp["id"]
        actual_imp_path = os.path.join(os.getcwd(), IMPRINT_DIR, imp_id) if imp_id != "default" else os.getcwd()
        
        active_theme = "default"
        if imp_id == "default":
            active_theme = getattr(engine.config, "active_theme", "default") or "default"
        else:
            config_path = os.path.join(actual_imp_path, CONFIG_DIR, CONFIG_IMPRINT_NAME)
            if os.path.exists(config_path):
                try:
                    with open(config_path, "r", encoding="utf-8") as f:
                        c = yaml.safe_load(f) or {}
                        active_theme = c.get("active_theme", "default")
                except Exception:
                    pass

        vault_path = imp.get("vault_root") or ""
        abs_v = imp.get("vault_abs") or (os.path.abspath(os.path.expanduser(vault_path)) if vault_path else "")
        vault_exists = os.path.exists(abs_v) if abs_v else False

        # 📂 统计文库真实文稿数量：优先从主权账本对正，缺失或为 0 时直接遍历物理原稿文库自愈保底
        doc_count = 0
        ledger_candidates = [
            os.path.join(abs_v, ".plenipes", "cache", "ledger.db") if abs_v else "",
            os.path.join(actual_imp_path, METADATA_DIR, "runtime", "cache", "ledger.db"),
            os.path.join(actual_imp_path, METADATA_DIR, "themes", active_theme, "ledger.db")
        ]
        for meta_db in ledger_candidates:
            if meta_db and os.path.exists(meta_db):
                try:
                    conn = sqlite3.connect(meta_db, timeout=2.0)
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM documents")
                    row = cursor.fetchone()
                    if row and row[0] > 0:
                        doc_count = row[0]
                    conn.close()
                    if doc_count > 0:
                        break
                except Exception:
                    pass

        # 🛡️ 物理真理保底：如果账本未生成或记录为 0，且本地原稿文库真实存在，直接遍历统计 Markdown 文件总数
        if doc_count == 0 and vault_exists and os.path.isdir(abs_v):
            try:
                ignored_dirs = {".git", ".obsidian", ".trash", ".plenipes", "node_modules", ".venv", "themes", "dist", "public", "build", "assets", "static", ".github"}
                for root, dirs, files in os.walk(abs_v):
                    dirs[:] = [d for d in dirs if not d.startswith(".") and d.lower() not in ignored_dirs]
                    for f in files:
                        if f.endswith((".md", ".markdown")) and not f.startswith("."):
                            doc_count += 1
            except Exception:
                pass
            
        health = sentry.check_isolation_health(actual_imp_path, theme=active_theme)
        
        # 🛡️ 物理真理对正：只有当工具链健全且原稿文库路径在物理磁盘真实存在时，健康状态才为 True
        is_healthy = bool(health.get("has_local_toolchain", True) and vault_exists)

        stats[imp_id] = {
            "doc_count": doc_count,
            "isolation": health.get("isolation_level", "NORMAL"),
            "healthy": is_healthy,
            "vault_exists": vault_exists,
            "vault_root": vault_path
        }
    return stats
