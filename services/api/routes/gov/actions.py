# -*- coding: utf-8 -*-
"""
🛡️ [V74.60] Gov Actions & Theme Execution Routes
职责：承载主题引导（bootstrap_theme）、发布触发（trigger_publish）、翻译风格（apply_translation_style）、
      分层缓存治理与系统维护等高级写入与调度动作的路由门面。
架构：已按照 SOP-02 完成物理拆分，底层逻辑已解耦至 actions_shards/。
"""

from fastapi import APIRouter, Depends, Request
from typing import Dict, Any
from ..system import verify_token
from .actions_shards.theme_and_publish_ops import (
    StyleRequest,
    TranslateNavLabelsRequest,
    bootstrap_theme_impl,
    trigger_publish_impl,
    apply_translation_style_impl,
    translate_nav_labels_impl
)
from .actions_shards.cache_and_maintenance_ops import (
    trigger_system_gc_impl,
    get_cache_stats_impl,
    clear_block_cache_impl,
    reset_fingerprints_only_impl,
    rebuild_ledger_from_cache_impl,
    clear_ai_meta_cache_impl,
    clear_build_cache_impl,
    reset_ledger_impl,
    reset_ledger_and_sync_impl,
    trigger_cache_migration_impl
)

router = APIRouter()


# =========================================================================
# 🎨 1. 主题装帧、发布调度与风格模板路由
# =========================================================================

@router.post("/api/themes/bootstrap", dependencies=[Depends(verify_token)])
async def bootstrap_theme(req: Dict[str, Any]) -> Dict[str, Any]:
    """引导安装与重构主题。"""
    return await bootstrap_theme_impl(req)


@router.post("/api/publish/trigger", dependencies=[Depends(verify_token)])
async def trigger_publish(req: Dict[str, Any]) -> Dict[str, Any]:
    """触发流式发布与物理同步。"""
    return await trigger_publish_impl(req)


@router.post("/api/config/style")
async def apply_translation_style(req: StyleRequest, request: Request) -> Dict[str, Any]:
    """应用翻译风格与方言模板。"""
    return await apply_translation_style_impl(req, request)


@router.post("/api/governance/translate-nav-labels", dependencies=[Depends(verify_token)])
async def translate_nav_labels(req: TranslateNavLabelsRequest) -> Dict[str, Any]:
    """🤖 [AI 导航翻译] 将导航菜单标题快速翻译为指定的全部目标语言"""
    return await translate_nav_labels_impl(req)


# =========================================================================
# 🧹 2. 分层缓存治理、账本运维与物理剪枝路由
# =========================================================================

@router.post("/api/governance/gc", dependencies=[Depends(verify_token)])
async def trigger_system_gc() -> Dict[str, Any]:
    """一键物理剪枝 (🧹 物理 GC)：唤醒清道夫回收幽灵路由、物理垃圾资产与 SQLite 孤儿账本。"""
    return await trigger_system_gc_impl()


@router.get("/api/system/cache/stats", dependencies=[Depends(verify_token)])
async def get_cache_stats() -> Dict[str, Any]:
    """🛡️ [分层缓存治理] 获取全域多层缓存状态与盘点接口"""
    return await get_cache_stats_impl()


@router.post("/api/governance/cache/clear", dependencies=[Depends(verify_token)])
async def clear_block_cache() -> Dict[str, Any]:
    """🗑️ [分层缓存] 仅清空段落翻译缓存 (Block Cache)"""
    return await clear_block_cache_impl()


@router.post("/api/governance/ledger/reset-fingerprints", dependencies=[Depends(verify_token)])
async def reset_fingerprints_only() -> Dict[str, Any]:
    """⚡ [分层缓存] 仅重置文档指纹 (0 LLM 算力消耗重编译)"""
    return await reset_fingerprints_only_impl()


@router.post("/api/governance/ledger/rebuild-from-cache", dependencies=[Depends(verify_token)])
async def rebuild_ledger_from_cache() -> Dict[str, Any]:
    """🩹 [分层缓存] 从本地物理元信息快照自愈重建 SQLite 账本"""
    return await rebuild_ledger_from_cache_impl()


@router.post("/api/governance/cache/ai-meta/clear", dependencies=[Depends(verify_token)])
async def clear_ai_meta_cache() -> Dict[str, Any]:
    """🏷️ [分层缓存] 仅清空 AI 生成的 Slug 与 SEO 描述缓存"""
    return await clear_ai_meta_cache_impl()


@router.post("/api/governance/cache/build/clear", dependencies=[Depends(verify_token)])
async def clear_build_cache() -> Dict[str, Any]:
    """🧹 [分层缓存] 仅清理 SSG 源码镜像与增量构建产物缓存"""
    return await clear_build_cache_impl()


@router.post("/api/governance/ledger/reset", dependencies=[Depends(verify_token)])
async def reset_ledger() -> Dict[str, Any]:
    """🔄 [全域重置] 物理重置 SQLite 账本中的全部文档记录与哈希指纹"""
    return await reset_ledger_impl()


@router.post("/api/governance/reset-and-sync", dependencies=[Depends(verify_token)])
async def reset_ledger_and_sync() -> Dict[str, Any]:
    """🔄 [一键全量重译与发布] 清空段落缓存、重置文档指纹账本并强行触发全量 AI 翻译与出版"""
    return await reset_ledger_and_sync_impl()


@router.post("/api/governance/cache/migrate", dependencies=[Depends(verify_token)])
async def trigger_cache_migration(req: Dict[str, Any]) -> Dict[str, Any]:
    """🚚 [段落缓存治理] 手动触发物理迁移接口"""
    return await trigger_cache_migration_impl(req)
