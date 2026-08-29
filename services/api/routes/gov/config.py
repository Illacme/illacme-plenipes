# -*- coding: utf-8 -*-
"""
🛡️ [V74.55] Gov Configuration & Execution Routes
职责：承载全量配置审计、更新、主权同步以及出版指令触发路由门面。
架构：已按照 SOP-02 物理降解为 config_shards/*，主文件作为轻量路由门面。
"""

import os
import yaml
from fastapi import APIRouter, Depends
from typing import Optional
from core.runtime.engine_singleton import get_global_engine
from ..system import verify_token
from core.config.config import CONFIG_NAME, CONFIG_LOCAL_NAME, IMPRINT_DIR, CONFIG_DIR, CONFIG_IMPRINT_NAME
from core.utils.tracing import tlog
from .config_shards.config_sync_ops import process_config_sync
from .config_shards.config_persistence_ops import persist_config_to_disk
from .config_shards.config_reload_ops import live_reload_engine_config

router = APIRouter()


@router.get("/api/system/config", dependencies=[Depends(verify_token)])
def get_full_config(level: str = "merged", imprint_id: Optional[str] = None) -> dict:
    """获取全局、局部或刻印合并配置及规则映射。"""
    engine = get_global_engine()
    if not engine:
        return {"error": "Engine not initialized"}
    
    from core.config.governance_map import GOVERNANCE_RULES
    from core.governance.license_guard import LicenseGuard
    
    if level == "merged":
        data = engine.config.model_dump()
        data["_governance_rules"] = GOVERNANCE_RULES
        data["_is_licensed"] = LicenseGuard.is_licensed() or LicenseGuard.is_default_imprint_and_theme_active()
        return data
    
    path = CONFIG_NAME
    if level == "local":
        path = CONFIG_LOCAL_NAME
    elif level == "imprint":
        target_id = imprint_id or engine.im.get_active_imprint()
        path = os.path.join(IMPRINT_DIR, target_id, CONFIG_DIR, CONFIG_IMPRINT_NAME)
    
    data = {}
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
        except Exception:
            data = {"error": f"Failed to parse {path}"}
    else:
        data = {"error": f"File {path} not found"}
        
    return {
        "config": data,
        "governance_rules": GOVERNANCE_RULES
    }


@router.post("/api/config/update", dependencies=[Depends(verify_token)])
async def update_config(req: dict, imprint_id: Optional[str] = None, migrate_cache: bool = False) -> dict:
    """更新内存及磁盘配置，包含底座只读防御、类型自愈、License 校验以及在线热重构。"""
    engine = get_global_engine()
    if not engine:
        return {"error": "Engine not initialized"}
    
    tlog.info(f"📥 [配置更新请求] Payload: {req}, Imprint: {imprint_id}, MigrateCache: {migrate_cache}")

    # Phase 1 & 2 & 3: 前置校验与内存同步
    routing_groups, err_response = process_config_sync(engine, req, imprint_id, migrate_cache)
    if err_response is not None:
        return err_response

    # Phase 4: 物理持久化落盘
    if routing_groups:
        persist_config_to_disk(engine, routing_groups, imprint_id)

    # Phase 5: 在线热重构
    live_reload_engine_config(engine, req, imprint_id)

    return {"status": "success", "active_config": engine.config.model_dump()}
