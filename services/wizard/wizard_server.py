import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import List, Optional
from services.wizard.wizard_ops import (
    probe_nodes_logic,
    list_files_logic,
    get_ai_models_logic,
    validate_ai_logic,
    init_press_logic
)

app = FastAPI(title="Illacme Plenipes Wizard")
STATIC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "web", "wizard"))
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

class InitRequest(BaseModel):
    imprint_id: Optional[str] = None
    imprint_name: Optional[str] = None
    press_name: Optional[str] = None
    manuscripts_path: str
    active_theme: str = "default"
    enable_ai: bool = False
    ai_provider: str = "openai"
    ai_model: str = "gpt-4o-mini"
    ai_api_key: str = ""
    ai_base_url: str = ""
    source_lang: str = "zh"
    target_langs: List[str] = []
    active_dialect: Optional[str] = "auto"
    github_token: Optional[str] = ""
    github_repo: Optional[str] = ""
    cloudflare_token: Optional[str] = ""
    cloudflare_project: Optional[str] = ""

class FsRequest(BaseModel):
    path: str = "."

class AiValidateRequest(BaseModel):
    provider: str
    model: Optional[str] = "default"
    api_key: str
    base_url: Optional[str] = None

@app.get("/", response_class=HTMLResponse)
async def get_wizard():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if not os.path.exists(index_file):
        return "<h1>Assets Missing</h1>"
    with open(index_file, "r", encoding="utf-8") as f:
        return f.read()

@app.get("/favicon.ico", include_in_schema=False)
async def favicon() -> FileResponse:
    """提供向导服务的 Favicon 皇家图标"""
    logo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "web", "dashboard", "logo.png"))
    return FileResponse(logo_path)

@app.get("/api/probe")
async def probe_nodes():
    return probe_nodes_logic()

@app.post("/api/fs/ls")
async def list_files(req: FsRequest):
    return list_files_logic(req)

@app.post("/api/ai/models")
async def get_ai_models(req: AiValidateRequest):
    return await get_ai_models_logic(req)

@app.post("/api/ai/validate")
async def validate_ai(req: AiValidateRequest):
    return await validate_ai_logic(req)

@app.post("/api/init")
async def init_press(req: InitRequest):
    def shutdown_cb():
        global server_instance
        if server_instance:
            server_instance.should_exit = True
    return init_press_logic(req, shutdown_cb=shutdown_cb)

@app.post("/api/shutdown")
async def shutdown_wizard(request: Request):
    global server_instance
    if server_instance:
        server_instance.should_exit = True
    return {"message": "done"}

@app.get("/api/auth/callback", response_class=HTMLResponse)
async def auth_callback(token: str, extra: Optional[str] = "", provider: str = "github"):
    """
    🌐 OAuth 本地回环接口
    接收来自中继服务器传回的 Token 与配置参数，通过 HTML5 postMessage 安全回传给父向导，并关闭自身窗口。
    """
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Sovereign Auth Success</title>
        <style>
            body {{
                background: #08080f;
                color: #e8e8f0;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                display: flex;
                align-items: center;
                justify-content: center;
                height: 100vh;
                margin: 0;
            }}
            .card {{
                background: rgba(255,255,255,0.03);
                border: 1px solid rgba(255,255,255,0.08);
                padding: 40px;
                border-radius: 20px;
                text-align: center;
                max-width: 400px;
                box-shadow: 0 20px 50px rgba(0,0,0,0.3);
            }}
            h2 {{ color: #00f2ff; margin-bottom: 10px; font-weight: 600; }}
            p {{ color: #888; font-size: 0.9rem; line-height: 1.6; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h2>✅ 授权绑定成功</h2>
            <p>主权凭证已安全注入您的本地总编室。此窗口正在自动关闭...</p>
        </div>
        <script>
            if (window.opener) {{
                window.opener.postMessage({{
                    type: 'auth_success',
                    provider: '{provider}',
                    token: '{token}',
                    extra: '{extra}'
                }}, '*');
            }}
            setTimeout(function() {{
                window.close();
            }}, 1200);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

server_instance = None

def start_wizard_server(port: int = 43211):
    global server_instance
    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning")
    server_instance = uvicorn.Server(config)
    server_instance.run()

if __name__ == "__main__":
    start_wizard_server()
