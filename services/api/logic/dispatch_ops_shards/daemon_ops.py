#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📡 [V68.0] Illacme Plenipes - Dispatch Daemon Shard
职责：本地预览服务器 (DevServer) 的拉起与停止。
架构收敛：全面委托给 ThemeDevServerOrchestrator 统一调度。
"""

import time
from .telemetry_ops import check_port
from core.runtime.infrastructure.theme_orchestrator import theme_orchestrator

def toggle_lab_logic(engine) -> dict:
    """
    🧪 实时预览引擎统一物理调度
    当用户在控制台点击开关时，委托 ThemeDevServerOrchestrator 执行启停，消除双头冲突。
    """
    config = engine.config
    imprint_id = config.active_imprint or "default"
    theme = config.active_theme or "default"
    target_port = theme_orchestrator.resolve_authoritative_port(engine=engine)

    is_running = check_port(target_port)

    if is_running:
        theme_orchestrator.shutdown_all()
        time.sleep(0.3)
        is_active = check_port(target_port)
        message = "实时预览引擎已关闭"
    else:
        result = theme_orchestrator.launch_dev_server(
            theme_id=theme,
            imprint_id=imprint_id,
            requested_port=target_port,
            engine=engine
        )
        time.sleep(0.3)
        actual_port = result.get("port", target_port)
        is_active = check_port(actual_port)
        if result.get("status") == "success" and is_active:
            message = f"实时预览引擎已物理点火启动 (端口: {actual_port})"
        else:
            is_active = False
            message = f"实时预览引擎启动异常: {result.get('message', '端口被占用或超时')}"

    return {
        "success": True,
        "is_active": is_active,
        "message": message
    }
