# -*- coding: utf-8 -*-
"""
🛡️ [V74.60] Gov Actions & Theme Execution Routes
职责：承载主题引导（bootstrap_theme）、发布触发（trigger_publish）与翻译风格更新（apply_translation_style）等高级写入与调度动作。
"""

import os
import subprocess
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from typing import Dict, Any, Optional
from core.runtime.engine_singleton import get_global_engine
from core.utils.tracing import tlog
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
    """🛡️ [分层缓存治理] 获取全域多层缓存状态与盘点接口"""
    engine = get_global_engine()
    if not engine:
        return {"file_count": 0, "size_bytes": 0, "meta_file_count": 0, "meta_size_bytes": 0, "build_size_bytes": 0, "root": ""}
    
    # 1. 段落缓存盘点
    file_count = 0
    size_bytes = 0
    root = getattr(engine.block_cache, 'root', '') if hasattr(engine, 'block_cache') and engine.block_cache else ''
    if root and os.path.exists(root):
        for dirpath, _, filenames in os.walk(root):
            for filename in filenames:
                if filename.endswith(".txt"):
                    file_count += 1
                    try: size_bytes += os.path.getsize(os.path.join(dirpath, filename))
                    except Exception: pass

    # 2. 元信息物理文件盘点
    meta_count = 0
    meta_size = 0
    if hasattr(engine, 'meta') and engine.meta and hasattr(engine.meta, 'file_store') and engine.meta.file_store:
        meta_count, meta_size = engine.meta.file_store.count_and_size()

    # 3. 源码镜像与构建产物盘点
    build_size = 0
    try:
        vault_cache = engine.config.get_vault_cache_dir()
        for sub_name in ["sources", "build", "runtime"]:
            sub_dir = os.path.join(vault_cache, sub_name)
            if os.path.exists(sub_dir):
                for dirpath, _, filenames in os.walk(sub_dir):
                    for filename in filenames:
                        try: build_size += os.path.getsize(os.path.join(dirpath, filename))
                        except Exception: pass
    except Exception: pass

    return {
        "file_count": file_count,
        "size_bytes": size_bytes,
        "meta_file_count": meta_count,
        "meta_size_bytes": meta_size,
        "build_size_bytes": build_size,
        "root": root
    }

@router.post("/api/governance/cache/clear", dependencies=[Depends(verify_token)])
async def clear_block_cache() -> Dict[str, Any]:
    """🗑️ [分层缓存] 仅清空段落翻译缓存 (Block Cache)"""
    engine = get_global_engine()
    if not engine or not hasattr(engine, 'block_cache') or not engine.block_cache:
        return {"status": "error", "message": "Block cache not initialized"}
    try:
        success = engine.block_cache.clear_all_cache()
        if success:
            bus.emit("UI_TERMINAL_DATA", type="LOG", data="🗑️ [分层缓存] 全量段落翻译缓存已物理安全抹除。")
            return {"status": "success", "message": "Block cache cleared successfully"}
        return {"status": "error", "message": "Failed to clear block cache"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.post("/api/governance/ledger/reset-fingerprints", dependencies=[Depends(verify_token)])
async def reset_fingerprints_only() -> Dict[str, Any]:
    """⚡ [分层缓存] 仅重置文档指纹 (0 LLM 算力消耗重编译)"""
    engine = get_global_engine()
    if not engine or not hasattr(engine, 'meta') or not engine.meta:
        return {"status": "error", "message": "Metadata manager not initialized"}
    try:
        engine.meta.clear_fingerprints_only()
        bus.emit("UI_TERMINAL_DATA", type="LOG", data="⚡ [指纹重置] 文档哈希指纹已成功清空（AI Slug/SEO 及译文已完整保留，下次发布将 0 算力开销全量重编译）。")
        return {"status": "success", "message": "文档指纹已成功清空，AI 译文与元数据已保留"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.post("/api/governance/ledger/rebuild-from-cache", dependencies=[Depends(verify_token)])
async def rebuild_ledger_from_cache() -> Dict[str, Any]:
    """🩹 [分层缓存] 从本地物理元信息快照自愈重建 SQLite 账本"""
    engine = get_global_engine()
    if not engine or not hasattr(engine, 'meta') or not engine.meta:
        return {"status": "error", "message": "Metadata manager not initialized"}
    try:
        count = engine.meta.rebuild_from_file_cache()
        bus.emit("UI_TERMINAL_DATA", type="LOG", data=f"🩹 [账本自愈] 成功从物理元信息镜像恢复 {count} 篇文档账本记录！")
        return {"status": "success", "message": f"成功从物理快照自愈恢复 {count} 篇文档记录", "count": count}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.post("/api/governance/cache/ai-meta/clear", dependencies=[Depends(verify_token)])
async def clear_ai_meta_cache() -> Dict[str, Any]:
    """🏷️ [分层缓存] 仅清空 AI 生成的 Slug 与 SEO 描述缓存"""
    engine = get_global_engine()
    if not engine or not hasattr(engine, 'meta') or not engine.meta:
        return {"status": "error", "message": "Metadata manager not initialized"}
    try:
        engine.meta.clear_ai_metadata(mode="all")
        bus.emit("UI_TERMINAL_DATA", type="LOG", data="🏷️ [元数据重塑] AI 生成的 Slug 与 SEO 描述缓存已成功重置。")
        return {"status": "success", "message": "AI Slug 与 SEO 元数据已清空"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.post("/api/governance/cache/build/clear", dependencies=[Depends(verify_token)])
async def clear_build_cache() -> Dict[str, Any]:
    """🧹 [分层缓存] 仅清理 SSG 源码镜像与增量构建产物缓存"""
    engine = get_global_engine()
    if not engine:
        return {"status": "error", "message": "Engine not initialized"}
    try:
        import shutil
        vault_cache = engine.config.get_vault_cache_dir()
        cleaned_dirs = []
        for sub_name in ["sources", "build", "runtime"]:
            target_dir = os.path.join(vault_cache, sub_name)
            if os.path.exists(target_dir):
                shutil.rmtree(target_dir)
                os.makedirs(target_dir, exist_ok=True)
                cleaned_dirs.append(sub_name)
        bus.emit("UI_TERMINAL_DATA", type="LOG", data=f"🧹 [构建清理] 已成功清理编译产物缓存: {', '.join(cleaned_dirs) or '无'}")
        return {"status": "success", "message": f"已清理构建缓存目录: {', '.join(cleaned_dirs)}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.post("/api/governance/ledger/reset", dependencies=[Depends(verify_token)])
async def reset_ledger() -> Dict[str, Any]:
    """🔄 [全域重置] 物理重置 SQLite 账本中的全部文档记录与哈希指纹"""
    engine = get_global_engine()
    if not engine:
        return {"status": "error", "message": "Engine not initialized"}
    try:
        if hasattr(engine, 'meta') and engine.meta:
            engine.meta.clear_all_documents(clear_files=True)
        bus.emit("UI_TERMINAL_DATA", type="LOG", data="🔄 [账本重置] 全域文档指纹账本与元信息镜像已被安全重置归零。")
        return {"status": "success", "message": "文档指纹账本已成功重置归零"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.post("/api/governance/reset-and-sync", dependencies=[Depends(verify_token)])
async def reset_ledger_and_sync() -> Dict[str, Any]:
    """🔄 [一键全量重译与发布] 清空段落缓存、重置文档指纹账本并强行触发全量 AI 翻译与出版"""
    engine = get_global_engine()
    if not engine:
        return {"status": "error", "message": "Engine not initialized"}
    
    # 🛡️ [AI 可用性前置拦截]
    try:
        from core.governance.checks.ai import check_ai_availability_or_raise
        check_ai_availability_or_raise(engine)
    except RuntimeError as e:
        return {"status": "error", "message": str(e)}

    try:
        # 1. 物理清空段落翻译缓存
        if hasattr(engine, 'block_cache') and engine.block_cache:
            engine.block_cache.clear_all_cache()

        # 2. 物理清空/重置 SQLite 账本中的文档指纹与历史译文记录
        if hasattr(engine, 'meta') and engine.meta:
            engine.meta.clear_all_documents()

        # 3. 异步启动全量强制点火 (force=True, clear_cache=True)
        from core.runtime.orchestrator import start_asynchronous_sync
        future_id = start_asynchronous_sync(
            engine,
            dry_run=False,
            force=True,
            clear_cache=True,
            sandbox=False
        )
        if future_id is None or future_id == 0:
            return {"status": "rejected", "message": "已有发布任务正在后台运行"}
        
        bus.emit("UI_TERMINAL_DATA", type="LOG", data="🔄 [全量重译点火] 已成功清空段落缓存并重置指纹账本，已强行唤醒 AI 算力中心对所有多语言页面进行全新翻译与出版！")
        return {
            "status": "started",
            "future_id": future_id,
            "message": "全量重译与发布流水线已启动"
        }
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


class TranslateNavLabelsRequest(BaseModel):
    label: str
    target_languages: list[str]
    slot: Optional[str] = None
    source_language: Optional[str] = "zh"

@router.post("/api/governance/translate-nav-labels", dependencies=[Depends(verify_token)])
async def translate_nav_labels(req: TranslateNavLabelsRequest) -> Dict[str, Any]:
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
