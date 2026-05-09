import os
import sys
import yaml
import uvicorn
import socket
import threading
import shutil
import signal
import time
import subprocess
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional
from core.governance.imprint_manager import im
from core.governance.license_guard import LicenseGuard
import core.adapters.ai
from core.adapters.ai.registry import AIProviderRegistry
from core.utils.tracing import tlog
from core.logic.diagnostics import DiagnosticsService

app = FastAPI(title="Illacme Plenipes Wizard")
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

class InitRequest(BaseModel):
    imprint_id: str
    imprint_name: str
    manuscripts_path: str
    active_theme: str = "default"
    enable_ai: bool = False
    ai_provider: str = "openai"
    ai_model: str = "gpt-4o-mini"
    ai_api_key: str = ""
    ai_base_url: str = ""
    source_lang: str = "zh"
    target_langs: List[str] = []

class FsRequest(BaseModel):
    path: str = "."

class AiValidateRequest(BaseModel):
    provider: str
    model: Optional[str] = "default"
    api_key: str
    base_url: Optional[str] = None

from core.utils.language_hub import LanguageHub

@app.get("/", response_class=HTMLResponse)
async def get_wizard():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if not os.path.exists(index_file):
        return "<h1>Assets Missing</h1>"
    with open(index_file, "r", encoding="utf-8") as f:
        return f.read()

@app.get("/api/probe")
async def probe_nodes():
    nodes = DiagnosticsService.probe_local_compute()
    rec_p = nodes[0]["provider"] if nodes else "openai"
    rec_m = "llama3.1" if rec_p == "ollama" else ("gpt-4o-mini" if rec_p == "openai" else "default")
    
    vault_suggestions = DiagnosticsService.get_vault_suggestions()
    
    from core.config.config import CONFIG_IMPRINT_NAME, CONFIG_LOCAL_NAME
    cfg_p = os.path.join(os.getcwd(), CONFIG_IMPRINT_NAME)
    current_config = None
    if os.path.exists(cfg_p):
        try:
            with open(cfg_p, 'r', encoding='utf-8') as f:
                current_config = yaml.safe_load(f)
        except:
            pass

    import random
    existing = im.list_imprints()
    existing_ids = {t["id"].lower() for t in existing}
    
    def gen_id():
        w1 = ["Aether", "Borealis", "Stellar", "Sovereign", "Boundless", "Ethereal", "Vivid", "Noble", "Infinite", "Radiant", "Arcane", "Astral", "Celestial", "Primal", "Zenith", "Apex", "Titan", "Obsidian", "Ivory", "Shadow", "Luminous", "Ancient", "Modern"]
        w2 = ["Voyage", "Legacy", "Horizon", "Nexus", "Echo", "Spirit", "Realm", "Vision", "Foundry", "Vault", "Harbor", "Citadel", "Domain", "Sanctum", "Archive", "Atlas", "Vortex", "Crest", "Drift", "Pulse", "Rift", "Tide", "Warp", "Zephyr"]
        return f"{random.choice(w1).lower()}_{random.choice(w2).lower()}"
    
    random_id = gen_id()
    attempts = 0
    while random_id in existing_ids and attempts < 10:
        random_id = gen_id()
        attempts += 1

    return {
        "current_config": current_config,
        "fingerprint": LicenseGuard.get_machine_fingerprint(),
        "nodes": nodes,
        "is_licensed": LicenseGuard.is_licensed(),
        "recommended": {
            "imprint_name": random_id,
            "provider": rec_p,
            "model": rec_m,
            "vault": vault_suggestions[0]["path"] if vault_suggestions else "./manuscripts"
        },
        "vault_suggestions": vault_suggestions,
        "available_themes": [
            {"id": "default", "name": "Sovereign (Default)", "desc": "极致简约的主权底座，回归创作本质", "official": True},
            {"id": "universal", "name": "Universal (General Markdown)", "desc": "通用 Markdown 排版，完美兼容各类写作场景", "official": True},
            {"id": "starlight", "name": "Starlight (Modern Docs)", "desc": "工业级审美，专为现代化文档中心打造", "official": True},
            {"id": "vitepress", "name": "VitePress (Lightning Fast)", "desc": "极速响应，基于 Vite 的现代技术文档风格", "official": True},
            {"id": "docusaurus", "name": "Docusaurus (Project Hub)", "desc": "经典的文档站点架构，适合大规模项目管理", "official": True},
            {"id": "nextra", "name": "Nextra (Next.js Powered)", "desc": "灵动轻盈，基于 Next.js 的高级内容排版", "official": True}
        ],
        "available_providers": [
            {
                "id": p,
                "name": {
                    "openai": "OpenAI", "ollama": "Ollama (Local)", "lmstudio": "LM Studio (Local)",
                    "google": "Google Gemini", "anthropic": "Anthropic Claude", "deepseek": "DeepSeek",
                    "siliconflow": "SiliconFlow", "mistral": "Mistral AI", "groq": "Groq",
                    "together": "Together AI", "openrouter": "OpenRouter", "azure": "Azure OpenAI",
                    "cohere": "Cohere", "mock": "模拟算力 (Mock)"
                }.get(p, p.capitalize()),
                "default_url": getattr(AIProviderRegistry.get_provider(p), "DEFAULT_URL", "")
            }
            for p in AIProviderRegistry.get_all_protocols()
        ],
        "available_langs": LanguageHub.get_supported_matrix()
    }

@app.post("/api/fs/ls")
async def list_files(req: FsRequest):
    path = os.path.expanduser(req.path)
    if not os.path.exists(path):
        return {"current": path, "items": [], "error": "路径不存在"}
    try:
        items = []
        if os.path.dirname(path) != path:
            items.append({"name": "..", "path": os.path.dirname(path), "type": "dir"})
        for entry in os.scandir(path):
            if entry.is_dir() and not entry.name.startswith("."):
                items.append({"name": entry.name, "path": entry.path, "type": "dir"})
        return {"current": os.path.abspath(path), "items": sorted(items, key=lambda x: (x or {}).get("name", ""))}
    except Exception as e:
        return {"current": path, "items": [], "error": str(e)}

@app.post("/api/ai/models")
async def get_ai_models(req: AiValidateRequest):
    p_cls = AIProviderRegistry.get_provider(req.provider)
    if not p_cls: return {"models": []}
    try:
        url = req.base_url or getattr(p_cls, "DEFAULT_URL", "")
        n_cfg = type('N', (), {'base_url': url, 'api_key': req.api_key, 'type': req.provider,
                               'limits': type('L', (), {'max_concurrency': 1, 'timeout': 10})()})()
        cfg = type('D', (), {'base_url': url, 'api_key': req.api_key, 'model': req.model, 'api_timeout': 10,
                             'providers': {'w': n_cfg}})()
        t = p_cls("w", cfg)
        return {"models": await t.list_models()}
    except Exception as e:
        err_str = str(e)
        return {"models": [], "error": f"原始提示: {err_str}"}

@app.post("/api/ai/validate")
async def validate_ai(req: AiValidateRequest):
    return await DiagnosticsService.validate_ai_connectivity(req.provider, req.model, req.api_key, req.base_url)

@app.post("/api/init")
async def init_press(req: InitRequest):
    m_path = os.path.abspath(os.path.expanduser(req.manuscripts_path))
    
    if not LicenseGuard.is_pro_feature_allowed("multi_imprint"):
        if len(im.list_imprints()) >= 1:
            raise HTTPException(status_code=403, detail="社区版仅限划定 1 个版图。请升级至授权版。")

    if not im.init_sovereign_imprint(req.imprint_id, m_path, imprint_name=req.imprint_name):
        raise HTTPException(status_code=400, detail="创建失败：物理版图初始化异常。")
    
    from core.config.config import CONFIG_IMPRINT_NAME, IMPRINT_DIR, CONFIG_DIR, CONFIG_LOCAL_NAME
    
    # 1. 注入品牌层配置
    cfg_p = os.path.join(IMPRINT_DIR, req.imprint_id, CONFIG_DIR, CONFIG_IMPRINT_NAME)
    if os.path.exists(cfg_p):
        try:
            with open(cfg_p, 'r', encoding='utf-8') as f:
                cfg = yaml.safe_load(f) or {}
            cfg["active_theme"] = req.active_theme
            cfg["imprint_name"] = req.imprint_name
            if req.target_langs:
                ln = {"en":"English","ja":"日本語","ko":"한국어","de":"Deutsch","fr":"Français","es":"Español"}
                cfg["i18n_settings"] = {"enabled":True, "source":{"lang_code":req.source_lang, "name":"中文"},
                    "targets":[{"lang_code":lc, "name":ln.get(lc,lc), "translate_body":True} for lc in req.target_langs]}
            with open(cfg_p, 'w', encoding='utf-8') as f:
                yaml.safe_dump(cfg, f, allow_unicode=True)
        except Exception as e:
            tlog.warning(f"Config Injection Failed: {e}")
            
    # 2. 🚀 [V65.1] 强制物理锁定：直接操作 config.local.yaml 字典
    try:
        local_path = os.path.join(os.getcwd(), CONFIG_LOCAL_NAME)
        local_data = {}
        if os.path.exists(local_path):
            try:
                with open(local_path, 'r', encoding='utf-8') as f:
                    local_data = yaml.safe_load(f) or {}
            except: pass
            
        local_data["active_imprint"] = req.imprint_id
        if "system" not in local_data: local_data["system"] = {}
        local_data["system"]["data_root"] = f"imprints/{req.imprint_id}"
        
        if req.enable_ai:
            if "translation" not in local_data: local_data["translation"] = {}
            local_data["translation"]["primary_node"] = "wizard"
            if "providers" not in local_data["translation"]: local_data["translation"]["providers"] = {}
            local_data["translation"]["providers"]["wizard"] = {
                "type": req.ai_provider, "model": req.ai_model, "api_key": req.ai_api_key, "base_url": req.ai_base_url
            }

        with open(local_path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(local_data, f, allow_unicode=True)
        tlog.success(f"🛡️ [主权锁定] 品牌 '{req.imprint_id}' 指纹已强制写入 {local_path}。")
    except Exception as e:
        tlog.warning(f"Sovereignty Lock Failed: {e}")

    im.switch(req.imprint_id)

    # 3. 部署主题
    from core.config.config import THEMES_DIR
    try:
        imprint_themes_dir = os.path.join(im.imprint_root, req.imprint_id, THEMES_DIR)
        os.makedirs(imprint_themes_dir, exist_ok=True)
        source_theme_path = os.path.abspath(os.path.join(THEMES_DIR, req.active_theme))
        target_theme_path = os.path.join(imprint_themes_dir, req.active_theme)
        
        if os.path.exists(source_theme_path):
            if os.path.exists(target_theme_path):
                shutil.rmtree(target_theme_path)
            shutil.copytree(source_theme_path, target_theme_path)
            tlog.info(f"🎨 [主题对正] 已将主题 '{req.active_theme}' 部署至品牌疆域。")
    except Exception as e:
        tlog.warning(f"Theme Deployment Failed: {e}")

    # 4. 平滑移交
    try:
        def graceful_handoff():
            time.sleep(0.5)
            if 'server_instance' in globals() and server_instance:
                server_instance.should_exit = True
        threading.Thread(target=graceful_handoff, daemon=True).start()
    except: pass

    return {"status": "success", "imprint_id": req.imprint_id}

@app.post("/api/shutdown")
async def shutdown_wizard(request: Request):
    if 'server_instance' in globals() and server_instance:
        server_instance.should_exit = True
    return {"message": "done"}

server_instance = None

def start_wizard_server(port: int = 43211):
    global server_instance
    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning")
    server_instance = uvicorn.Server(config)
    server_instance.run()

if __name__ == "__main__":
    start_wizard_server()
