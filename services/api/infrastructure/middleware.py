# -*- coding: utf-8 -*-
"""
⚙️ Illacme API Infrastructure - Middleware (中间件基础设施)
职责：负责 API 的安全拦截与跨域控制。
🛡️ [V48.3]：全开放 CORS 策略，确保分布式仪表盘的访问主权。
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

def setup_middleware(app: FastAPI) -> None:
    """
    为 FastAPI 应用注入核心中间件。
    
    Args:
        app: 目标 FastAPI 应用实例。
    """
    # 🔓 允许全域跨域（CORS）
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"]
    )
