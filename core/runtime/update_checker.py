# -*- coding: utf-8 -*-
"""
Illacme Plenipes - Auto-Update Sentinel & Cloud Release Checker
模块职责：负责感知云端 GitHub Releases 最新发版、语义化版本比对及宿主操作系统专属安装包智能匹配。
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""

import os
import re
import sys
import time
import json
import platform
import urllib.request
import urllib.error
from typing import Dict, Any, Optional, Tuple

from core.utils.tracing import tlog

# 当前客户端发版真理源 (发版时随 build 自动对齐)
APP_VERSION = "1.5.0"
GITHUB_REPO = "Illacme/illacme-plenipes"
CACHE_TTL_SECONDS = 600.0  # 10 分钟内存缓存，防御 GitHub 速率限制


class UpdateChecker:
    """🛰️ 云端版本探测与客户端升级中枢"""

    _cache_payload: Optional[Dict[str, Any]] = None
    _last_checked_time: float = 0.0

    @classmethod
    def get_current_version(cls) -> str:
        """获取当前客户端的语义化版本号 (去除前导 v)"""
        # 1. 优先尝试从环境变量读取
        env_ver = os.getenv("ILLACME_CLIENT_VERSION")
        if env_ver:
            return env_ver.lstrip("v").strip()

        # 2. 若在源码开发环境中，尝试从 Git Tag 读取真实标签
        try:
            import subprocess
            res = subprocess.run(
                ["git", "describe", "--tags", "--abbrev=0"],
                capture_output=True,
                text=True,
                timeout=1.5,
                cwd=os.path.dirname(os.path.abspath(__file__))
            )
            if res.returncode == 0 and res.stdout.strip():
                return res.stdout.strip().lstrip("v")
        except Exception:
            pass

        return APP_VERSION.lstrip("v")

    @classmethod
    def parse_semver(cls, ver_str: str) -> Tuple[int, int, int]:
        """将版本字符串解析为数字三元组 (major, minor, patch)，忽略 prerelease 后缀"""
        # 1. 剔除 - 或 + 后的 prerelease/build 元数据 (如 -rc1, +build2)
        base = ver_str.lstrip("v").strip().split("-")[0].split("+")[0]
        clean = re.sub(r"[^\d.]", "", base)
        parts = clean.split(".")
        nums = []
        for p in parts[:3]:
            try:
                nums.append(int(p))
            except ValueError:
                nums.append(0)
        while len(nums) < 3:
            nums.append(0)
        return (nums[0], nums[1], nums[2])

    @classmethod
    def is_newer_version(cls, latest_ver: str, current_ver: str) -> bool:
        """比对最新版本是否高于当前版本"""
        latest_tuple = cls.parse_semver(latest_ver)
        current_tuple = cls.parse_semver(current_ver)
        return latest_tuple > current_tuple

    @classmethod
    def detect_platform_asset(cls, assets: list) -> Optional[Dict[str, Any]]:
        """根据当前操作系统与 CPU 架构，智能匹配最优推荐安装包"""
        os_type = platform.system()
        machine = platform.machine().lower()
        is_arm = "arm" in machine or "aarch64" in machine

        candidates = []
        for a in assets:
            name = a.get("name", "")
            if not name or name.endswith(".sha256"):
                continue

            # macOS 智能匹配
            if os_type == "Darwin":
                if ".dmg" in name:
                    candidates.append((10, a, "原装 DMG 镜像 (首选)"))
                elif ".zip" in name and "macOS" in name:
                    candidates.append((5, a, "便携 ZIP 压缩包"))

            # Windows 智能匹配
            elif os_type == "Windows":
                if "-Setup.exe" in name:
                    candidates.append((10, a, "一键安装向导 (首选)"))
                elif ".zip" in name and "Windows" in name:
                    candidates.append((5, a, "便携 ZIP 压缩包"))

            # Linux 智能匹配
            elif os_type == "Linux":
                if ".tar.gz" in name and "Linux" in name:
                    candidates.append((10, a, "原生运行归档"))

        if not candidates:
            return None

        # 按优先级权重降序排序
        candidates.sort(key=lambda x: x[0], reverse=True)
        best = candidates[0][1]
        desc = candidates[0][2]
        size_bytes = best.get("size", 0)
        size_mb = round(size_bytes / (1024 * 1024), 1) if size_bytes else 0.0

        return {
            "name": best.get("name"),
            "download_url": best.get("browser_download_url"),
            "size_mb": size_mb,
            "format_desc": desc,
            "download_count": best.get("download_count", 0)
        }

    @classmethod
    def check_update(cls, force: bool = False, repo: str = GITHUB_REPO) -> Dict[str, Any]:
        """
        请求 GitHub Releases API 检查最新版本。
        内置 10 分钟缓存与超时容错，确保全链路静默不卡顿。
        """
        now = time.time()
        if not force and cls._cache_payload and (now - cls._last_checked_time < CACHE_TTL_SECONDS):
            return cls._cache_payload

        current_ver = cls.get_current_version()
        api_url = f"https://api.github.com/repos/{repo}/releases/latest"

        req = urllib.request.Request(
            api_url,
            headers={
                "User-Agent": f"Illacme-Plenipes-Desktop/{current_ver}",
                "Accept": "application/vnd.github.v3+json"
            }
        )

        try:
            with urllib.request.urlopen(req, timeout=5.0) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    tag_name = data.get("tag_name", "").lstrip("v")
                    has_update = cls.is_newer_version(tag_name, current_ver)
                    assets = data.get("assets", [])
                    recommended_asset = cls.detect_platform_asset(assets)

                    payload = {
                        "status": "success",
                        "current_version": f"v{current_ver}",
                        "latest_version": f"v{tag_name}" if tag_name else f"v{current_ver}",
                        "has_update": has_update,
                        "release_name": data.get("name", f"Illacme Plenipes v{tag_name}"),
                        "published_at": data.get("published_at", ""),
                        "html_url": data.get("html_url", f"https://github.com/{repo}/releases"),
                        "release_notes": data.get("body", ""),
                        "recommended_asset": recommended_asset,
                        "assets_count": len(assets),
                        "checked_at": time.strftime("%Y-%m-%d %H:%M:%S")
                    }

                    cls._cache_payload = payload
                    cls._last_checked_time = now
                    tlog.info(f"🛰️ [版本检查] 成功同步云端版本: 最新 v{tag_name} (当前 v{current_ver}, 有更新: {has_update})")
                    return payload

        except urllib.error.HTTPError as e:
            tlog.warning(f"⚠️ [版本检查] GitHub API HTTP 异常: {e.code} - {e.reason}")
        except urllib.error.URLError as e:
            tlog.warning(f"⚠️ [版本检查] 网络连接异常 (可能离线或网络受限): {e.reason}")
        except Exception as e:
            tlog.warning(f"⚠️ [版本检查] 未知异常: {e}")

        # 离线或异常时的安全降级兜底
        fallback = {
            "status": "offline_fallback",
            "current_version": f"v{current_ver}",
            "latest_version": f"v{current_ver}",
            "has_update": False,
            "release_name": f"Illacme Plenipes v{current_ver}",
            "html_url": f"https://github.com/{repo}/releases",
            "release_notes": "当前处于离线环境或网络受限，未能获取云端更新说明。",
            "recommended_asset": None,
            "checked_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        return fallback
