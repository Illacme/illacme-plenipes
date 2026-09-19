# -*- coding: utf-8 -*-
"""
🎨 [V74.8] System Theme & Wizard Lifecycle Operations Shard
职责：提供主题依赖自动化安装、升级、物理快照回滚、模板槽位探测与品牌向导服务启停。
"""

import os
import threading
import urllib.request
from typing import Dict, Any
from fastapi import HTTPException

from core.utils.event_bus import bus
from core.logic.diagnostics.component_monitor import ComponentMonitor
from services.api.logic import sys_ops


def _get_engine():
    """获取全局引擎实例，优先兼容外部对主模块的动态 patch / mock"""
    try:
        import services.api.routes.system as parent_mod
        if hasattr(parent_mod, "get_global_engine"):
            return parent_mod.get_global_engine()
    except Exception:
        pass
    from core.runtime.engine_singleton import get_global_engine
    return get_global_engine()


async def install_theme_dependencies_logic() -> Dict[str, str]:
    """🚀 [V52.11] 自动化依赖安装接口"""
    engine = _get_engine()
    if not engine:
        raise HTTPException(status_code=400, detail="Engine missing")
    
    from core.config.config import THEMES_DIR
    theme_dir = os.path.join(engine.paths.get(THEMES_DIR, THEMES_DIR), engine.active_theme)
    if not os.path.exists(os.path.join(theme_dir, "package.json")):
        return {"status": "skipped", "message": "No package.json"}
    
    threading.Thread(target=sys_ops.run_theme_install, args=(engine, theme_dir), daemon=True).start()
    return {"status": "started"}


async def upgrade_theme_dependencies_logic() -> Dict[str, str]:
    """🚀 [V65.0] 自动化版本升级接口"""
    engine = _get_engine()
    if not engine:
        raise HTTPException(status_code=400, detail="Engine missing")
    from core.config.config import THEMES_DIR
    theme_dir = os.path.join(engine.paths.get(THEMES_DIR, THEMES_DIR), engine.active_theme)
    threading.Thread(target=sys_ops.run_theme_upgrade, args=(engine, theme_dir), daemon=True).start()
    return {"status": "started"}


async def rollback_theme_config_logic() -> Dict[str, Any]:
    """🚀 [V65.3] 物理快照回滚接口"""
    engine = _get_engine()
    if not engine:
        raise HTTPException(status_code=400, detail="Engine missing")
    from core.config.config import THEMES_DIR
    theme_dir = os.path.join(engine.paths.get(THEMES_DIR, THEMES_DIR), engine.active_theme)
    restored = sys_ops.rollback_config(engine, theme_dir)
    if restored:
        bus.emit("UI_TERMINAL_DATA", type="LOG", data=f"⏪ [环境复原] 已恢复: {', '.join(restored)}")
        if "package.json" in restored:
            await install_theme_dependencies_logic()
        return {"status": "success", "restored": restored}
    return {"status": "skipped"}


def get_theme_slots_logic() -> Dict[str, Any]:
    """🚀 [V75.0] 动态探测当前主题/SSG 引擎支持的页面模板槽位"""
    engine = _get_engine()
    if not engine or not hasattr(engine, "ssg_adapter") or not engine.ssg_adapter:
        return {"slots": {}}
    
    try:
        return {"slots": engine.ssg_adapter.get_feature_slots()}
    except Exception:
        return {"slots": {}}


async def start_wizard_logic() -> Dict[str, str]:
    """🚀 [V55.0] 启动品牌向导服务"""
    if ComponentMonitor.check_port(43211):
        return {"status": "already_running"}
    from services.wizard.wizard_server import start_wizard_server
    threading.Thread(target=start_wizard_server, kwargs={"port": 43211}, daemon=True).start()
    return {"status": "started"}


async def stop_wizard_logic() -> Dict[str, str]:
    """🛑 [V55.0] 停止品牌向导服务"""
    try:
        req = urllib.request.Request("http://127.0.0.1:43211/api/shutdown", method="POST")
        with urllib.request.urlopen(req, timeout=2.0):
            pass
        return {"status": "stopped"}
    except Exception:
        return {"status": "stopped", "note": "Service may already be down"}
