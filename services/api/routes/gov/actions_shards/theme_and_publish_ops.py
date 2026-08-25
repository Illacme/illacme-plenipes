# -*- coding: utf-8 -*-
"""
🎨 [V74.60] Theme, Publish & Style Operations Shard
职责：承载主题引导（bootstrap_theme）、发布触发（trigger_publish）、翻译风格更新（apply_translation_style）与 AI 导航翻译。
🛡️ [SOP-02 模块拆分 / AEL-Iter-v10]
"""

import os
import subprocess
import shutil
from fastapi import Request
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from core.runtime.engine_singleton import get_global_engine
from core.utils.tracing import tlog
from core.utils.event_bus import bus


class StyleRequest(BaseModel):
    style: str


class TranslateNavLabelsRequest(BaseModel):
    label: str
    target_languages: List[str]
    slot: Optional[str] = None
    source_language: Optional[str] = "zh"


async def bootstrap_theme_impl(req: Dict[str, Any]) -> Dict[str, Any]:
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
        
    # 📡 [V74.96] 离线预检自愈：若本地 static/vendor/theme-cache 下有高保真离线 Tar 压缩包，自动免网点火！
    cache_tar: str = os.path.join(os.getcwd(), "core", "api", "static", "vendor", "theme-cache", f"{theme_id}.tar.gz")
    if os.path.exists(cache_tar):
        bus.emit("UI_TERMINAL_DATA", type="LOG", data=f"  [📡 离线自愈] 发现本地离线包缓存: {os.path.basename(cache_tar)}，跳过网络，直接本地解压自愈点火...")
        try:
            import tarfile
            os.makedirs(target_path, exist_ok=True)
            with tarfile.open(cache_tar, "r:gz") as tar:
                tar.extractall(path=target_path)
            bus.emit("UI_TERMINAL_DATA", type="LOG", data=f"  [📡 离线自愈] 主题 {theme_id.upper()} 通过本地离线包已完美部署成功！")
            return {"status": "success", "message": "Theme initialized from local offline cache"}
        except Exception as e:
            bus.emit("UI_TERMINAL_DATA", type="LOG", data=f"  [🚨 离线自愈失败] 本地压缩包损坏: {e}")
            if os.path.exists(target_path):
                shutil.rmtree(target_path)
        
    bootstrap_cmds: Dict[str, str] = {
        "starlight": f"npx -y create-astro@latest {theme_id} --template starlight --no-install --no-git --yes",
        "docusaurus": f"npx -y create-docusaurus@latest {theme_id} classic --skip-install",
        "vitepress": f"mkdir -p {theme_id} && cd {theme_id} && npm init -y && node -e \"const fs=require('fs'); const p=JSON.parse(fs.readFileSync('package.json')); p.scripts={{dev:'vitepress dev',start:'vitepress dev',build:'vitepress build',preview:'vitepress preview'}}; fs.writeFileSync('package.json',JSON.stringify(p,null,2));\" && npm install -D vitepress",
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


async def trigger_publish_impl(req: Dict[str, Any]) -> Dict[str, Any]:
    """
    触发流式发布与物理同步。
    
    :param req: 包含发布模式（静态、干跑、沙盒）的请求字典。
    :return: 异步任务 ID 或错误信息。
    """
    engine = get_global_engine()
    if not engine:
        return {"error": "Engine not initialized"}
    
    # 🛡️ [V76.8] 翻译矩阵与算力可用性强关联校验熔断门禁 (同步拦截)
    try:
        from core.governance.checks.ai import check_ai_availability_or_raise
        check_ai_availability_or_raise(engine)
    except RuntimeError as e:
        return {"status": "error", "message": str(e)}

    try:
        mode: str = req.get("mode", "static")
        paths = req.get("paths", None)
        force: bool = req.get("force", False)
        clear_cache: bool = req.get("clear_cache", False)
        target_langs = req.get("target_langs", None)
        from core.runtime.orchestrator import start_asynchronous_sync
        task_id = start_asynchronous_sync(
            engine,
            dry_run=(mode == "dry-run"),
            force=force,
            clear_cache=clear_cache,
            sandbox=(mode == "sandbox"),
            requested_paths=paths,
            target_langs=target_langs
        )
        if task_id is None:
            return {"status": "error", "message": "Already running"}
        return {"status": "task_queued", "task_id": task_id}
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def apply_translation_style_impl(req: StyleRequest, request: Request) -> Dict[str, Any]:
    """
    应用翻译风格与方言模板。
    
    :param req: 包含风格名称的请求模型.
    :param request: 包含 Imprint-Id 请求头的请求对象。
    :return: 状态及当前风格。
    """
    engine = get_global_engine()
    if engine:
        enable_ai = getattr(engine.config.translation, "enable_ai", False) if engine.config.translation else False
        if not enable_ai:
            return {"status": "error", "message": "🛡️ [主权拦截] AI 算力当前处于关闭状态，无法应用翻译风格"}

    from core.governance.imprint_manager import im
    from core.config.config import IMPRINT_DIR, CONFIG_IMPRINT_NAME
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
    if engine:
        engine.config.translation.active_style = req.style
        engine.config.dump_to_disk(os.path.join(IMPRINT_DIR, target_imprint, CONFIG_DIR, CONFIG_IMPRINT_NAME))
    shutil.copy2(source_template, os.path.join(os.getcwd(), CONFIG_DIR, PROMPTS_NAME))
    return {"status": "success", "style": req.style}


async def translate_nav_labels_impl(req: TranslateNavLabelsRequest) -> Dict[str, Any]:
    """🤖 [AI 导航翻译] 将导航菜单标题快速翻译为指定的全部目标语言"""
    engine = get_global_engine()
    label = (req.label or "").strip()
    target_langs = req.target_languages or []
    if not label or not target_langs:
        return {"ok": True, "translations": {}}

    translations = {}
    from core.adapters.egress.ssg.base import SLOT_I18N_FALLBACK
    slot = (req.slot or "docs").lower()
    
    # 尝试获取 AI 算力节点
    node = None
    if engine and hasattr(engine, "config") and getattr(engine.config, "translation", None):
        try:
            from core.logic.ai.ai_factory import TranslatorFactory
            node = TranslatorFactory.create(engine.config.translation)
        except Exception:
            node = None

    for lang in target_langs:
        # 1. 若字典精准匹配已知标准槽位与常用中文名称，优先秒级回填
        if slot in SLOT_I18N_FALLBACK and lang in SLOT_I18N_FALLBACK[slot]:
            dict_val = SLOT_I18N_FALLBACK[slot][lang]
            if label in ["文档中心", "官方博客", "展示页面", "自定义频道", "Docs", "Blog", "Showcase", "Pages", slot]:
                translations[lang] = dict_val
                continue

        # 2. 调用大模型 AI 进行高保真翻译
        if node:
            try:
                from core.logic.ai.ai_logic_hub import AILogicHub
                rem = f"Translate this short website navigation title concisely into {lang}. Output only the translated title (1-3 words), no punctuation, no quotes, no markdown."
                translated = node.translate(label, source_lang=req.source_language or "auto", target_lang=lang, remedy_instruction=rem)
                clean_res = AILogicHub.clean_metadata_value(translated or "") if translated else ""
                if clean_res:
                    translations[lang] = clean_res
                    continue
            except Exception as e:
                tlog.warning(f"AI translation for nav label '{label}' into {lang} failed: {e}")

        # 3. 降级回退
        if slot in SLOT_I18N_FALLBACK and lang in SLOT_I18N_FALLBACK[slot]:
            translations[lang] = SLOT_I18N_FALLBACK[slot][lang]
        else:
            translations[lang] = label

    return {"ok": True, "translations": translations}
