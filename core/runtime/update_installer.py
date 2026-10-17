# -*- coding: utf-8 -*-
"""
Illacme Plenipes - In-App Silent Auto-Update & Self-Restart Pipeline
模块职责：负责客户端后台静默下载、断点分块流式传输、跨平台无缝静默替换与优雅自重启。
🛡️ [SOP-01 规范]：单文件行数严格 ≤ 300 行。
"""

import os
import sys
import time
import shutil
import platform
import threading
import subprocess
import urllib.request
import urllib.error
from typing import Dict, Any, Optional

from core.utils.tracing import tlog


class UpdateInstaller:
    """🛰️ 应用内后台静默更新与跨平台自重启引擎"""

    _lock = threading.Lock()
    _download_thread: Optional[threading.Thread] = None
    _status: str = "idle"  # idle | downloading | ready | applying | error
    _downloaded_bytes: int = 0
    _total_bytes: int = 0
    _percent: float = 0.0
    _speed_mb: float = 0.0
    _error_message: str = ""
    _downloaded_file_path: Optional[str] = None
    _target_version: str = ""

    @classmethod
    def get_cache_dir(cls) -> str:
        """获取更新缓存目录"""
        base_dir = os.path.join(os.getcwd(), ".plenipes", "cache", "updates")
        os.makedirs(base_dir, exist_ok=True)
        return base_dir

    @classmethod
    def get_progress(cls) -> Dict[str, Any]:
        """获取当前下载或升级进度"""
        with cls._lock:
            return {
                "status": cls._status,
                "downloaded_bytes": cls._downloaded_bytes,
                "total_bytes": cls._total_bytes,
                "percent": round(cls._percent, 1),
                "speed_mb": round(cls._speed_mb, 2),
                "error": cls._error_message,
                "file_path": cls._downloaded_file_path,
                "target_version": cls._target_version,
                "is_ready": cls._status == "ready" and bool(cls._downloaded_file_path and os.path.exists(cls._downloaded_file_path))
            }

    @classmethod
    def start_download(cls, download_url: str, version: str = "", filename: Optional[str] = None) -> Dict[str, Any]:
        """在后台守护线程中启动静默分块下载"""
        with cls._lock:
            if cls._status == "downloading":
                return {"success": False, "message": "已有更新任务正在下载中", "status": "downloading"}

            cls._status = "downloading"
            cls._downloaded_bytes = 0
            cls._total_bytes = 0
            cls._percent = 0.0
            cls._speed_mb = 0.0
            cls._error_message = ""
            cls._target_version = version

        # 启动后台守护工作线程
        thread = threading.Thread(
            target=cls._download_worker,
            args=(download_url, version, filename),
            daemon=True,
            name="SilentUpdateDownloader"
        )
        cls._download_thread = thread
        thread.start()

        tlog.info(f"🛰️ [静默更新] 已点火后台下载线程: {download_url}")
        return {"success": True, "message": "已在后台启动静默下载", "status": "downloading"}

    @classmethod
    def _download_worker(cls, url: str, version: str, custom_filename: Optional[str]) -> None:
        """分块流式下载工作函数"""
        cache_dir = cls.get_cache_dir()
        file_name = custom_filename or url.split("/")[-1] or f"illacme_update_{int(time.time())}.bin"
        final_path = os.path.join(cache_dir, file_name)
        part_path = final_path + ".part"

        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Illacme-Plenipes-AutoUpdater/1.0"}
        )

        try:
            with urllib.request.urlopen(req, timeout=15.0) as resp:
                total = int(resp.headers.get("content-length", 0))
                with cls._lock:
                    cls._total_bytes = total

                downloaded = 0
                start_time = time.time()
                last_calc_time = start_time
                last_calc_bytes = 0

                with open(part_path, "wb") as f:
                    chunk_size = 128 * 1024  # 128KB 缓冲区
                    while True:
                        chunk = resp.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)

                        now = time.time()
                        if now - last_calc_time >= 0.5:
                            duration = now - last_calc_time
                            speed = ((downloaded - last_calc_bytes) / (1024 * 1024)) / duration if duration > 0 else 0
                            pct = (downloaded / total * 100) if total > 0 else 0

                            with cls._lock:
                                cls._downloaded_bytes = downloaded
                                cls._percent = pct
                                cls._speed_mb = speed

                            last_calc_time = now
                            last_calc_bytes = downloaded

            # 下载完成，重命名临时文件
            if os.path.exists(final_path):
                try:
                    os.remove(final_path)
                except Exception:
                    pass
            shutil.move(part_path, final_path)

            with cls._lock:
                cls._status = "ready"
                cls._downloaded_bytes = downloaded
                cls._percent = 100.0
                cls._speed_mb = 0.0
                cls._downloaded_file_path = final_path

            tlog.info(f"✅ [静默更新] 安装包下载完成: {final_path} (大小: {round(downloaded / (1024*1024), 2)} MB)")

        except Exception as e:
            tlog.error(f"❌ [静默更新] 下载失败: {e}")
            if os.path.exists(part_path):
                try:
                    os.remove(part_path)
                except Exception:
                    pass
            with cls._lock:
                cls._status = "error"
                cls._error_message = str(e)

    @classmethod
    def apply_and_restart(cls) -> Dict[str, Any]:
        """
        🚀 执行静默替换或启动安装向导，并在释放单例锁后自重启客户端
        """
        with cls._lock:
            if cls._status != "ready" or not cls._downloaded_file_path or not os.path.exists(cls._downloaded_file_path):
                return {"success": False, "message": "更新包尚未就绪，无法执行升级"}
            cls._status = "applying"
            file_path = cls._downloaded_file_path

        os_type = platform.system()
        tlog.info(f"🔄 [静默更新] 准备执行宿主系统升级自重启 ({os_type}): {file_path}")

        try:
            # 1. Windows 环境静默安装与重启流水线
            if os_type == "Windows" and file_path.lower().endswith(".exe"):
                bat_script = os.path.join(cls.get_cache_dir(), "apply_update.bat")
                current_pid = os.getpid()
                exe_target = sys.executable if getattr(sys, "frozen", False) else sys.argv[0]

                bat_content = f"""@echo off
timeout /t 1 /nobreak > nul
start "" /wait "{file_path}" /VERYSILENT /SUPPRESSMSGBOXES /NORESTART /CLOSEAPPLICATIONS
start "" "{exe_target}"
del "%~f0"
"""
                with open(bat_script, "w", encoding="gbk") as f:
                    f.write(bat_content)

                # 以完全分离的子进程拉起
                subprocess.Popen(["cmd.exe", "/c", bat_script], creationflags=0x00000008 | 0x00000200)
                cls._schedule_exit(1.0)
                return {"success": True, "message": "正在执行静默升级并自重启，客户端即将就绪..."}

            # 2. macOS 环境下 DMG 挂载与静默覆盖或应用拉起
            elif os_type == "Darwin":
                sh_script = os.path.join(cls.get_cache_dir(), "apply_update.sh")
                current_app = "/Applications/Illacme Plenipes.app"
                
                sh_content = f"""#!/bin/sh
sleep 1
# 探测是否为 DMG 并执行挂载
if echo "{file_path}" | grep -q "\\.dmg$"; then
    MOUNT_POINT=$(hdiutil attach "{file_path}" -nobrowse -readonly | grep -o '/Volumes/.*' | head -n 1)
    if [ -n "$MOUNT_POINT" ]; then
        APP_SRC=$(find "$MOUNT_POINT" -maxdepth 1 -name "*.app" | head -n 1)
        if [ -n "$APP_SRC" ]; then
            cp -R "$APP_SRC" "/Applications/"
            hdiutil detach "$MOUNT_POINT" -force > /dev/null 2>&1
            open -a "{current_app}"
            rm -f "$0"
            exit 0
        fi
        hdiutil detach "$MOUNT_POINT" -force > /dev/null 2>&1
    fi
fi
# 兜底回退：若非 DMG 或挂载失败，调用系统 open 打开
open "{file_path}"
rm -f "$0"
"""
                with open(sh_script, "w", encoding="utf-8") as f:
                    f.write(sh_content)
                os.chmod(sh_script, 0o755)

                subprocess.Popen(["/bin/sh", sh_script], start_new_session=True)
                cls._schedule_exit(1.2)
                return {"success": True, "message": "正在执行无缝替换并重启应用，请稍候..."}

            # 3. 通用系统降级：打开下载文件并退出当前进程
            else:
                if shutil.which("xdg-open"):
                    subprocess.Popen(["xdg-open", file_path], start_new_session=True)
                cls._schedule_exit(1.5)
                return {"success": True, "message": "已调起系统安装向导，客户端正在重启..."}

        except Exception as e:
            tlog.error(f"❌ [静默更新] 执行自重启失败: {e}")
            with cls._lock:
                cls._status = "error"
                cls._error_message = f"执行升级自重启失败: {e}"
            return {"success": False, "message": f"执行升级失败: {e}"}

    @classmethod
    def _schedule_exit(cls, delay_sec: float) -> None:
        """延迟退出当前进程，释放单例锁"""
        def _do_exit():
            time.sleep(delay_sec)
            tlog.info("🛑 [静默更新] 客户端进程安全退出，将控制权交接给新版实例。")
            os._exit(0)

        t = threading.Thread(target=_do_exit, daemon=True)
        t.start()
