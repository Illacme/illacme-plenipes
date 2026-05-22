#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📡 [V68.0] Illacme Plenipes - Dispatch Daemon Shard
职责：本地静态预览服务器 (DevServer) 的拉起与停止。
"""

import os
import time
from .telemetry_ops import check_port

def toggle_lab_logic(engine) -> dict:
    """
    🧪 实时预览引擎物理调度 (Physical Daemon Scheduling)
    当用户点击启动时，在后台线程中拉起零依赖的静态资源预览服务器，并在关闭时物理杀灭。
    """
    config = engine.config
    imprint_id = config.active_imprint or "default"
    theme = config.active_theme or "default"
    
    preview_dir = engine.paths.get('static_dir') or engine.paths.get('target_base')
    if not preview_dir:
        preview_dir = os.path.join("imprints", imprint_id, "themes", theme, "dist")
    
    preview_dir = os.path.abspath(preview_dir)
    port = 43213

    from core.utils.dev_server import DevServer
    
    if not hasattr(engine, 'preview_server') or engine.preview_server is None:
        engine.preview_server = DevServer(directory=preview_dir, port=port)

    is_running = check_port(port)

    if is_running:
        engine.preview_server.stop()
        time.sleep(0.2)
        is_active = check_port(port)
        message = "实时预览引擎已关闭"
    else:
        os.makedirs(preview_dir, exist_ok=True)
        success = engine.preview_server.start(blocking=False)
        time.sleep(0.3)
        is_active = check_port(port)
        if success and is_active:
            message = "实时预览引擎已物理点火启动"
        else:
            is_active = False
            message = "实时预览引擎启动失败，可能 43213 端口被占用"

    return {
        "success": True,
        "is_active": is_active,
        "message": message
    }
