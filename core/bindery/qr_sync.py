# -*- coding: utf-8 -*-
"""
📱 [V125.3] Bindery LAN QR Mobile Sync Engine
职责：探测活跃物理网卡局域网 IP，动态将出版物直链生成为高清二维码 Data URI，实现移动设备一键直传。
规范：遵循工业主权架构，单文件行数严格 ≤ 300 行。
"""

import io
import socket
import base64
from typing import Dict, Any, Optional
try:
    import qrcode
except ImportError:
    qrcode = None


def get_lan_ip() -> str:
    """获取本机真实的物理局域网 IP 地址 (优先排除点对点虚拟 VPN / 代理网卡)"""
    try:
        import subprocess, re
        out = subprocess.check_output(["ifconfig"], text=True, stderr=subprocess.DEVNULL)
        matches = re.findall(r"inet\s+(\d+\.\d+\.\d+\.\d+)\s+netmask\s+\S+\s+broadcast\s+(\d+\.\d+\.\d+\.\d+)", out)
        for ip, _ in matches:
            if ip.startswith("192.168.") or ip.startswith("10.") or (ip.startswith("172.") and not ip.startswith("172.18.")):
                return ip
        for ip, _ in matches:
            if not ip.startswith("127."):
                return ip
    except Exception:
        pass
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            if ip and not ip.startswith("127.") and not ip.startswith("172.18."):
                return ip
    except Exception:
        pass
    try:
        ip = socket.gethostbyname(socket.gethostname())
        if ip and not ip.startswith("127."):
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
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=8,
            border=2,
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
    token: Optional[str] = None
) -> Dict[str, Any]:
    """组装移动端扫码同步所需的目标 URL 与二维码载荷 (支持局域网直连或公网隧道)"""
    lan_ip = get_lan_ip()
    endpoint = "/api/bindery/view" if action == "view" and filename.endswith(".html") else "/api/bindery/download"
    if base_url:
        token_param = f"&token={token}" if token else ""
        target_url = f"{base_url.rstrip('/')}{endpoint}?file={filename}{token_param}"
        is_public = True
    else:
        target_url = f"http://{lan_ip}:{port}{endpoint}?file={filename}"
        is_public = False

    qr_data_uri = generate_qr_data_uri(target_url)
    fmt = "webbook" if filename.endswith(".html") else ("pdf" if filename.endswith(".pdf") else "epub")
    return {
        "success": True,
        "filename": filename,
        "format": fmt,
        "action": action,
        "lan_ip": lan_ip,
        "port": port,
        "url": target_url,
        "qr_data_uri": qr_data_uri,
        "has_qr_engine": bool(qr_data_uri),
        "is_public": is_public,
        "token": token,
        "expires_in": 1800 if token else None,
    }
