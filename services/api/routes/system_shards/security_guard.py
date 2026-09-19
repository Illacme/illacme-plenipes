# -*- coding: utf-8 -*-
"""
🛡️ [V74.8] System Security Guard Shard
职责：多维校验 API 访问令牌与物理来源，守护主权网关安全边界。
"""

from typing import Optional
from fastapi import Header, HTTPException, Request


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


def verify_token(request: Request = None, x_token: Optional[str] = Header(None, alias="X-Token")) -> None:
    """
    🛡️ 主权网关安全守卫：多维校验 API 访问令牌与物理来源。
    - 若配置了 system.api_token，则无论来源必须匹配合法令牌；
    - 若未配置 system.api_token：
      - 本地回环 (127.0.0.1 / ::1 / localhost / testclient) 免密放行，确保单人本地出版体验零摩擦；
      - 跨网络/局域网/公网访问或开启 strict_security 时，强制阻断并要求配置安全令牌。
    """
    engine = _get_engine()
    sys_cfg = getattr(engine.config, "system", None) if (engine and getattr(engine, "config", None)) else None
    api_token = getattr(sys_cfg, "api_token", None) if sys_cfg else None
    strict_sec = getattr(sys_cfg, "strict_security", False) if sys_cfg else False

    # 1. 显式配置了 api_token 的情况
    if api_token:
        # 兼容 Header X-Token 或 URL query param ?token=...
        query_token = request.query_params.get("token") if request else None
        incoming_token = x_token or query_token
        if incoming_token != api_token:
            from core.utils.event_bus import bus
            client_host = request.client.host if (request and request.client) else "未知"
            bus.emit("SECURITY_ALERT", category="API_TOKEN_INVALID", message=f"接口认证失败：来自 {client_host} 的越权访问已被物理拦截。")
            raise HTTPException(status_code=401, detail="Unauthorized: Invalid or missing API token")
        return

    # 2. 未配置 api_token 时：执行来源主机安全防护
    client_host = request.client.host if (request and request.client) else ""
    is_localhost = client_host in ("127.0.0.1", "::1", "localhost", "testclient")
    
    # 若开启严格安全模式，或者来自非本地回环地址
    if strict_sec or not is_localhost:
        from core.utils.event_bus import bus
        bus.emit("SECURITY_ALERT", category="NON_LOCALHOST_BLOCKED", message=f"跨网访问拦截：检测到非回环地址 {client_host} 尝试在未配置 API Token 的情况下访问主权网关。")
        raise HTTPException(
            status_code=401,
            detail=f"Unauthorized: Access from non-localhost IP ({client_host}) requires system.api_token to be configured."
        )
