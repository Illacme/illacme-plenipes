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
                import shutil
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


@router.post("/api/config/style")
async def apply_translation_style(req: StyleRequest, request: Request) -> Dict[str, Any]:
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
    if engine:
        engine.config.translation.active_style = req.style
        engine.config.dump_to_disk(os.path.join(IMPRINT_DIR, target_imprint, CONFIG_DIR, CONFIG_IMPRINT_NAME))
    shutil.copy2(source_template, os.path.join(os.getcwd(), CONFIG_DIR, PROMPTS_NAME))
    return {"status": "success", "style": req.style}

@router.post("/api/governance/gc", dependencies=[Depends(verify_token)])
async def trigger_system_gc() -> Dict[str, Any]:
    """
    一键物理剪枝 (🧹 物理 GC)：唤醒清道夫回收幽灵路由、物理垃圾资产与 SQLite 孤儿账本。
    """
    engine = get_global_engine()
    if not engine:
        return {"status": "error", "message": "Engine not initialized"}
    if not hasattr(engine, "janitor") or engine.janitor is None:
        return {"status": "error", "message": "Janitor engine not initialized"}
    try:
        # 1. 扫描当前 vault_root 物理磁盘上的真实文件列表
        vault_root_abs = os.path.abspath(engine.vault_root) if getattr(engine, "vault_root", None) else ""
        current_source_files = set()
        if vault_root_abs and os.path.exists(vault_root_abs):
            for root, _, files in os.walk(vault_root_abs):
                for f in files:
                    if f.endswith(('.md', '.markdown')):
                        abs_p = os.path.join(root, f)
                        rel_p = os.path.relpath(abs_p, vault_root_abs).replace("\\", "/")
                        current_source_files.add(rel_p)

        # 2. 执行 SQLite 数据库中的孤儿账本擦除 (方案二履约)
        docs_snapshot = engine.meta.get_documents_snapshot()
        orphans = [p for p in docs_snapshot.keys() if p not in current_source_files]
        if orphans:
            for orphan in orphans:
                try:
                    engine.meta.remove_document(orphan)
                except Exception:
                    pass
            bus.emit("UI_TERMINAL_DATA", type="LOG", data=f"🧹 [物理 GC] 已成功擦除 {len(orphans)} 篇不在当前文库内的 SQLite 幽灵孤儿账本。")

        # 3. 执行幽灵节点与路由物理清洗
        engine.janitor.gc_ghost_nodes(is_dry_run=False)
        bus.emit("UI_TERMINAL_DATA", type="LOG", data="🧹 [一键物理剪枝] 物理 GC 成功！已物理回收幽灵路由与冗余 Markdown 资产。")
        return {"status": "success", "message": f"GC executed successfully. Cleaned {len(orphans)} orphan records."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/api/system/cache/stats", dependencies=[Depends(verify_token)])
async def get_cache_stats() -> Dict[str, Any]:
    """🛡️ [段落缓存治理] 获取缓存状态接口"""
    engine = get_global_engine()
    if not engine or not hasattr(engine, 'block_cache') or not engine.block_cache:
        return {"file_count": 0, "size_bytes": 0, "root": ""}
    
    root = engine.block_cache.root
    file_count = 0
    size_bytes = 0
    if os.path.exists(root):
        for dirpath, _, filenames in os.walk(root):
            for filename in filenames:
                if filename.endswith(".txt"):
                    file_count += 1
                    try:
                        size_bytes += os.path.getsize(os.path.join(dirpath, filename))
                    except Exception:
                        pass
    return {
        "file_count": file_count,
        "size_bytes": size_bytes,
        "root": root
    }

@router.post("/api/governance/cache/clear", dependencies=[Depends(verify_token)])
async def clear_block_cache() -> Dict[str, Any]:
    """🗑️ [段落缓存治理] 一键物理清除全量缓存接口"""
    engine = get_global_engine()
    if not engine or not hasattr(engine, 'block_cache') or not engine.block_cache:
        return {"status": "error", "message": "Block cache not initialized"}
    try:
        success = engine.block_cache.clear_all_cache()
        if success:
            bus.emit("UI_TERMINAL_DATA", type="LOG", data="🗑️ [一键缓存清空] 全量段落翻译缓存已被安全物理移除。")
            return {"status": "success", "message": "Block cache cleared successfully"}
        return {"status": "error", "message": "Failed to clear block cache"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.post("/api/governance/cache/migrate", dependencies=[Depends(verify_token)])
async def trigger_cache_migration(req: Dict[str, Any]) -> Dict[str, Any]:
    """🚚 [段落缓存治理] 手动触发物理迁移接口"""
    engine = get_global_engine()
    if not engine or not hasattr(engine, 'block_cache') or not engine.block_cache:
        return {"status": "error", "message": "Block cache not initialized"}
    try:
        old_levels = req.get("old_levels", 1)
        new_levels = req.get("new_levels", 1)
        old_dir = req.get("old_dir", None)
        new_dir = req.get("new_dir", None)
        
        engine.block_cache.migrate_cache(old_dir, new_dir, old_levels, new_levels)
        return {"status": "success", "message": "Cache migrated successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
