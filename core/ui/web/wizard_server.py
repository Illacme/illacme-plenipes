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
    # 🚀 [V50.0] 动态排重：确保建议的出版品牌 ID 不与现有疆域冲突
    existing = im.list_imprints()
    existing_ids = {t["id"].lower() for t in existing}
    
    def gen_id():
        # 🚀 [V50.4.7] 工业级宏大品牌词库：双词对撞逻辑
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
        if "timeout" in err_str.lower():
            guide = "【解决建议：连接超时。请检查您的网络是否可以访问该 AI 官方服务，或尝试配置科学上网代理】"
        elif "refused" in err_str.lower():
            guide = "【解决建议：连接被拒绝。如果是本地服务，请确认 Ollama/LM Studio 是否已开启且端口正确】"
        elif "401" in err_str or "auth" in err_str.lower():
            guide = "【解决建议：认证失败。请检查 API Key 是否正确填写】"
        else:
            guide = "【解决建议：模型发现失败，请根据下方原始提示检查配置】"
        return {"models": [], "error": f"{guide}<br>原始提示: {err_str}"}

@app.post("/api/ai/validate")
async def validate_ai(req: AiValidateRequest):
    return await DiagnosticsService.validate_ai_connectivity(req.provider, req.model, req.api_key, req.base_url)

@app.post("/api/init")
async def init_press(req: InitRequest):
    m_path = os.path.abspath(os.path.expanduser(req.manuscripts_path))
    
    # 🛡️ [V55.0] 准入预检：如果许可证受限，直接透传物理阻断原因
    if not LicenseGuard.is_pro_feature_allowed("multi_imprint"):
        if len(im.list_imprints()) >= 1:
            raise HTTPException(
                status_code=403,
                detail="社区版仅限划定 1 个版图。请升级至授权版以解锁多品牌版图管理。"
            )

    # 🚀 [V52.10] 物理主权确立
    if not im.init_sovereign_imprint(req.imprint_id, m_path, imprint_name=req.imprint_name):
        raise HTTPException(status_code=400, detail="创建失败：物理版图初始化异常，请检查文件夹权限或磁盘空间。")
    
    from core.config.config import CONFIG_IMPRINT_NAME, IMPRINT_DIR, CONFIG_DIR
    cfg_p = os.path.join(IMPRINT_DIR, req.imprint_id, CONFIG_DIR, CONFIG_IMPRINT_NAME)
    if os.path.exists(cfg_p):
        try:
            with open(cfg_p, 'r', encoding='utf-8') as f:
                cfg = yaml.safe_load(f) or {}
            cfg["active_theme"] = req.active_theme
            cfg["imprint_name"] = req.imprint_name
            cfg.setdefault("translation", {})["enable_ai"] = req.enable_ai
            if req.enable_ai and req.ai_api_key:
                cfg["translation"]["primary_node"] = "wizard"
                cfg["translation"]["providers"] = {
                    "wizard": {
                        "provider": req.ai_provider,
                        "model": req.ai_model,
                        "api_key": req.ai_api_key,
                        "base_url": req.ai_base_url
                    }
                }
            if req.target_langs:
                ln = {"en":"English","ja":"日本語","ko":"한국어","de":"Deutsch","fr":"Français","es":"Español"}
                cfg["i18n_settings"] = {"enabled":True, "source":{"lang_code":req.source_lang, "name":"中文"},
                    "targets":[{"lang_code":lc, "name":ln.get(lc,lc), "translate_body":True} for lc in req.target_langs]}
            with open(cfg_p, 'w', encoding='utf-8') as f:
                yaml.safe_dump(cfg, f, allow_unicode=True)
        except Exception as e:
            tlog.warning(f"Config Injection Failed: {e}")
            
    im.switch(req.imprint_id)

    # 🚀 [V52.10] 物理主权锁定：将当前品牌 ID 写入 config.local.yaml
    from core.config.config import CONFIG_LOCAL_NAME, CONFIG_NAME
    try:
        from core.config.config import load_config
        from core.config.config_models import Configuration
        
        # 尝试加载现有配置或创建一个全新的主权配置
        local_path = os.path.join(os.getcwd(), CONFIG_LOCAL_NAME)
        root_config_path = CONFIG_NAME
        
        if os.path.exists(root_config_path):
            config_obj = load_config(root_config_path)
        else:
            # 🛡️ 如果连基础配置都没有，我们手动构造一个最简主权模型
            config_obj = Configuration()
            
        # 合并本地覆盖
        if os.path.exists(local_path):
            try:
                with open(local_path, 'r', encoding='utf-8') as f:
                    local_data = yaml.safe_load(f) or {}
            except: pass

        # 写入核心主权参数
        config_obj.active_imprint = req.imprint_id
        
        # 🚀 [V52.10] 同步 AI 算力配置至全局覆盖层
        if req.enable_ai:
            from core.config.models.ai import TranslationProvider
            config_obj.translation.primary_node = "wizard"
            config_obj.translation.providers["wizard"] = TranslationProvider(
                type=req.ai_provider,
                model=req.ai_model,
                api_key=req.ai_api_key,
                base_url=req.ai_base_url
            )
        
        # 持久化至本地覆盖层
        config_obj.dump_to_disk(local_path)
        tlog.success(f"🛡️ [主权锁定] 品牌 '{req.imprint_id}' 及其 AI 算力配置已同步至 {local_path}。")
    except Exception as e:
        tlog.warning(f"Sovereignty Lock Failed: {e}")

    # 🚀 [V50.5] 物理装帧拷贝：将选定主题源文件克隆至品牌主权疆域
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

    # 🚀 [V50.5] 工业级原地接力
    # 既然端口已经分立 (43211 vs 43212)，我们不再需要杀掉进程
    # 只需要停止当前的向导 Web 服务，让主进程继续向下执行即可
    try:
        tlog.info("🔌 [自举激活] 向导配置完成，正在申请平滑切换至总编室 (Dashboard)...")
        
        # 🚀 [V50.5] 优雅停机协议：
        # 我们不再启动新进程，而是设置一个标志位让 uvicorn 退出循环
        def graceful_handoff():
            time.sleep(0.5)
            tlog.info("🏁 [向导归位] 引导任务圆满完成，正在移交主进程控制权...")
            if 'server_instance' in globals() and server_instance:
                server_instance.should_exit = True
            
        threading.Thread(target=graceful_handoff, daemon=True).start()
        tlog.info("  └── ✅ 信号已发出，主程序即将进入主权总编室模式。")
    except Exception as e:
        tlog.warning(f"Dashboard Handoff Failed: {e}")

    return {"status": "success", "imprint_id": req.imprint_name}

@app.post("/api/shutdown")
async def shutdown_wizard(request: Request):
    if 'server_instance' in globals() and server_instance:
        server_instance.should_exit = True
    return {"message": "done"}

# 🚀 全局服务器实例，用于实现跨线程停机
server_instance = None

def start_wizard_server(port: int = 43211):
    global server_instance
    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning")
    server_instance = uvicorn.Server(config)
    server_instance.run()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=43211)
    args = parser.parse_args()
    start_wizard_server(port=args.port)
