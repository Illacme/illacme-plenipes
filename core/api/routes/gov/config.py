# -*- coding: utf-8 -*-
"""
🛡️ [V74.55] Gov Configuration & Execution Routes
职责：承载全量配置审计、更新、主权同步以及出版指令触发路由。
架构：已从 governance.py 物理降解，实现业务逻辑的原子化隔离。
"""

import os
import yaml
from fastapi import APIRouter, Depends, Request
from typing import Optional
from core.runtime.cli_bootstrap import get_global_engine
from ..system import verify_token
from core.config.config import CONFIG_NAME, CONFIG_LOCAL_NAME, IMPRINT_DIR, CONFIG_DIR, CONFIG_IMPRINT_NAME
from core.utils.tracing import tlog
from core.utils.event_bus import bus
from pydantic import BaseModel

router = APIRouter()

class StyleRequest(BaseModel):
    style: str

@router.get("/api/system/config", dependencies=[Depends(verify_token)])
def get_full_config(level: str = "merged", imprint_id: Optional[str] = None):
    engine = get_global_engine()
    if not engine: return {"error": "Engine not initialized"}
    
    from core.config.governance_map import GOVERNANCE_RULES
    from core.governance.license_guard import LicenseGuard
    
    if level == "merged":
        data = engine.config.model_dump()
        data["_governance_rules"] = GOVERNANCE_RULES
        data["_is_licensed"] = LicenseGuard.is_licensed()
        return data
    
    path = CONFIG_NAME
    if level == "local":
        path = CONFIG_LOCAL_NAME
    elif level == "imprint":
        target_id = imprint_id or engine.im.get_active_imprint()
        path = os.path.join(IMPRINT_DIR, target_id, CONFIG_DIR, CONFIG_IMPRINT_NAME)
    
    data = {}
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
        except:
            data = {"error": f"Failed to parse {path}"}
    else:
        data = {"error": f"File {path} not found"}
        
    return {
        "config": data,
        "governance_rules": GOVERNANCE_RULES
    }

@router.post("/api/config/update", dependencies=[Depends(verify_token)])
async def update_config(req: dict, imprint_id: Optional[str] = None):
    engine = get_global_engine()
    if not engine: return {"error": "Engine not initialized"}
    
    from core.config.governance_map import resolve_governance_level
    routing_groups = {"local": {}, "imprint": {}, "global": {}}
    
    for key, value in req.items():
        if key == "_level": continue
        level = resolve_governance_level(key)
        if imprint_id: level = "imprint"
        routing_groups[level][key] = value
        
        if not imprint_id or imprint_id == engine.im.get_active_imprint():
            parts = key.split('.')
            target = engine.config
            for part in parts[:-1]:
                if isinstance(target, dict):
                    target = target.get(part)
                elif hasattr(target, part):
                    target = getattr(target, part)
                else:
                    target = None
                    break
            
            if target:
                final_key = parts[-1]
                if isinstance(target, dict):
                    target[final_key] = value
                elif hasattr(target, final_key):
                    if key == "i18n_settings.targets" and isinstance(value, list):
                        from core.governance.license_guard import LicenseGuard
                        if not LicenseGuard.is_licensed() and len(value) > 1:
                            return {"status": "error", "error": "🛡️ [主权拦截] 社区版仅支持 1 个目标语种。"}
                        from core.config.config_models import I18nTarget
                        from core.utils.language_hub import LanguageHub
                        new_targets = []
                        for code in value:
                            name = LanguageHub.resolve_to_name(code)
                            iso = LanguageHub.resolve_to_iso(code)
                            new_targets.append(I18nTarget(lang_code=iso, name=name, prompt_lang=name))
                        value = new_targets
                        routing_groups[level][key] = [t.model_dump() for t in value]
                    elif key == "i18n_settings.source.lang_code" and isinstance(value, str):
                        from core.utils.language_hub import LanguageHub
                        name = LanguageHub.resolve_to_name(value)
                        if hasattr(target, 'name'): target.name = name
                        routing_groups[level]["i18n_settings.source.name"] = name
                    
                    if final_key == "publishing_mode":
                        from core.config.models.governance import PublishingMode
                        try: value = PublishingMode(value)
                        except: pass
                    elif final_key == "seo_strategy":
                        from core.config.models.governance import SeoStrategy
                        try: value = SeoStrategy(value)
                        except: pass
                    setattr(target, final_key, value)

    def make_yaml_safe(data):
        if hasattr(data, 'model_dump'): return data.model_dump()
        if isinstance(data, dict): return {k: make_yaml_safe(v) for k, v in data.items()}
        if isinstance(data, list): return [make_yaml_safe(v) for v in data]
        return data

    target_imprint = imprint_id or engine.im.get_active_imprint()
    paths = {
        "local": CONFIG_LOCAL_NAME,
        "imprint": os.path.join(IMPRINT_DIR, target_imprint, CONFIG_DIR, CONFIG_IMPRINT_NAME) if target_imprint else None,
        "global": CONFIG_NAME
    }
    
    file_data = {}
    for lvl, path in paths.items():
        if path and os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    file_data[lvl] = yaml.safe_load(f) or {}
            except: file_data[lvl] = {}
        else: file_data[lvl] = {}

    dirty_levels = set()
    for lvl, fields in routing_groups.items():
        if not fields: continue
        dest_data = file_data[lvl]
        for k, v in fields.items():
            k_parts = k.split('.')
            d = dest_data
            for p in k_parts[:-1]:
                if p not in d: d[p] = {}
                d = d[p]
            d[k_parts[-1]] = make_yaml_safe(v)
            dirty_levels.add(lvl)
            if lvl == "imprint" and not imprint_id:
                ld = file_data["local"]
                for p in k_parts[:-1]:
                    if ld and p in ld and isinstance(ld[p], dict): ld = ld[p]
                    else:
                        ld = None
                        break
                if ld and k_parts[-1] in ld:
                    del ld[k_parts[-1]]
                    dirty_levels.add("local")

    for lvl, path in paths.items():
        if not path or lvl not in dirty_levels: continue
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                yaml.safe_dump(make_yaml_safe(file_data[lvl]), f, allow_unicode=True, sort_keys=False)
        except Exception as e: tlog.error(f"❌ 落盘失败: {path} - {e}")
            
    if not imprint_id or imprint_id == engine.im.get_active_imprint():
        engine.active_theme = engine.config.active_theme
        engine.vault_root = engine.config.vault_root
        
        if "active_theme" in req:
            theme_id = req["active_theme"]
            from core.config.config import THEMES_DIR
            local_theme_path = os.path.join(engine.config.system.data_root, THEMES_DIR, theme_id)
            global_theme_path = os.path.join(os.getcwd(), THEMES_DIR, theme_id)
            if not os.path.exists(local_theme_path) and os.path.exists(global_theme_path):
                import shutil
                shutil.copytree(global_theme_path, local_theme_path, dirs_exist_ok=True, ignore=shutil.ignore_patterns('node_modules', '.git', '.DS_Store'))
            
            from core.adapters.egress.ssg import SSGAdapter
            from core.config.config import ThemeSettings
            temp_adapter = SSGAdapter(ThemeSettings(name=theme_id), engine=engine)
            slots = temp_adapter.get_feature_slots()
            is_i18n = engine.config.i18n_settings.enable_multilingual and len(engine.config.i18n_settings.targets) > 0
            if hasattr(engine.config, "output_paths"):
                for slot_id, slot_cfg in slots.items():
                    rel_path = slot_cfg["multi" if is_i18n else "single"]
                    engine.config.output_paths[f"{slot_id}_dir"] = os.path.join(THEMES_DIR, theme_id, rel_path)

        from core.runtime.engine_factory import EngineFactory
        EngineFactory._init_paths_and_adapters(engine)
        bus.emit("CONFIG_RELOADED", config=engine.config)
            
    return {"status": "success", "active_config": engine.config.model_dump()}

@router.post("/api/config/style")
async def apply_translation_style(req: StyleRequest, request: Request):
    from core.governance.imprint_manager import im
    import shutil
    imprint_id = request.headers.get("Imprint-Id")
    target_imprint = imprint_id or im.get_active_imprint()
    if not target_imprint: return {"status": "error", "message": "No active imprint"}
    from core.config.config import PROMPTS_NAME, DIALECTS_DIR, DEFAULT_DIALECT_NAME, CONFIG_DIR, PROMPTS_TEMPLATES_DIR
    source_template = os.path.join(os.getcwd(), CONFIG_DIR, PROMPTS_TEMPLATES_DIR, f"{req.style}.yaml")
    if not os.path.exists(source_template): return {"status": "error", "message": f"Template {req.style} not found"}
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

@router.post("/api/themes/bootstrap", dependencies=[Depends(verify_token)])
async def bootstrap_theme(req: dict):
    theme_id = req.get("id")
    if not theme_id: return {"status": "error", "message": "Missing theme ID"}
    import subprocess
    from core.config.config import THEMES_DIR
    target_path = os.path.join(os.getcwd(), THEMES_DIR, theme_id)
    if os.path.exists(target_path): return {"status": "error", "message": "Assets exist"}
    bootstrap_cmds = {
        "starlight": f"npx -y create-astro@latest {theme_id} --template starlight --no-install --no-git --yes",
        "docusaurus": f"npx -y create-docusaurus@latest {theme_id} classic --skip-install",
        "vitepress": f"mkdir -p {theme_id} && cd {theme_id} && npm init -y && npm install -D vitepress",
        "nextra": f"npx -y create-nextra-app@latest {theme_id} --example docs"
    }
    cmd = bootstrap_cmds.get(theme_id)
    if not cmd: return {"status": "error", "message": "Unsupported engine"}
    env = os.environ.copy()
    env["CI"] = "true"
    process = subprocess.Popen(cmd, shell=True, cwd=os.path.join(os.getcwd(), THEMES_DIR), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env)
    for line in process.stdout: bus.emit("UI_TERMINAL_DATA", type="LOG", data=f"  [CLI] {line.strip()}")
    process.wait()
    if process.returncode == 0:
        if theme_id == "docusaurus":
            os.makedirs(os.path.join(target_path, "docs"), exist_ok=True)
            with open(os.path.join(target_path, "docs", "intro.md"), "w", encoding="utf-8") as f: f.write("# Welcome")
        return {"status": "success", "message": "Theme initialized"}
    return {"status": "error", "message": f"Failed (Code: {process.returncode})"}

@router.post("/api/publish/trigger", dependencies=[Depends(verify_token)])
async def trigger_publish(req: dict):
    engine = get_global_engine()
    if not engine: return {"error": "Engine not initialized"}
    try:
        mode = req.get("mode", "static")
        from core.runtime.orchestrator import start_asynchronous_sync
        task_id = start_asynchronous_sync(engine, dry_run=(mode == "dry-run"), sandbox=(mode == "sandbox"))
        if task_id is None: return {"status": "error", "message": "Already running"}
        return {"status": "task_queued", "task_id": task_id}
    except Exception as e: return {"status": "error", "message": str(e)}
