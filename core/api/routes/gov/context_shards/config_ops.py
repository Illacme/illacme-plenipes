# -*- coding: utf-8 -*-
"""
🛡️ [V74.55] Gov Config Ops
职责：承载系统多源配置读取（merged / local / imprint）及授权审计的底层原子实现。
"""

import os
from typing import Optional
from core.runtime.engine_singleton import get_global_engine
from core.config.config import CONFIG_NAME, CONFIG_LOCAL_NAME, IMPRINT_DIR, CONFIG_DIR, CONFIG_IMPRINT_NAME

def get_full_config_impl(level: str = "merged", imprint_id: Optional[str] = None):
    """
    承载多模式配置加载（merged、local 与 imprint 配置策略读取以及 LicenseGuard 授权检查）的原子逻辑。
    """
    engine = get_global_engine()
    if not engine: return {"error": "Engine not initialized"}

    from core.config.governance_map import GOVERNANCE_RULES
    from core.governance.license_guard import LicenseGuard

    if level == "merged":
        data = engine.config.model_dump()
        data["_governance_rules"] = GOVERNANCE_RULES
        data["_is_licensed"] = LicenseGuard.is_licensed()
        return data

    import yaml
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
        except:
            data = {"error": f"Failed to parse {path}"}
    else:
        data = {"error": f"File {path} not found"}

    return {
        "config": data,
        "governance_rules": GOVERNANCE_RULES
    }
