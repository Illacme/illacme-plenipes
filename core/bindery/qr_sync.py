# -*- coding: utf-8 -*-
"""
📱 [V125.3] Bindery LAN QR Mobile Sync Engine
职责：探测活跃物理网卡局域网 IP，动态将出版物直链生成为高清二维码 Data URI，实现移动设备一键直传。
规范：遵循工业主权架构，单文件行数严格 ≤ 300 行。
"""

import io
import socket
import base64
import urllib.parse
from typing import Dict, Any, Optional
try:
    import qrcode
except ImportError:
    qrcode = None


def get_lan_ip() -> str:
    """获取本机真实的物理局域网 IP 地址 (优先排除点对点虚拟 VPN / 代理网卡)"""
    try:
        from core.bindery.tunnel_diagnostic import get_lan_candidates
        cands = get_lan_candidates()
        if cands and cands[0]["ip"] and not cands[0]["ip"].startswith("127."):
            return cands[0]["ip"]
    except Exception:
        pass
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            if ip and not ip.startswith("127.") and not ip.startswith("172.18.") and not ip.startswith("198.18."):
                return ip
    except Exception:
        pass
    return "127.0.0.1"


def generate_qr_data_uri(content: str) -> str:
    """将文本或 URL 编码为黑白高对比度二维码 PNG 的 Base64 Data URI (支持零依赖平稳降级)"""
    if qrcode is None:
        return ""
    try:
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=8,
            border=4,
        )
        qr.add_data(content)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        buf = io.BytesIO()
        img.save(buf)
        b64_data = base64.b64encode(buf.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{b64_data}"
    except Exception:
        return ""


def build_mobile_sync_payload(
    filename: str,
    port: int = 43212,
    action: str = "download",
    base_url: Optional[str] = None,
    token: Optional[str] = None,
    custom_ip: Optional[str] = None
) -> Dict[str, Any]:
    """组装移动端扫码同步所需的目标 URL 与二维码载荷 (支持局域网直连或公网隧道)"""
    from core.bindery.tunnel_diagnostic import get_lan_candidates
    candidates = get_lan_candidates()
    lan_ip = custom_ip.strip() if custom_ip and custom_ip.strip() else (candidates[0]["ip"] if candidates else get_lan_ip())

    is_html = filename.endswith(".html")
    is_viewable = filename.endswith((".html", ".epub", ".pdf"))
    if is_html and action != "force_download":
        act_type = "view"
    elif action == "view" and is_viewable:
        act_type = "view"
    else:
        act_type = "download"

    endpoint = f"/api/bindery/{act_type}"
    enc_file = urllib.parse.quote(filename)
    if base_url:
        token_enc = urllib.parse.quote(token) if token else ""
        if token_enc:
            # 🛡️ 纯路径双保险路由：即便中间防钓鱼/重定向页截断丢弃了 ?query 参数，Path 仍 100% 完好
            target_url = f"{base_url.rstrip('/')}{endpoint}/{token_enc}/{enc_file}?file={enc_file}&token={token_enc}"
        else:
            target_url = f"{base_url.rstrip('/')}{endpoint}?file={enc_file}"
        is_public = True
    else:
        target_url = f"http://{lan_ip}:{port}{endpoint}?file={enc_file}"
        is_public = False

    qr_data_uri = generate_qr_data_uri(target_url)
    fmt = "webbook" if filename.endswith(".html") else ("pdf" if filename.endswith(".pdf") else "epub")
    return {
        "success": True,
        "filename": filename,
        "format": fmt,
        "action": act_type,
        "lan_ip": lan_ip,
        "lan_candidates": candidates,
        "port": port,
        "url": target_url,
        "qr_data_uri": qr_data_uri,
        "has_qr_engine": bool(qr_data_uri),
        "is_public": is_public,
        "token": token,
        "expires_in": 1800 if token else None,
    }

