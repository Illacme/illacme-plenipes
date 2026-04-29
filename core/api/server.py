#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - API Control Plane
模块职责：提供 RESTful 接口基座，负责路由分发与安全中枢。
🛡️ [V24.6 Refactored]：解耦后的轻量化 API 网关。
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# 🚀 [V24.6] 导入解耦后的路由器
from .routes import system, content, governance

app = FastAPI(title="Illacme-plenipes API Gateway", version="V24.6")

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

def start_api_server(host="0.0.0.0", port=43211, blocking=True):
    """启动物理服务"""
    import uvicorn
    if blocking:
        uvicorn.run(app, host=host, port=port)
    else:
        import threading
        thread = threading.Thread(target=uvicorn.run, args=(app,), kwargs={"host": host, "port": port}, daemon=True)
        thread.start()
