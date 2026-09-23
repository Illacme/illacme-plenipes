# -*- coding: utf-8 -*-
"""
⚡ [V125.4] Bindery Tunnel & Mobile Sync Routes
职责：暴露零配置公网隧道启动、停止、状态查询及局域网/公网扫码载荷生成接口。
规范：遵循工业主权架构，单文件行数严格 ≤ 300 行。
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Query, Depends, HTTPException, Request

from core.bindery.tunnel import get_tunnel_hub
from core.bindery.qr_sync import build_mobile_sync_payload
from services.api.routes.system import verify_token

router = APIRouter(tags=["bindery_tunnel"])


def _check_safe_book(file: str) -> None:
    """防路径穿越安全校验"""
    import os
    safe_name = os.path.basename(file.strip())
    if not safe_name or safe_name != file:
        raise HTTPException(status_code=400, detail="非法的请求参数。")


@router.get("/api/bindery/qr")
async def get_publication_qr_code(
    file: str = Query(..., description="文件名"),
    action: str = Query("download", description="download 或 view")
) -> Dict[str, Any]:
    """获取移动端局域网直连二维码载荷"""
    _check_safe_book(file)
    return build_mobile_sync_payload(file, action=action)


@router.get("/api/bindery/tunnel/status")
async def get_tunnel_status() -> Dict[str, Any]:
    """查询当前临时公网隧道的存活状态与分配的公网 URL"""
    hub = get_tunnel_hub()
    status = hub.get_status()
    return {"success": True, **status}


@router.post("/api/bindery/tunnel/start", dependencies=[Depends(verify_token)])
async def start_tunnel(request: Request) -> Dict[str, Any]:
    """一键唤醒零配置临时公网隧道 (优先 Cloudflare，备选 Native SSH)"""
    hub = get_tunnel_hub()
    status = hub.start_tunnel(port=43212)
    if not status.get("is_running"):
        raise HTTPException(
            status_code=500,
            detail=status.get("error") or "无法启动临时公网隧道，请检查网络连接。"
        )
    return {"success": True, **status}


@router.post("/api/bindery/tunnel/stop", dependencies=[Depends(verify_token)])
async def stop_tunnel() -> Dict[str, Any]:
    """注销并切断临时公网隧道，安全收缩回局域网保护模式"""
    hub = get_tunnel_hub()
    res = hub.stop_tunnel()
    return {"success": True, **res}


@router.get("/api/bindery/qr/public")
async def get_public_qr_code(
    file: str = Query(..., description="目标文件名"),
    action: str = Query("download", description="download 或 view")
) -> Dict[str, Any]:
    """获取移动端公网直连扫码载荷与 30 分钟限时防越权安全令牌"""
    _check_safe_book(file)
    hub = get_tunnel_hub()
    status = hub.get_status()
    if not status.get("is_running") or not status.get("public_url"):
        raise HTTPException(status_code=400, detail="临时公网隧道未启动，请先开启公网通道。")

    token = hub.issue_token(file, ttl_seconds=1800)
    payload = build_mobile_sync_payload(
        filename=file,
        port=43212,
        action=action,
        base_url=status["public_url"],
        token=token
    )
    return payload
