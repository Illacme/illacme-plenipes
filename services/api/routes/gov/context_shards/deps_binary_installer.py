# -*- coding: utf-8 -*-
"""
🛰️ [V126.0] Illacme Plenipes - Binary CLI Dependencies Installer
职责：独立承载跨平台单文件二进制工具 (如 cloudflared) 的环境探测、免密下载、解压落盘与权限自愈。
🛡️ [SOP-01 规范]：单文件代码行数严格 ≤ 300 行。
"""

import os
import io
import shutil
import tarfile
import platform
import subprocess
import urllib.request
from typing import List, Dict, Any, Tuple, Optional


def get_cloudflared_target_path() -> str:
    """获取产品专属二进制存放绝对路径"""
    bin_dir = os.path.expanduser("~/.plenipes/bin")
    is_win = platform.system() == "Windows"
    return os.path.join(bin_dir, "cloudflared.exe" if is_win else "cloudflared")


def resolve_cloudflared_package_name() -> Tuple[Optional[str], Optional[str]]:
    """
    根据当前系统的操作系统与 CPU 芯片架构解析对应的安装包文件名与提取格式
    :return: (package_filename, format_type) 例如 ("cloudflared-darwin-arm64.tgz", "tar.gz")
    """
    sys_name = platform.system()
    machine = platform.machine().lower()
    is_arm = "arm" in machine or "aarch64" in machine

    if sys_name == "Darwin":
        pkg = "cloudflared-darwin-arm64.tgz" if is_arm else "cloudflared-darwin-amd64.tgz"
        return pkg, "tgz"
    elif sys_name == "Linux":
        pkg = "cloudflared-linux-arm64" if is_arm else "cloudflared-linux-amd64"
        return pkg, "raw"
    elif sys_name == "Windows":
        return "cloudflared-windows-amd64.exe", "raw"
    return None, None


def download_binary_stream(urls: List[str], timeout: int = 30) -> Optional[bytes]:
    """尝试从多个镜像源依次流式下载文件内容 (支持 Failover 容灾)"""
    headers = {"User-Agent": "Mozilla/5.0 (IllacmePlenipes-CLI-Installer)"}
    for url in urls:
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as response:
                if response.status == 200:
                    return response.read()
        except Exception:
            continue
    return None


def install_cloudflared_binary(log_fn) -> Dict[str, Any]:
    """
    ⚡ 一键自动安装与部署 cloudflared 命令行组件
    :param log_fn: 日志记录回调函数 log(level, message)
    :return: {"success": bool, "logs": list}
    """
    logs: List[Dict[str, str]] = []

    def _log(level: str, msg: str):
        logs.append(log_fn(level, msg))

    _log("INFO", "🔍 [环境探测] 正在检查本地环境是否存在已就绪的 cloudflared 组件...")
    target_bin = get_cloudflared_target_path()

    # 1. 检查全局或产品本地是否已安装
    existing = shutil.which("cloudflared")
    if existing:
        _log("SUCCESS", f"🟢 [检测完成] 系统全局已存在 cloudflared 组件: {existing}")
        return {"success": True, "logs": logs}
    if os.path.exists(target_bin) and os.access(target_bin, os.X_OK):
        _log("SUCCESS", f"🟢 [检测完成] 本地产品沙盒已存在就绪的 cloudflared: {target_bin}")
        return {"success": True, "logs": logs}

    pkg_name, format_type = resolve_cloudflared_package_name()
    if not pkg_name:
        _log("ERROR", f"❌ 暂不支持当前操作系统架构: {platform.system()} ({platform.machine()})")
        return {"success": False, "logs": logs}

    sys_info = f"{platform.system()} ({platform.machine()})"
    _log("INFO", f"💻 [架构识别] 当前系统为 {sys_info}，对应组件包: {pkg_name}")

    # 2. 尝试使用 macOS 本地 Homebrew（若可用且快速）
    if platform.system() == "Darwin":
        brew_bin = shutil.which("brew")
        if brew_bin:
            _log("INFO", "🍺 [包管理器] 检测到本机安装了 Homebrew，尝试快速执行 brew install cloudflared...")
            try:
                proc = subprocess.run([brew_bin, "install", "cloudflared"], capture_output=True, text=True, timeout=120)
                if proc.returncode == 0:
                    installed = shutil.which("cloudflared") or target_bin
                    _log("SUCCESS", f"🟢 [Homebrew 成功] Cloudflare 穿透驱动已通过 Homebrew 安装就绪: {installed}")
                    return {"success": True, "logs": logs}
                else:
                    _log("WARN", f"⚠️ brew 安装未闭环 (转为使用官方单文件直接极速部署): {proc.stderr[:120] if proc.stderr else '跳过'}")
            except Exception as e:
                _log("WARN", f"⚠️ 调起 brew 进程超时或异常 (转为直接部署官方单文件): {e}")

    # 3. 从多源镜像直接下载官方单文件静态二进制并落盘至 ~/.plenipes/bin/
    urls = [
        f"https://github.com/cloudflare/cloudflared/releases/latest/download/{pkg_name}",
        f"https://ghproxy.net/https://github.com/cloudflare/cloudflared/releases/latest/download/{pkg_name}",
        f"https://mirror.ghproxy.com/https://github.com/cloudflare/cloudflared/releases/latest/download/{pkg_name}"
    ]

    _log("INFO", "🌐 [网络拉取] 正在从官方及加速源拉取静态组件 (约 15~35MB)...")
    content = download_binary_stream(urls, timeout=60)
    if not content:
        _log("ERROR", "❌ [下载失败] 连接官方 Releases 及加速镜像源均超时，请检查外网连接。")
        return {"success": False, "logs": logs}

    bin_dir = os.path.dirname(target_bin)
    os.makedirs(bin_dir, exist_ok=True)

    try:
        if format_type == "tgz":
            _log("INFO", "📦 [解包展开] 正在解压并提取 cloudflared 核心可执行文件...")
            with tarfile.open(fileobj=io.BytesIO(content), mode="r:gz") as tar:
                member = tar.extractfile("cloudflared")
                if not member:
                    _log("ERROR", "❌ 压缩包中未找到 cloudflared 目标二进制。")
                    return {"success": False, "logs": logs}
                with open(target_bin, "wb") as f:
                    shutil.copyfileobj(member, f)
        else:
            with open(target_bin, "wb") as f:
                f.write(content)

        # 赋予可执行权限
        os.chmod(target_bin, 0o755)
        _log("INFO", f"🔒 [安全授权] 已配置可执行权限并持久化至: {target_bin}")

        # 执行自检验证
        ver_proc = subprocess.run([target_bin, "--version"], capture_output=True, text=True, timeout=5)
        ver_output = (ver_proc.stdout or ver_proc.stderr or "").strip()
        _log("SUCCESS", f"🟢 [组件就绪] {ver_output or 'Cloudflare Tunnel 命令行客户端物理装配成功！'}")
        return {"success": True, "logs": logs}
    except Exception as e:
        _log("ERROR", f"❌ 写入或解压组件异常: {e}")
        return {"success": False, "logs": logs}
