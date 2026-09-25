# -*- coding: utf-8 -*-
"""
⚡ [V125.4] Bindery Tunnel & Mobile Sync Routes
职责：暴露零配置公网隧道启动、停止、状态查询及局域网/公网扫码载荷生成接口。
规范：遵循工业主权架构，单文件行数严格 ≤ 300 行。
"""

import asyncio
from typing import Dict, Any, Optional
from fastapi import APIRouter, Query, Depends, HTTPException, Request

from pydantic import BaseModel
from core.bindery.tunnel import get_tunnel_hub
from core.bindery.qr_sync import build_mobile_sync_payload
from services.api.routes.system import verify_token

from core.bindery.tunnel_diagnostic import probe_lan_health, probe_public_tunnel, auto_heal_public_tunnel

router = APIRouter(tags=["bindery_tunnel"])


class TunnelStartPayload(BaseModel):
    driver: Optional[str] = None


def _check_safe_book(file: str) -> None:
    """防路径穿越安全校验"""
    import os
    safe_name = os.path.basename(file.strip())
    if not safe_name or safe_name != file:
        raise HTTPException(status_code=400, detail="非法的请求参数。")


@router.get("/api/bindery/qr")
async def get_publication_qr_code(
    file: str = Query(..., description="文件名"),
    action: str = Query("download", description="download 或 view"),
    ip: Optional[str] = Query(None, description="指定候选局域网 IP")
) -> Dict[str, Any]:
    """获取移动端局域网直连二维码载荷 (支持多网卡候选 IP 切换)"""
    _check_safe_book(file)
    return build_mobile_sync_payload(file, action=action, custom_ip=ip)


@router.get("/api/bindery/tunnel/drivers")
async def get_tunnel_drivers() -> Dict[str, Any]:
    """获取当前品牌下已启用的临时公网穿透驱动列表"""
    hub = get_tunnel_hub()
    drivers = hub.list_available_drivers(only_enabled=True)
    cur_status = hub.get_status()
    active_driver = cur_status.get("provider") or next((d["id"] for d in drivers if d.get("is_preferred")), (drivers[0]["id"] if drivers else "localhost_run"))
    return {
        "success": True,
        "drivers": drivers,
        "active_driver": active_driver
    }


@router.get("/api/bindery/tunnel/status")
async def get_tunnel_status(refresh: bool = Query(False, description="是否强制执行活性验证")) -> Dict[str, Any]:
    """查询当前临时公网隧道的存活状态与分配的公网 URL"""
    hub = get_tunnel_hub()
    status = hub.get_status(verify_alive=refresh)
    return {"success": True, **status}


@router.post("/api/bindery/tunnel/start", dependencies=[Depends(verify_token)])
async def start_tunnel(request: Request, payload: Optional[TunnelStartPayload] = None) -> Dict[str, Any]:
    """一键唤醒零配置临时公网隧道 (支持指定驱动)"""
    driver = None
    if payload and payload.driver:
        driver = payload.driver.strip().lower()
    else:
        try:
            body = await request.json()
            if isinstance(body, dict) and body.get("driver"):
                driver = str(body["driver"]).strip().lower()
        except Exception:
            pass

    hub = get_tunnel_hub()
    status = await asyncio.to_thread(hub.start_tunnel, 43212, 15, driver)
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
    res = await asyncio.to_thread(hub.stop_tunnel)
    return {"success": True, **res}


@router.get("/api/bindery/qr/public")
async def get_public_qr_code(
    file: str = Query(..., description="目标文件名"),
    action: str = Query("download", description="download 或 view")
) -> Dict[str, Any]:
    """获取移动端公网直连扫码载荷与 30 分钟限时防越权安全令牌 (带活性自愈保护)"""
    _check_safe_book(file)
    hub = get_tunnel_hub()
    status = hub.get_status(verify_alive=False)
    if not status.get("is_running") or not status.get("public_url"):
        raise HTTPException(status_code=400, detail="临时公网隧道未启动或已失效，请重新开启公网通道。")

    token = hub.issue_token(file, ttl_seconds=1800)
    payload = build_mobile_sync_payload(
        filename=file,
        port=43212,
        action=action,
        base_url=status["public_url"],
        token=token
    )
    return payload


@router.get("/api/bindery/probe/lan")
async def probe_lan_interface(ip: Optional[str] = Query(None, description="待检测的目标局域网 IP")) -> Dict[str, Any]:
    """探测本机局域网多网卡环境、端口可用性与网络自检诊断报告"""
    return await asyncio.to_thread(probe_lan_health, target_ip=ip, port=43212)


@router.get("/api/bindery/tunnel/probe")
async def probe_tunnel_health_route() -> Dict[str, Any]:
    """主动向当前激活的公网 URL 发送回环探针，探测 RTT 延时并识别故障状态"""
    hub = get_tunnel_hub()
    status = hub.get_status(verify_alive=False)
    if not status.get("is_running") or not status.get("public_url"):
        return {
            "success": False,
            "healthy": False,
            "message": "公网隧道未启动"
        }
    probe_res = await asyncio.to_thread(probe_public_tunnel, status["public_url"], 3.5)
    return {
        "success": True,
        "provider": status.get("provider"),
        "provider_name": status.get("provider_name"),
        "public_url": status["public_url"],
        **probe_res
    }


@router.post("/api/bindery/tunnel/auto-heal", dependencies=[Depends(verify_token)])
async def auto_heal_tunnel_route() -> Dict[str, Any]:
    """一键触发链路自愈：检测当前通道并在异常时无缝调度切换至最优备选公网隧道"""
    hub = get_tunnel_hub()
    heal_res = await asyncio.to_thread(auto_heal_public_tunnel, hub, None, 43212)
    return heal_res


@router.get("/api/bindery/download/{token}/{file:path}")
async def download_ebook_by_pure_path(token: str, file: str):
    """纯路径公网下载端点 (彻底免疫防钓鱼页面丢弃 Query 参数的情况)"""
    import os
    from fastapi.responses import FileResponse
    _check_safe_book(file)
    hub = get_tunnel_hub()
    if not hub.verify_token(file, token):
        raise HTTPException(status_code=403, detail="安全访问凭据已失效或已过期。")
    base_dir = os.path.abspath("dist/books")
    target_path = os.path.abspath(os.path.join(base_dir, file))
    if not target_path.startswith(base_dir + os.sep) or not os.path.isfile(target_path):
        raise HTTPException(status_code=404, detail="请求的出版物文件未找到或已被清理。")
    ext = os.path.splitext(file)[1].lower()
    media_map = {".epub": "application/epub+zip", ".html": "text/html", ".pdf": "application/pdf"}
    return FileResponse(path=target_path, media_type=media_map.get(ext, "application/octet-stream"), filename=file)


@router.get("/api/bindery/view/{token}/{file:path}")
async def view_ebook_by_pure_path(token: str, file: str):
    """纯路径公网在线阅读端点 (彻底免疫防钓鱼页面丢弃 Query 参数的情况)"""
    import os
    from fastapi.responses import Response, FileResponse
    _check_safe_book(file)
    hub = get_tunnel_hub()
    if not hub.verify_token(file, token):
        raise HTTPException(status_code=403, detail="安全访问凭据已失效或已过期。")
    base_dir = os.path.abspath("dist/books")
    target_path = os.path.abspath(os.path.join(base_dir, file))
    if not target_path.startswith(base_dir + os.sep) or not os.path.isfile(target_path):
        raise HTTPException(status_code=404, detail="请求的出版物文件未找到或已被清理。")

    ext = os.path.splitext(file)[1].lower()
    if ext == ".html":
        with open(target_path, "r", encoding="utf-8") as f:
            return Response(content=f.read(), media_type="text/html; charset=utf-8", headers={"Cache-Control": "no-cache, no-store", "Pragma": "no-cache"})
    if ext == ".pdf":
        return FileResponse(path=target_path, media_type="application/pdf", filename=file, content_disposition_type="inline", headers={"Cache-Control": "no-cache, no-store"})
    if ext == ".epub":
        from core.adapters.egress.ebook.epub_reader import render_epub_reader_html
        try:
            return Response(content=render_epub_reader_html(target_path), media_type="text/html; charset=utf-8", headers={"Cache-Control": "no-cache, no-store", "Pragma": "no-cache"})
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"EPUB 电子书解析失败: {e}")
    raise HTTPException(status_code=400, detail="仅支持 WebBook (HTML)、PDF 或 EPUB 格式在线翻阅。")


