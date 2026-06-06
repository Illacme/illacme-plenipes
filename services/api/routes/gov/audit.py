# -*- coding: utf-8 -*-
"""
🛡️ [V74.56] Gov Configuration Auditing Routes
职责：提供三层配置层级关系与凭据安全审计 API。
"""
from fastapi import APIRouter, Depends
from typing import Optional
from core.runtime.engine_singleton import get_global_engine
from services.api.routes.system import verify_token

router = APIRouter()

@router.get("/api/config/audit", dependencies=[Depends(verify_token)])
def get_config_audit(imprint_id: Optional[str] = None) -> dict:
    """运行三层配置安全继承拓扑审计"""
    engine = get_global_engine()
    if not engine:
        return {"error": "Engine not initialized"}
    
    from core.config.auditor import audit_config_layers
    try:
        report = audit_config_layers(engine.config_manager, imprint_id=imprint_id)
        return report
    except Exception as e:
        return {"error": f"Audit failed: {str(e)}"}
