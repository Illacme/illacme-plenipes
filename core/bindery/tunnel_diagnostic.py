# -*- coding: utf-8 -*-
"""
⚡ [V126.0] Bindery Tunnel & Network Diagnostic Probe Engine
职责：负责局域网物理网卡多候选探针、公网隧道回环主动健康检测、异常特征识别与一键链路自愈推荐。
规范：遵循工业主权架构，单文件行数严格 ≤ 300 行。
"""

import time
import socket
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional
from core.utils.tracing import tlog


def get_lan_candidates() -> List[Dict[str, Any]]:
    """探测本机所有非回环的候选局域网 IP 地址及其接口特征 (强力隔离虚拟代理/VPN/容器网卡)"""
    candidates = []
    seen_ips = set()

    # 1. 状态机解析 ifconfig 网卡段落 (兼容 macOS 与 Linux 的顶格网卡名与缩进行格式)
    try:
        import subprocess
        import re
        out = subprocess.check_output(["ifconfig"], text=True, stderr=subprocess.DEVNULL)
        cur_iface = None
        ifaces: Dict[str, List[str]] = {}
        for line in out.splitlines():
            m_iface = re.match(r"^([a-zA-Z0-9_]+):", line)
            if m_iface:
                cur_iface = m_iface.group(1)
                ifaces[cur_iface] = []
            elif cur_iface:
                ifaces[cur_iface].append(line)

        for iface, lines in ifaces.items():
            block_txt = "\n".join(lines)
            ip_m = re.search(r"inet\s+(\d+\.\d+\.\d+\.\d+)", block_txt)
            if not ip_m:
                continue
            ip = ip_m.group(1)
            if ip.startswith("127.") or ip in seen_ips:
                continue
            seen_ips.add(ip)

            has_bcast = "broadcast" in block_txt
            is_ptp = "POINTOPOINT" in block_txt or "-->" in block_txt or iface.startswith("utun") or iface.startswith("tun")
            is_wifi_eth = iface.startswith("en") or iface.startswith("eth") or iface.startswith("wl")
            is_virtual = (
                ip.startswith("172.17.") or ip.startswith("172.18.") or
                ip.startswith("198.18.") or is_ptp or "docker" in iface or "bridge" in iface
            )

            # 优先级分级打分：物理带广播的 Wi-Fi/以太网 (10) > 一般局域网 (6) > 虚拟代理 (1)
            if has_bcast and is_wifi_eth and not is_virtual:
                priority = 10 if (ip.startswith("192.168.") or ip.startswith("10.")) else 8
                desc = f"物理无线/有线网卡 ({iface})"
            elif has_bcast and not is_virtual:
                priority = 6
                desc = f"局域网接口 ({iface})"
            else:
                priority = 1
                desc = f"虚拟/代理/容器网卡 ({iface})"

            candidates.append({
                "ip": ip,
                "interface": iface,
                "desc": desc,
                "is_preferred": False,
                "priority": priority
            })
    except Exception:
        pass

    # 2. 备用 socket 默认路由探测 (防穿透虚拟代理保护)
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            def_ip = s.getsockname()[0]
            if def_ip and not def_ip.startswith("127.") and def_ip not in seen_ips:
                seen_ips.add(def_ip)
                is_virt = def_ip.startswith("172.17.") or def_ip.startswith("172.18.") or def_ip.startswith("198.18.")
                candidates.append({
                    "ip": def_ip,
                    "interface": "default",
                    "desc": "系统默认路由网卡" if not is_virt else "默认代理出口网卡",
                    "is_preferred": False,
                    "priority": 7 if not is_virt else 2
                })
    except Exception:
        pass

    # 3. 排序并标记首选 (物理 Wi-Fi / 以太网优先)
    candidates.sort(key=lambda x: x["priority"], reverse=True)
    if candidates:
        candidates[0]["is_preferred"] = True
    else:
        candidates.append({
            "ip": "127.0.0.1",
            "interface": "lo0",
            "desc": "本机回环 (仅本机可达)",
            "is_preferred": True,
            "priority": 0
        })
    return candidates



def probe_lan_health(target_ip: Optional[str] = None, port: int = 43212) -> Dict[str, Any]:
    """探测局域网节点健康状态与多网卡环境"""
    candidates = get_lan_candidates()
    active_ip = target_ip or (candidates[0]["ip"] if candidates else "127.0.0.1")

    # 本机本地端口连通性检查
    port_open = False
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.6)
            res = s.connect_ex(("127.0.0.1", port))
            port_open = (res == 0)
    except Exception:
        port_open = False

    tips = []
    if not port_open:
        tips.append(f"⚠️ 本机服务端口 {port} 未就绪，请确认系统已启动。")
    if len(candidates) > 1:
        tips.append("💡 本机检测到多个网络接口（如同时连接了有线/无线或虚拟网卡），若手机打不开可尝试切换下方候选 IP。")
    tips.append("📶 手机必须连接至同一 Wi-Fi。若路由器开启了【AP 隔离/访客模式】或系统开启了防火墙，请先允许入站连接。")

    return {
        "success": True,
        "active_ip": active_ip,
        "port": port,
        "port_open": port_open,
        "candidates": candidates,
        "tips": tips
    }


def probe_public_tunnel(public_url: str, timeout_seconds: float = 3.5) -> Dict[str, Any]:
    """主动向分配的公网 URL 发送回环探针，测量 RTT 延时并识别故障特征"""
    if not public_url:
        return {
            "healthy": False,
            "rtt_ms": None,
            "status_code": None,
            "error_code": "NO_URL",
            "message": "公网隧道尚未分配有效域名"
        }

    probe_url = f"{public_url.rstrip('/')}/api/bindery/tunnel/status"
    req = urllib.request.Request(
        probe_url,
        headers={"User-Agent": "Illacme-Diagnostic-Probe/1.0", "Accept": "application/json"}
    )

    t0 = time.time()
    try:
        # 针对自签名证书或临时域名宽容验证
        import ssl
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        with urllib.request.urlopen(req, timeout=timeout_seconds, context=ctx) as resp:
            rtt_ms = int((time.time() - t0) * 1000)
            status_code = resp.getcode()
            body_sample = resp.read(2048).decode("utf-8", errors="ignore")

            if "no tunnel here" in body_sample.lower():
                return {"healthy": False, "rtt_ms": rtt_ms, "status_code": 502, "error_code": "NO_TUNNEL_AT_HOST", "message": "远端中继服务尚未成功映射到本地端口 (no tunnel here)"}
            if "wasn't found" in body_sample.lower() or status_code == 404:
                return {"healthy": False, "rtt_ms": rtt_ms, "status_code": 404, "error_code": "FOREIGN_HOST", "message": "公网域名未命中本机服务 (访问到了非目标主机)"}
            if status_code == 200:
                return {"healthy": True, "rtt_ms": rtt_ms, "status_code": 200, "error_code": None, "message": f"公网通道通畅，响应时延 {rtt_ms}ms"}
            return {"healthy": False, "rtt_ms": rtt_ms, "status_code": status_code, "error_code": f"HTTP_{status_code}", "message": f"远端返回异常 HTTP 状态码: {status_code}"}
    except urllib.error.HTTPError as e:
        rtt_ms = int((time.time() - t0) * 1000)
        body = ""
        try:
            body = e.read(1024).decode("utf-8", errors="ignore")
        except Exception:
            pass
        if "no tunnel here" in body.lower():
            return {"healthy": False, "rtt_ms": rtt_ms, "status_code": e.code, "error_code": "NO_TUNNEL_AT_HOST", "message": "远端中继服务尚未成功映射到本地端口 (no tunnel here)"}
        if e.code in [400, 401, 403]:
            return {"healthy": True, "rtt_ms": rtt_ms, "status_code": e.code, "error_code": None, "message": f"公网通道已建立，状态码 {e.code}"}
        return {"healthy": False, "rtt_ms": rtt_ms, "status_code": e.code, "error_code": f"HTTP_{e.code}", "message": f"公网中继端响应错误 HTTP {e.code}"}
    except urllib.error.URLError as e:
        rtt_ms = int((time.time() - t0) * 1000)
        err_str = str(e.reason).lower()
        err_code = "TIMEOUT" if "timed out" in err_str else ("REFUSED" if "connection refused" in err_str else ("DNS_FAIL" if "name" in err_str or "nodename" in err_str else "NETWORK_ERROR"))
        msg = "公网请求超时" if err_code == "TIMEOUT" else ("远端拒绝连接" if err_code == "REFUSED" else ("动态域名尚未解析完成" if err_code == "DNS_FAIL" else f"网络连接失败: {e.reason}"))
        return {"healthy": False, "rtt_ms": rtt_ms, "status_code": None, "error_code": err_code, "message": msg}
    except Exception as e:
        return {"healthy": False, "rtt_ms": None, "status_code": None, "error_code": "UNKNOWN", "message": f"探针探测异常: {str(e)}"}


def auto_heal_public_tunnel(hub, current_driver: Optional[str] = None, port: int = 43212) -> Dict[str, Any]:
    """链路自愈中枢：探测当前隧道，若失效自动轮转并调度最快最健康的备选可用隧道"""
    status = hub.get_status(verify_alive=False)
    cur_running = status.get("is_running")
    cur_url = status.get("public_url")
    cur_provider = status.get("provider") or current_driver

    # 先探测当前通道
    if cur_running and cur_url:
        probe = probe_public_tunnel(cur_url, timeout_seconds=2.5)
        if probe.get("healthy"):
            return {
                "success": True,
                "healed": False,
                "driver": cur_provider,
                "public_url": cur_url,
                "probe": probe,
                "message": f"当前通道 [{cur_provider}] 处于极佳健康状态，无需自愈切换。"
            }

    # 当前不可用或未运行，寻找候选备用驱动
    available = hub.list_available_drivers(only_enabled=True)
    driver_ids = [d["id"] for d in available]
    # 优先挑选不同于当前失败通道的驱动
    alternatives = [d_id for d_id in driver_ids if d_id != cur_provider]
    if not alternatives and driver_ids:
        alternatives = driver_ids

    tried_log = []
    for cand in alternatives:
        tlog.info(f"🔄 [链路自愈] 尝试切换至备用公网隧道: {cand}")
        hub.stop_tunnel()
        st = hub.start_tunnel(port=port, timeout_seconds=12, driver=cand)
        if st.get("is_running") and st.get("public_url"):
            # 立即进行回环健康探针
            cand_probe = probe_public_tunnel(st["public_url"], timeout_seconds=3.0)
            if cand_probe.get("healthy"):
                tlog.info(f"✨ [链路自愈成功] 已自动自愈并切换至稳定通道: {cand} (RTT: {cand_probe['rtt_ms']}ms)")
                return {
                    "success": True,
                    "healed": True,
                    "driver": cand,
                    "provider_name": st.get("provider_name") or cand.upper(),
                    "public_url": st["public_url"],
                    "probe": cand_probe,
                    "message": f"已自动自愈并无缝切换至高可用通道 [{cand}]。"
                }
            tried_log.append(f"{cand} (通道就绪但回环探针未通: {cand_probe['message']})")
        else:
            tried_log.append(f"{cand} (启动失败: {st.get('error', '未知错误')})")

    return {
        "success": False,
        "healed": False,
        "driver": cur_provider,
        "public_url": cur_url,
        "message": f"所有备用公网通道均未能通过探针检测: {'; '.join(tried_log)}。建议切换至局域网直传模式。"
    }
