#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes - Foundry Voyage Web Server
职责：托管可视化引导页面，执行算力节点探测与空间初始化 API。
🛡️ [V35.0]：基于 FastAPI 的主权引导服务器。
"""

import os
import uvicorn
import socket
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from core.governance.territory_manager import wm

from core.governance.license_guard import LicenseGuard
from core.utils.tracing import tlog

app = FastAPI(title="Foundry Voyage Wizard")

# 📂 挂载静态资源
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

class InitRequest(BaseModel):
    press_name: str
    manuscripts_path: str

@app.get("/", response_class=HTMLResponse)
async def get_wizard():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if not os.path.exists(index_file):
        return "<h1>Foundry Voyage Wizard - Static Assets Missing</h1>"
    with open(index_file, "r", encoding="utf-8") as f:
        return f.read()

@app.get("/api/probe")
async def probe_nodes():
    """实时探测本机算力节点"""
    nodes = []
    def check_port(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.3)
            return s.connect_ex(('127.0.0.1', port)) == 0

    if check_port(11434): nodes.append({"name": "Ollama", "status": "online", "icon": "brain"})
    if check_port(1234): nodes.append({"name": "LM Studio", "status": "online", "icon": "cpu"})
    
    return {
        "fingerprint": LicenseGuard.get_machine_fingerprint(),
        "nodes": nodes,
        "is_licensed": LicenseGuard.is_licensed()
    }

@app.post("/api/init")
async def init_press(req: InitRequest):
    """执行疆域初始化"""
    tlog.info(f"🏗️ [Web Wizard] 收到初始化请求: {req.press_name}")
    
    # 🚀 [V35.1] 物理路径预处理
    m_path = os.path.expanduser(os.path.expandvars(req.manuscripts_path))
    if not os.path.isabs(m_path):
        m_path = os.path.abspath(m_path)

        
    success = wm.init_sovereign_territory(req.press_name, req.manuscripts_path)
    if success:
        wm.switch(req.press_name)
        return {"status": "success", "message": f"主权疆域 '{req.press_name}' 已成功落成！"}
    else:
        raise HTTPException(status_code=400, detail="疆域创建失败，请检查名称或授权限额。")


def start_wizard_server(port: int = 43210):
    tlog.info(f"📡 [Web Wizard] 正在启动引导服务器: http://127.0.0.1:{port}")
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")
