# -*- coding: utf-8 -*-
"""
🛡️ [V74.55] Gov Imprints Shard: Switch Operations
职责：承载出版品牌热切换、同步锁保护与引擎深度重载。
"""


def _get_engine():
    """获取全局引擎实例，优先兼容外部对主模块的动态 patch / mock"""
    try:
        import services.api.routes.gov.imprints as parent_mod
        if hasattr(parent_mod, "get_global_engine"):
            return parent_mod.get_global_engine()
    except Exception:
        pass
    from core.runtime.engine_singleton import get_global_engine
    return get_global_engine()


async def switch_imprint_logic(req: dict) -> dict:
    """🚀 热切换当前出版品牌并触发深度重载"""
    from core.governance.imprint_manager import im
    from core.runtime.cli_bootstrap import deep_reload_imprint
    
    # 🛡️ [Sync Lock] 检查当前是否在进行全域同步
    engine = _get_engine()
    if engine and getattr(engine, "is_syncing", False):
        return {"success": False, "error": "🛑 品牌当前正处于【全域同步】状态，为了防止数据账本损坏和输出路径污染，已拦截切换品牌操作。请等待当前同步任务完成后再试。"}

    imprint_id = req.get("imprint_id")
    if not imprint_id:
        return {"error": "Missing imprint_id"}
    
    try:
        success = deep_reload_imprint(imprint_id)
    except (ValueError, SystemExit) as e:
        msg = str(e)
        if not msg or msg == "1":
            msg = f"品牌 [{imprint_id}] 预检或路径校验未通过"
        return {"success": False, "error": f"品牌预检未通过: {msg}"}
    except Exception as e:
        return {"success": False, "error": f"引擎深度重载异常: {e}"}

    if success:
        im.switch(imprint_id)
        if engine and hasattr(engine, "ledger") and engine.ledger:
            engine.ledger.log(
                event_type="PUBLISH_LAYOUT_CHANGED",
                details=f"切换当前出版品牌至: {imprint_id}",
                severity="INFO",
                actor="APIAdmin",
                metadata={"imprint_id": imprint_id}
            )
        return {"success": True, "active": imprint_id}
    else:
        return {"success": False, "error": "引擎深度重载失败，请检查终端日志。"}
