# -*- coding: utf-8 -*-
"""
🛡️ [V74.9] Gov Plugin Ops Dependencies Installer Shard
职责：独立承载插件外部依赖包的一键自动安装、环境感应自适应与多镜像源 Failover 自愈逻辑。
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

    def log(level: str, msg: str) -> dict:
        now = datetime.datetime.now().strftime("%H:%M:%S")
        return {"time": now, "level": level, "message": msg}

    # ── 系统级 CLI 依赖（Git）自愈 ──────────────────────────
    if plugin_id == "github_pages":
        import shutil
        import platform
        if shutil.which("git"):
            return {"success": True, "logs": [{"time": "", "level": "SUCCESS", "message": "系统已存在可用的 git 工具，无需重复安装。"}]}
        
        sys_type = platform.system()
        logs = []
        
        # 1. macOS (Darwin) - 使用 Homebrew 自愈
        if sys_type == "Darwin":
            brew_path = shutil.which("brew")
            if brew_path:
                logs.append(log("INFO", "🧬 [物理自愈] 检测到 macOS 缺失 git，但发现 Homebrew。正在自动执行 brew install git..."))
                try:
                    process = subprocess.run([brew_path, "install", "git"], capture_output=True, text=True, timeout=300)
                    if process.returncode == 0:
                        logs.append(log("SUCCESS", "🟢 [物理自愈] Git 命令行工具通过 Homebrew 自动装载成功！"))
                        return {"success": True, "logs": logs}
                    else:
                        logs.append(log("ERROR", f"❌ brew install git 失败: {process.stderr or process.stdout}"))
                        return {"success": False, "logs": logs}
                except Exception as e:
                    logs.append(log("ERROR", f"❌ 执行 brew 安装进程异常: {e}"))
                    return {"success": False, "logs": logs}

        # 2. Linux - 使用 apt-get, yum 或 dnf 自愈
        elif sys_type == "Linux":
            pkg_mgr = None
            install_cmd = []
            if shutil.which("apt-get"):
                pkg_mgr = "apt-get"
                install_cmd = ["sudo", "apt-get", "update", "&&", "sudo", "apt-get", "install", "-y", "git"]
            elif shutil.which("yum"):
                pkg_mgr = "yum"
                install_cmd = ["sudo", "yum", "install", "-y", "git"]
            elif shutil.which("dnf"):
                pkg_mgr = "dnf"
                install_cmd = ["sudo", "dnf", "install", "-y", "git"]
                
            if pkg_mgr:
                logs.append(log("INFO", f"🧬 [物理自愈] 检测到 Linux 缺失 git，发现包管理器 {pkg_mgr}。正在自动执行安装..."))
                try:
                    process = subprocess.run(" ".join(install_cmd), capture_output=True, text=True, timeout=300, shell=True)
                    if process.returncode == 0:
                        logs.append(log("SUCCESS", f"🟢 [物理自愈] Git 命令行工具通过 {pkg_mgr} 自动装载成功！"))
                        return {"success": True, "logs": logs}
                    else:
                        logs.append(log("ERROR", f"❌ 通过 {pkg_mgr} 安装 git 失败: {process.stderr or process.stdout}"))
                        return {"success": False, "logs": logs}
                except Exception as e:
                    logs.append(log("ERROR", f"❌ 执行 Linux 安装进程异常: {e}"))
                    return {"success": False, "logs": logs}

        # 3. Windows - 使用 winget 或 choco 自愈
        elif sys_type == "Windows":
            win_tool = None
            install_cmd = []
            if shutil.which("winget"):
                win_tool = "winget"
                install_cmd = ["winget", "install", "--silent", "Git.Git"]
            elif shutil.which("choco"):
                win_tool = "choco"
                install_cmd = ["choco", "install", "-y", "git"]
                
            if win_tool:
                logs.append(log("INFO", f"🧬 [物理自愈] 检测到 Windows 缺失 git，发现包管理器 {win_tool}。正在自动执行安装..."))
                try:
                    process = subprocess.run(install_cmd, capture_output=True, text=True, timeout=300, shell=True)
                    if process.returncode == 0:
                        logs.append(log("SUCCESS", f"🟢 [物理自愈] Git 命令行工具通过 {win_tool} 自动装载成功！"))
                        return {"success": True, "logs": logs}
                    else:
                        logs.append(log("ERROR", f"❌ 通过 {win_tool} 安装 git 失败: {process.stderr or process.stdout}"))
                        return {"success": False, "logs": logs}
                except Exception as e:
                    logs.append(log("ERROR", f"❌ 执行 Windows 安装进程异常: {e}"))
                    return {"success": False, "logs": logs}
        
        return {
            "success": False,
            "error": "物理自愈未完成：未检测到 Git 命令行工具。请在系统终端手动执行安装（如：brew install git、apt install git 或从 git-scm.com 下载安装）后再试。"
        }

    # ── Node/npm 依赖安装分支 ─────────────────────────────
    npm_deps = {
        "cloudflare_pages": ["wrangler"],
        "netlify": ["netlify-cli"],
        "vercel": ["vercel"],
        "firebase": ["firebase-tools"]
    }
    if plugin_id in npm_deps:
        import shutil
        import platform
        npm_path = shutil.which("npm")
        if not npm_path:
            return {
                "success": False,
                "error": "物理自愈失败：系统未检测到 Node.js 或 npm 运行环境，请先在宿主机安装 Node.js 后重试。"
            }
        
        is_windows = (platform.system() == "Windows")
        logs = []
        success = True
        for pkg in npm_deps[plugin_id]:
            logs.append(log("INFO", f"⚙️ 检测到 Node 环境。正在执行本地 npm 安装: {pkg}..."))
            cmd = [npm_path, "install", pkg, "--save-dev"]
            try:
                process = subprocess.run(cmd, capture_output=True, text=True, timeout=180, shell=is_windows)
                if process.returncode == 0:
                    logs.append(log("SUCCESS", f"🟢 依赖包 {pkg} 本地开发依赖安装成功！"))
                else:
                    err = (process.stderr or "").strip() or (process.stdout or "").strip()
                    logs.append(log("ERROR", f"❌ 依赖包 {pkg} 安装失败: {err}"))
                    success = False
            except Exception as e:
                logs.append(log("ERROR", f"❌ 执行安装进程异常: {e}"))
                success = False
        return {"success": success, "logs": logs}

    # ── Python 依赖安装分支 ──────────────────────────────
    dependencies = {
        "aliyun_oss": ["oss2"],
        "tencent_cos": ["cos-python-sdk-v5"],
        "qiniu_kodo": ["qiniu"],
        "s3": ["boto3"],
        "sftp": ["paramiko"]
    }.get(plugin_id, [])

    if not dependencies:
        return {"success": True, "logs": [{"time": "", "level": "SUCCESS", "message": "该插件不需要外部 Python/npm 依赖包。"}]}

    logs = []
    success = True
    
    # 动态构建可用镜像源列表，实现级联降级
    sources = [
        ("清华大学 PyPI 加速源", ["-i", "https://pypi.tuna.tsinghua.edu.cn/simple"]),
        ("阿里云 PyPI 加速源", ["-i", "https://mirrors.aliyun.com/pypi/simple/"]),
        ("系统默认配置源", [])
    ]
    
    # 共享的自愈参数列表
    extra_args = []
    import platform
    is_windows = (platform.system() == "Windows")

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
                process = subprocess.run(cmd, capture_output=True, text=True, timeout=60, shell=is_windows)
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
