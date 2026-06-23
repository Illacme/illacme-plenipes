# -*- coding: utf-8 -*-
"""
🛡️ [V74.9] Gov Plugin Ops Dependencies Installer Shard
职责：独立承载插件外部依赖包的一键自动安装、环境感应自适应与多镜像源 Failover 自愈逻辑。
符合 SOP-02 物理拆分协议与 300 行复杂度红线。
"""

import os
import sys
import subprocess
import datetime

async def install_plugin_deps_impl(payload: dict) -> dict:
    """
    🔌 一键依赖安装与自愈接口
    实现功能：虚拟环境感应、非虚拟环境 --user 隔离自适应、PEP 668 环境自愈、多 PyPI 源 Failover。
    """
    plugin_id = payload.get("id")
    if not plugin_id:
        return {"success": False, "error": "Plugin ID is required"}

    dependencies = {
        "aliyun_oss": ["oss2"],
        "tencent_cos": ["cos-python-sdk-v5"],
        "qiniu_kodo": ["qiniu"],
        "s3": ["boto3"],
        "sftp": ["paramiko"]
    }.get(plugin_id, [])

    if not dependencies:
        return {"success": True, "logs": [{"time": "", "level": "SUCCESS", "message": "该插件不需要外部 Python 依赖包。"}]}

    def log(level: str, msg: str) -> dict:
        now = datetime.datetime.now().strftime("%H:%M:%S")
        return {"time": now, "level": level, "message": msg}

    logs = []
    success = True
    
    # 动态构建可用镜像源列表，实现级联降级
    sources = [
        ("清华大学 PyPI 加速源", ["-i", "https://pypi.tuna.tsinghua.edu.cn/simple"]),
        ("阿里云 PyPI 加速源", ["-i", "https://mirrors.aliyun.com/pypi/simple/"]),
        ("系统默认配置源", [])
    ]
    
    # 共享的自愈参数列表 (例如在某一个包报错权限或系统托管时，后面的包自动应用其成果)
    extra_args = []

    for pkg in dependencies:
        pkg_success = False
        logs.append(log("INFO", f"⚙️ 开始分析依赖包 {pkg} 的安装环境..."))
        
        for source_name, source_args in sources:
            cmd = [sys.executable, "-m", "pip", "install", pkg]
            cmd.extend(source_args)
            
            # 环境诊断与自适应
            is_venv = (sys.prefix != sys.base_prefix)
            is_root = False
            if hasattr(os, "getuid"):
                try:
                    is_root = (os.getuid() == 0)
                except Exception:
                    pass
            
            # 在非虚环境且不是 root 用户时，默认先自适应追加 --user 参数防 Permission denied
            current_extra_args = list(extra_args)
            if not is_venv and not is_root and "--user" not in current_extra_args:
                current_extra_args.append("--user")
                
            cmd.extend(current_extra_args)
            
            try:
                process = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                if process.returncode == 0:
                    logs.append(log("SUCCESS", f"🟢 依赖包 {pkg} 成功通过 {source_name} 安装！"))
                    pkg_success = True
                    break
                else:
                    err_msg = (process.stderr or "").strip()
                    logs.append(log("WARNING", f"⚠️ 使用 {source_name} 安装 {pkg} 失败。准备尝试降级源..."))
                    
                    # 权限自愈策略
                    if "permission denied" in err_msg.lower() or "permission" in err_msg.lower():
                        if "--user" not in extra_args and not is_venv:
                            logs.append(log("INFO", "💡 检测到权限拦截，后续自愈尝试将自动追加 --user 隔离安装。"))
                            extra_args.append("--user")
                            
                    # PEP 668 外部管理环境自愈策略
                    if "externally-managed-environment" in err_msg.lower():
                        if "--break-system-packages" not in extra_args:
                            logs.append(log("INFO", "💡 检测到系统库锁定 (PEP 668)，后续自愈尝试将自动追加 --break-system-packages 强制绕过。"))
                            extra_args.append("--break-system-packages")
            except Exception as e:
                logs.append(log("WARNING", f"⚠️ 进程执行发生异常: {e}"))
                
        if not pkg_success:
            logs.append(log("ERROR", f"❌ 依赖包 {pkg} 安装失败。在所有可用源上均未成功部署。"))
            success = False

    return {"success": success, "logs": logs}
