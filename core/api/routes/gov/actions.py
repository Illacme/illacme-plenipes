# -*- coding: utf-8 -*-
"""
🛡️ [V74.60] Gov Actions & Theme Execution Routes
职责：承载主题引导（bootstrap_theme）、发布触发（trigger_publish）与翻译风格更新（apply_translation_style）等高级写入与调度动作。
"""

import os
import subprocess
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from typing import Dict, Any
from core.runtime.engine_singleton import get_global_engine
from ..system import verify_token
from core.utils.event_bus import bus

router = APIRouter()

class StyleRequest(BaseModel):
    style: str

@router.post("/api/themes/bootstrap", dependencies=[Depends(verify_token)])
async def bootstrap_theme(req: Dict[str, Any]) -> Dict[str, Any]:
    """
    引导安装与重构主题。
    
    :param req: 包含主题 ID 的请求字典。
    :return: 状态及执行日志。
    """
    theme_id: str = req.get("id", "")
    if not theme_id:
        return {"status": "error", "message": "Missing theme ID"}
        
    from core.config.config import THEMES_DIR
    target_path: str = os.path.join(os.getcwd(), THEMES_DIR, theme_id)
    if os.path.exists(target_path):
        return {"status": "error", "message": "Assets exist"}
        
    bootstrap_cmds: Dict[str, str] = {
        "starlight": f"npx -y create-astro@latest {theme_id} --template starlight --no-install --no-git --yes",
        "docusaurus": f"npx -y create-docusaurus@latest {theme_id} classic --skip-install",
        "vitepress": f"mkdir -p {theme_id} && cd {theme_id} && npm init -y && npm install -D vitepress",
        "nextra": f"npx -y create-nextra-app@latest {theme_id} --example docs"
    }
    cmd: str = bootstrap_cmds.get(theme_id, "")
    if not cmd:
        return {"status": "error", "message": "Unsupported engine"}
        
    env: Dict[str, str] = os.environ.copy()
    env["CI"] = "true"
    process = subprocess.Popen(
        cmd,
        shell=True,
        cwd=os.path.join(os.getcwd(), THEMES_DIR),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=env
    )
    for line in process.stdout:
        bus.emit("UI_TERMINAL_DATA", type="LOG", data=f"  [CLI] {line.strip()}")
    process.wait()
    if process.returncode == 0:
        if theme_id == "docusaurus":
            os.makedirs(os.path.join(target_path, "docs"), exist_ok=True)
            with open(os.path.join(target_path, "docs", "intro.md"), "w", encoding="utf-8") as f:
                f.write("# Welcome")
        return {"status": "success", "message": "Theme initialized"}
    return {"status": "error", "message": f"Failed (Code: {process.returncode})"}

@router.post("/api/publish/trigger", dependencies=[Depends(verify_token)])
async def trigger_publish(req: Dict[str, Any]) -> Dict[str, Any]:
    """
    触发流式发布与物理同步。
    
    :param req: 包含发布模式（静态、干跑、沙盒）的请求字典。
    :return: 异步任务 ID 或错误信息。
    """
    engine = get_global_engine()
    if not engine:
        return {"error": "Engine not initialized"}
    try:
        mode: str = req.get("mode", "static")
        from core.runtime.orchestrator import start_asynchronous_sync
        task_id = start_asynchronous_sync(
            engine,
            dry_run=(mode == "dry-run"),
            sandbox=(mode == "sandbox")
        )
        if task_id is None:
            return {"status": "error", "message": "Already running"}
        return {"status": "task_queued", "task_id": task_id}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.post("/api/config/style")
async def apply_translation_style(req: StyleRequest, request: Request) -> Dict[str, Any]:
    """
    应用翻译风格与方言模板。
    
    :param req: 包含风格名称的请求模型。
    :param request: 包含 Imprint-Id 请求头的请求对象。
    :return: 状态及当前风格。
    """
    from core.governance.imprint_manager import im
    from core.config.config import IMPRINT_DIR, CONFIG_IMPRINT_NAME
    import shutil
    imprint_id = request.headers.get("Imprint-Id")
    target_imprint = imprint_id or im.get_active_imprint()
    if not target_imprint:
        return {"status": "error", "message": "No active imprint"}
    from core.config.config import PROMPTS_NAME, DIALECTS_DIR, DEFAULT_DIALECT_NAME, CONFIG_DIR, PROMPTS_TEMPLATES_DIR
    source_template = os.path.join(os.getcwd(), CONFIG_DIR, PROMPTS_TEMPLATES_DIR, f"{req.style}.yaml")
    if not os.path.exists(source_template):
        return {"status": "error", "message": f"Template {req.style} not found"}
    target_dir = os.path.join(im.imprint_root, target_imprint, CONFIG_DIR, DIALECTS_DIR)
    os.makedirs(target_dir, exist_ok=True)
    shutil.copy2(source_template, os.path.join(target_dir, f"{req.style}.yaml"))
    shutil.copy2(source_template, os.path.join(target_dir, DEFAULT_DIALECT_NAME))
    engine = get_global_engine()
    if engine:
        engine.config.translation.active_style = req.style
        engine.config.dump_to_disk(os.path.join(IMPRINT_DIR, target_imprint, CONFIG_DIR, CONFIG_IMPRINT_NAME))
    shutil.copy2(source_template, os.path.join(os.getcwd(), CONFIG_DIR, PROMPTS_NAME))
    return {"status": "success", "style": req.style}
