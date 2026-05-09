#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - API Control Plane
模块职责：提供 RESTful 接口基座，负责路由分发与安全中枢。
🛡️ [V48.3 Refactored]：解耦后的轻量化 API 网关。
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# 🚀 [V48.3] 导入解耦后的路由器
from .routes import system, content, governance, ws, compute

from fastapi.responses import RedirectResponse

app = FastAPI(title="Illacme-plenipes API Gateway", version="V52.0")

app.include_router(compute.router)

@app.get("/health")
async def health_check():
    """🚀 [V52.10] 极速健康自愈接口：用于前端仪表盘的存活探测"""
    from core.runtime.cli_bootstrap import get_global_engine
    engine = get_global_engine()
    return {
        "status": "ok",
        "engine": "Illacme Plenipes V50.3",
        "active_imprint": engine.imprint_id if engine else None
    }

@app.get("/")
async def root_redirect():
    return RedirectResponse(url="/dashboard/")

# 🚀 [V52.1] 生命周期挂钩：物理链路预热
@app.on_event("startup")
async def startup_event():
    import asyncio
    from .routes import ws
    ws._main_loop = asyncio.get_running_loop()

# 🔓 允许跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# 🎨 挂载仪表盘静态页面
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/dashboard", StaticFiles(directory=static_dir, html=True), name="static")

# 🛰️ 注册模块化路由
app.include_router(system.router, tags=["System"])
app.include_router(content.router, tags=["Content"])
app.include_router(governance.router, tags=["Governance"])
app.include_router(ws.router, tags=["Realtime"])

def start_api_server(host="0.0.0.0", port=43212, blocking=True):
    """启动物理服务"""
    import uvicorn
    import time
    import logging
    
    # 🚀 [V50.5] 静默心跳：过滤掉高频的同步请求日志，保持终端整洁
    class HeartbeatFilter(logging.Filter):
        def filter(self, record):
            # 屏蔽 dashboard 的高频数据轮询日志
            msg = record.getMessage()
            return "/api/billing/stats" not in msg and "/api/galaxy/graph" not in msg

    # 注入过滤器到 uvicorn 的访问日志中
    logging.getLogger("uvicorn.access").addFilter(HeartbeatFilter())

    # 🚀 [V50.5] 端口接力保障：如果端口被占用（如向导尚未退出），则循环等待
    def run_with_retry():
        attempts = 0
        while attempts < 10:
            try:
                # 调低 log_level 进一步减少干扰
                uvicorn.run(app, host=host, port=port, log_level="info", access_log=True)
                return
            except Exception as e:
                attempts += 1
                time.sleep(1)
        
    if blocking:
        run_with_retry()
    else:
        import threading
        thread = threading.Thread(target=run_with_retry, daemon=True)
        thread.start()
