# -*- coding: utf-8 -*-
"""
🚀 [V74.8] System Sync & Watchdog Operations Shard
职责：提供全域发布同步点火、两段式毫秒级预检、流水线状态感知与监控狗挂起恢复。
"""

from typing import Dict, Any
from fastapi import HTTPException
from core.utils.tracing import tlog
from services.api.logic import sys_ops


def _get_engine():
    """获取全局引擎实例，优先兼容外部对主模块的动态 patch / mock"""
    try:
        import services.api.routes.system as parent_mod
        if hasattr(parent_mod, "get_global_engine"):
            return parent_mod.get_global_engine()
    except Exception:
        pass
    from core.runtime.engine_singleton import get_global_engine
    return get_global_engine()


async def precheck_sync_logic() -> Dict[str, Any]:
    """🚀 [V78.5] 毫秒级双段式预检接口：用于提供给 UI 拦截"""
    engine = _get_engine()
    if not engine:
        raise HTTPException(status_code=503, detail="Engine not ready")
    return sys_ops.run_precheck_logic(engine)


async def suspend_watchdog_logic() -> Dict[str, str]:
    """🚀 [V78.6] 挂起监控狗：阻止自动同步触发 (UI 独占模式)"""
    engine = _get_engine()
    if engine:
        engine.is_watchdog_suspended = True
        tlog.info("🤫 [UI] 已发出静默指令：监控狗进入休眠状态。")
    return {"status": "suspended"}


async def resume_watchdog_logic() -> Dict[str, str]:
    """🚀 [V78.6] 唤醒监控狗：恢复自动同步"""
    engine = _get_engine()
    if engine:
        engine.is_watchdog_suspended = False
        tlog.info("🐕 [UI] 已发出唤醒指令：监控狗重新开始巡视。")
    return {"status": "resumed"}


async def trigger_sync_logic(dry_run: bool = False, force: bool = False, sandbox: bool = False, local_only: bool = False, clear_cache: bool = False) -> Dict[str, Any]:
    """🚀 [V51.0] 全球同步点火接口：驱动编排中枢执行全量同步 / 发布预览"""
    engine = _get_engine()
    if not engine:
        raise HTTPException(status_code=503, detail="Engine not ready")
    
    # 🛡️ [V76.8] 翻译矩阵与算力可用性强关联校验熔断门禁 (同步拦截)
    try:
        from core.governance.checks.ai import check_ai_availability_or_raise
        check_ai_availability_or_raise(engine)
    except RuntimeError as e:
        return {"status": "error", "reason": str(e)}

    from core.runtime.orchestrator import start_asynchronous_sync
    future_id = start_asynchronous_sync(engine, dry_run=dry_run, force=force, sandbox=sandbox, local_only=local_only, clear_cache=clear_cache)

    if future_id is None or future_id == 0:
        return {"status": "rejected", "reason": "Already publishing"}
    
    return {
        "status": "started",
        "future_id": future_id,
        "mode": "asynchronous",
        "local_only": local_only
    }


def get_sync_status_logic() -> Dict[str, Any]:
    """🚀 [V78.8] 查询当前出版流水线是否在运行"""
    from core.runtime.orchestrator import _is_publishing
    return {"is_publishing": _is_publishing}


async def abort_sync_logic() -> Dict[str, Any]:
    """🛑 [V79.0] 中止全量同步接口"""
    engine = _get_engine()
    if not engine:
        return {"status": "error", "reason": "Engine not ready"}
    
    # 开启中止信号
    engine.abort_sync = True

    # 清空后台排队队列
    try:
        from core.runtime.orchestrator import _pending_sync_queue
        _pending_sync_queue.clear()
    except Exception:
        pass
    
    # 清空并发执行池中挂起的工作
    from core.logic.orchestration.task_orchestrator import global_executor, ai_executor, asset_executor
    global_executor.cancel_all_pending()
    ai_executor.cancel_all_pending()
    asset_executor.cancel_all_pending()
    
    tlog.warning("🛑 [UI] 已接收到停止同步指令，已向执行器广播中止信号并清空待处理队列。")
    return {"status": "aborted"}
