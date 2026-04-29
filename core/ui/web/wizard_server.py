#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes - Foundry Voyage Web Server
职责：托管可视化引导页面，执行算力节点探测与空间初始化 API。
🛡️ [V48.3]：全流程商业化引导服务器（疆域创建 + 主题 + AI + 语种）。
"""

import os
import yaml
import uvicorn
import socket
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional
from core.governance.territory_manager import wm

from core.governance.license_guard import LicenseGuard
from core.utils.tracing import tlog

app = FastAPI(title="Foundry Voyage Wizard")

# 📂 挂载静态资源
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# ==========================================
# Pydantic Models
# ==========================================

class InitRequest(BaseModel):
    press_name: str
    manuscripts_path: str
    active_theme: str = "starlight"
    ai_provider: str = "openai"
    ai_model: str = "gpt-4o-mini"
    ai_api_key: str = ""
    enable_ai: bool = False
    source_lang: str = "zh"
    target_langs: List[str] = []

# ==========================================
# Routes
# ==========================================

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

    if check_port(11434): nodes.append({"name": "Ollama", "status": "online", "port": 11434, "provider": "ollama"})
    if check_port(1234): nodes.append({"name": "LM Studio", "status": "online", "port": 1234, "provider": "openai-compatible"})
    
    return {
        "fingerprint": LicenseGuard.get_machine_fingerprint(),
        "nodes": nodes,
        "is_licensed": LicenseGuard.is_licensed(),
        "available_themes": [
            {"id": "starlight", "name": "Starlight (Astro)", "desc": "现代文档站，支持多语种侧边栏"},
            {"id": "docusaurus", "name": "Docusaurus (React)", "desc": "Meta 出品，强大的版本控制"},
            {"id": "vitepress", "name": "VitePress (Vue)", "desc": "极速构建，Vue 生态集成"},
            {"id": "nextra", "name": "Nextra (Next.js)", "desc": "Next.js 驱动，MDX 原生支持"},
            {"id": "default", "name": "通用 Markdown", "desc": "纯净 Markdown 输出，自由适配"}
        ],
        "available_providers": [
            {"id": "openai", "name": "OpenAI", "models": ["gpt-4o-mini", "gpt-4o", "gpt-4.1-mini"]},
            {"id": "openai-compatible", "name": "兼容 API (DeepSeek / Moonshot)", "models": ["deepseek-chat", "moonshot-v1-8k"]},
            {"id": "ollama", "name": "Ollama (本地)", "models": ["llama3", "qwen2", "mistral"]},
            {"id": "google", "name": "Google Gemini", "models": ["gemini-2.0-flash", "gemini-2.5-pro"]}
        ],
        "available_langs": [
            {"code": "en", "name": "English"},
            {"code": "ja", "name": "日本語"},
            {"code": "ko", "name": "한국어"},
            {"code": "de", "name": "Deutsch"},
            {"code": "fr", "name": "Français"},
            {"code": "es", "name": "Español"},
            {"code": "pt", "name": "Português"},
            {"code": "ru", "name": "Русский"},
            {"code": "ar", "name": "العربية"}
        ]
    }

@app.post("/api/init")
async def init_press(req: InitRequest):
    """🚀 [V48.3] 全流程疆域初始化：创建 + 配置 + 激活"""
    tlog.info(f"🏗️ [Web Wizard] 收到初始化请求: {req.press_name}")
    
    # 🚀 [V35.1] 物理路径预处理
    m_path = os.path.expanduser(os.path.expandvars(req.manuscripts_path))
    if not os.path.isabs(m_path):
        m_path = os.path.abspath(m_path)

    # 1. 创建物理疆域
    success = wm.init_sovereign_territory(req.press_name, req.manuscripts_path)
    if not success:
        raise HTTPException(status_code=400, detail="疆域创建失败，请检查名称或授权限额。")

    # 2. 🚀 [V48.3] 注入向导收集到的扩展配置
    territory_path = os.path.join(wm.territory_root, req.press_name)
    config_path = os.path.join(territory_path, "configs", "system.yaml")
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                cfg = yaml.safe_load(f) or {}
            
            # 注入主题选择
            cfg["active_theme"] = req.active_theme
            
            # 注入 AI 配置
            cfg.setdefault("translation", {})
            cfg["translation"]["enable_ai"] = req.enable_ai
            if req.enable_ai and req.ai_api_key:
                cfg["translation"]["primary_node"] = "wizard_configured"
                cfg["translation"]["providers"] = {
                    "wizard_configured": {
                        "provider": req.ai_provider,
                        "model": req.ai_model,
                        "api_key": req.ai_api_key
                    }
                }
            
            # 注入语种矩阵
            if req.target_langs:
                lang_names = {
                    "en": "English", "ja": "日本語", "ko": "한국어",
                    "de": "Deutsch", "fr": "Français", "es": "Español",
                    "pt": "Português", "ru": "Русский", "ar": "العربية"
                }
                cfg["i18n_settings"] = {
                    "enabled": True,
                    "source": {"lang_code": req.source_lang, "name": "简体中文" if req.source_lang == "zh" else req.source_lang},
                    "targets": [
                        {"lang_code": lc, "name": lang_names.get(lc, lc), "translate_body": True, "translate_title": True}
                        for lc in req.target_langs
                    ]
                }
            
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.safe_dump(cfg, f, allow_unicode=True)
                
            tlog.info(f"✅ [Web Wizard] 已注入扩展配置: theme={req.active_theme}, ai={req.enable_ai}, langs={req.target_langs}")
        except Exception as e:
            tlog.warning(f"⚠️ [Web Wizard] 扩展配置注入异常 (疆域已创建): {e}")

    # 3. 激活疆域
    wm.switch(req.press_name)
    
    return {
        "status": "success",
        "message": f"主权疆域 '{req.press_name}' 已成功落成！",
        "territory_id": req.press_name,
        "config_summary": {
            "theme": req.active_theme,
            "ai_enabled": req.enable_ai,
            "languages": req.target_langs
        }
    }


def start_wizard_server(port: int = 43210):
    tlog.info(f"📡 [Web Wizard] 正在启动引导服务器: http://127.0.0.1:{port}")
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")
