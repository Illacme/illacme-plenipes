# -*- coding: utf-8 -*-
"""
🧹 [V74.60] Cache & Ledger Maintenance Operations Shard
职责：分层缓存盘点（get_cache_stats）、物理剪枝（trigger_system_gc）、段落缓存清理、指纹/账本重置与缓存迁移。
🛡️ [SOP-02 模块拆分 / AEL-Iter-v10]
"""

import os
import shutil
from typing import Dict, Any
from core.runtime.engine_singleton import get_global_engine
from core.utils.event_bus import bus


async def trigger_system_gc_impl() -> Dict[str, Any]:
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


async def get_cache_stats_impl() -> Dict[str, Any]:
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


async def clear_block_cache_impl() -> Dict[str, Any]:
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


async def reset_fingerprints_only_impl() -> Dict[str, Any]:
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


async def rebuild_ledger_from_cache_impl() -> Dict[str, Any]:
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


async def clear_ai_meta_cache_impl() -> Dict[str, Any]:
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


async def clear_build_cache_impl() -> Dict[str, Any]:
    """🧹 [分层缓存] 仅清理 SSG 源码镜像与增量构建产物缓存"""
    engine = get_global_engine()
    if not engine:
        return {"status": "error", "message": "Engine not initialized"}
    try:
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


async def reset_ledger_impl() -> Dict[str, Any]:
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


async def reset_ledger_and_sync_impl() -> Dict[str, Any]:
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


async def trigger_cache_migration_impl(req: Dict[str, Any]) -> Dict[str, Any]:
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
