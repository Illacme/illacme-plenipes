# -*- coding: utf-8 -*-
"""
⚙️ Illacme-plenipes Core - API Control Plane
模块职责：提供 RESTful 接口基座，负责路由分发与安全中枢。
🛡️ [V74.8 Decoupled]：逻辑分片架构，基础设施已委托至 .infrastructure 模块。
"""

import os
from typing import Dict, Any, Optional
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, FileResponse
from contextlib import asynccontextmanager

# 🚀 导入分片后的路由器与基础设施
from .routes import system, content, governance, ws, compute
from .infrastructure.logging import setup_api_logging
from .infrastructure.middleware import setup_middleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    """🚀 [V52.1] 生命周期挂钩：物理链路预热"""
    import asyncio
    ws._main_loop = asyncio.get_running_loop()
    yield

# 1. 实例化主引擎 API 门户
app = FastAPI(title="Illacme-plenipes API Gateway", version="V52.0", lifespan=lifespan)

# 2. 注入核心基础设施逻辑 (代理执行)
setup_middleware(app)

# 3. 挂载路由器
app.include_router(compute.router)
app.include_router(system.router, tags=["System"])
app.include_router(content.router, tags=["Content"])
app.include_router(governance.router, tags=["Governance"])
app.include_router(ws.router, tags=["Realtime"])

@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """🚀 [V52.10] 极速健康自愈接口：用于前端仪表盘的存活探测"""
    from core.runtime.engine_singleton import get_global_engine
    engine = get_global_engine()
    return {
        "status": "ok",
        "engine": "Illacme Plenipes V50.3",
        "active_imprint": engine.imprint_id if engine else None
    }

@app.get("/")
async def root_redirect() -> RedirectResponse:
    """自动重定向至指挥中心"""
    return RedirectResponse(url="/dashboard/")

@app.get("/favicon.ico", include_in_schema=False)
async def favicon() -> FileResponse:
    """提供全景指挥中心 Favicon 皇家图标以消解浏览器 404 吵闹"""
    icon_path = os.path.join(static_dir, "logo.png")
    return FileResponse(icon_path)

# (Lifespan 已经接管了链路预热逻辑)

# 🎨 挂载仪表盘静态页面 (保持原始物理路径探测)
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/dashboard", StaticFiles(directory=static_dir, html=True), name="static")

# 🚀 [V68.0] 资产预览代理：挂载物理出版产物目录 (Dispatch Hub Proxy)
# 🛡️ 物理感应：挂载 imprints 目录以支持多品牌产物预览
imprints_dir = os.path.abspath(os.path.join(os.getcwd(), "imprints"))
if os.path.exists(imprints_dir):
    app.mount("/imprints", StaticFiles(directory=imprints_dir), name="imprints")

dist_dir = os.path.abspath(os.path.join(os.getcwd(), "dist"))
if not os.path.exists(dist_dir):
    os.makedirs(dist_dir, exist_ok=True)
app.mount("/previews", StaticFiles(directory=dist_dir), name="previews")

def start_api_server(host: str = "0.0.0.0", port: int = 43212, blocking: bool = True) -> None:
    """启动物理 API 服务"""
    import uvicorn
    import time
    import threading
    
    # 🚀 [V50.5] 注入分片后的日志过滤引擎
    setup_api_logging()

    # 🚀 [V78.0] 动态提取主权治理系统设置
    from core.runtime.engine_singleton import get_global_engine
    engine = get_global_engine()
    
    uvicorn_log_level = "info"
    uvicorn_access_log = True
    
    if engine and hasattr(engine, 'config') and hasattr(engine.config, 'system'):
        sys_cfg = engine.config.system
        # 兼容小写转换以匹配 uvicorn 规范
        uvicorn_log_level = getattr(sys_cfg, 'log_level', 'INFO').lower()
        uvicorn_access_log = getattr(sys_cfg, 'access_log', True)

    def run_with_retry() -> None:
        """端口接力保障：支持自愈式启动"""
        attempts = 0
        while attempts < 10:
            try:
                uvicorn.run(app, host=host, port=port, log_level=uvicorn_log_level, access_log=uvicorn_access_log)
                return
            except Exception:
                attempts += 1
                time.sleep(1)
        
    if blocking:
        run_with_retry()
    else:
        thread = threading.Thread(target=run_with_retry, daemon=True)
        thread.start()
