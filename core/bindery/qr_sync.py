# -*- coding: utf-8 -*-
"""
📱 [V125.3] Bindery LAN QR Mobile Sync Engine
职责：探测活跃物理网卡局域网 IP，动态将出版物直链生成为高清二维码 Data URI，实现移动设备一键直传。
规范：遵循工业主权架构，单文件行数严格 ≤ 300 行。
"""

import io
import socket
import base64
from typing import Dict, Any
try:
    import qrcode
except ImportError:
    qrcode = None


def get_lan_ip() -> str:
    """通过探测出站路由网关获取本机真实的物理局域网 IP 地址"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            if ip and not ip.startswith("127."):
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


def build_mobile_sync_payload(filename: str, port: int = 43212, action: str = "download") -> Dict[str, Any]:
    """组装移动端扫码同步所需的目标 URL 与二维码载荷"""
    lan_ip = get_lan_ip()
    endpoint = "/api/bindery/view" if action == "view" and filename.endswith(".html") else "/api/bindery/download"
    target_url = f"http://{lan_ip}:{port}{endpoint}?file={filename}"
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
    }
