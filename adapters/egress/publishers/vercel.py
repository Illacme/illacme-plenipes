#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes — Vercel Publisher Plugin
🚀 [V48.3]：通过 Vercel CLI 将站点资产物理同步至 Vercel Edge Network。
🛡️ [SOP-01 & SOP-02]：自底向上物理拆分重构版本，单文件物理行数严格 ≤300 行。
"""

import os
import subprocess
from typing import Dict, Any, Optional, List

from core.adapters.egress.publishers.base import BasePublisher
from core.utils.tracing import tlog
from .vercel_utils import (
    add_autotherapy_suggestion,
    resolve_proxy_env,
    sanitize_cmd_for_log,
    extract_deploy_url,
    auto_create_project,
)


class VercelPublisher(BasePublisher):
    """
    🚀 [V48.3] Vercel 发布插件
    通过 Vercel CLI 将静态站点产物部署至 Vercel Edge Network。
    """
    PLUGIN_ID = "vercel"
    DISPLAY_NAME = "Vercel"
    VERSION = "V3.5"
    DESCRIPTION = "通过 Vercel CLI 将站点资产物理同步至 Vercel Edge Network。"

    def __init__(self, config: Dict[str, Any], sys_config: Dict[str, Any] = None):
        super().__init__(config, sys_config)
        self.token = config.get("token", "")
        self.project_name = config.get("project_name", "")
        self.org_id = config.get("org_id", "")
        self.prod = config.get("prod", True)
        self.vercel_path = config.get("vercel_path", "vercel")
        self.proxy = config.get("proxy", "") or (sys_config.get("global_proxy") if isinstance(sys_config, dict) else "")

    def push(self, bundle_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """🚀 执行物理发布：通过 Vercel CLI 将 bundle_path 下的产物上传至 Vercel。"""
        if not self.token:
            return {"status": "skipped", "message": "Vercel token not configured."}

        if not os.path.isdir(bundle_path):
            return {"status": "error", "message": f"Bundle path does not exist: {bundle_path}"}

        is_primary = metadata.get("is_primary", False) if isinstance(metadata, dict) else False
        role_tag = " [官方主站]" if is_primary else (" [备用镜像]" if isinstance(metadata, dict) and "is_primary" in metadata else "")
        mode_label = "生产" if self.prod else "预览"
        tlog.info(f"🚀 [Vercel]{role_tag} 正在以 {mode_label} 模式部署...")

        # 自动增强静态路由（Clean URL 友好支持）
        vercel_json_path = os.path.join(bundle_path, "vercel.json")
        if not os.path.exists(vercel_json_path):
            try:
                import json
                with open(vercel_json_path, "w", encoding="utf-8") as f:
                    json.dump({"cleanUrls": True, "trailingSlash": False}, f, indent=2)
            except Exception as e:
                tlog.warning(f"⚠️ [Vercel] 写入 vercel.json 失败: {e}")

        try:
            cmd = self._build_vercel_command(bundle_path)
            tlog.debug(f"📋 [Vercel] 执行命令: {self._sanitize_cmd_for_log(cmd)}")

            env = os.environ.copy()
            env["CI"] = "1"
            if self.org_id:
                env["VERCEL_ORG_ID"] = self.org_id
            env = self._resolve_proxy_env(env)

            max_attempts = 2
            result = None
            for attempt in range(1, max_attempts + 1):
                result = subprocess.run(
                    cmd,
                    capture_output=True, text=True,
                    timeout=300,
                    env=env
                )

                if result.returncode == 0:
                    break

                error_msg = result.stderr.strip() or result.stdout.strip() or "Unknown error"
                if "was not found in the current scope" in error_msg and self.project_name:
                    tlog.info(f"ℹ️ [Vercel] 检测到项目 '{self.project_name}' 尚未创建，正在自动执行一键自愈创建...")
                    if self._auto_create_project():
                        continue

                network_errs = ["fetch failed", "upload aborted", "econnreset", "socket hang up", "timed out"]
                if attempt < max_attempts and any(ne in error_msg.lower() for ne in network_errs):
                    tlog.warning(f"⚠️ [Vercel] 遭遇网络抖动 ({error_msg[:100]}...)，正在执行自愈重试 ({attempt}/{max_attempts})...")
                    continue

                break

            if result.returncode != 0:
                error_msg = result.stderr.strip() or result.stdout.strip() or "Unknown error"
                healed_err = self._add_autotherapy_suggestion(error_msg)
                tlog.error(f"❌ [Vercel] 部署失败: {healed_err}")
                return {"status": "error", "message": f"Vercel deploy failed: {healed_err}"}

            deploy_url = self._extract_deploy_url(result.stdout)
            canonical_url = f"https://{self.project_name}.vercel.app" if self.project_name else ""
            primary_url = canonical_url if (self.prod and canonical_url) else (deploy_url or canonical_url)

            role_desc = f" [{ '官方主站' if is_primary else '备用镜像' }]" if isinstance(metadata, dict) and "is_primary" in metadata else ""
            tlog.success(f"✅ [Vercel] 部署成功{role_desc}！生产域名: {primary_url} (实例: {deploy_url or '未解析'})")
            return {
                "status": "success",
                "project": self.project_name,
                "mode": "production" if self.prod else "preview",
                "url": primary_url,
                "deployment_url": deploy_url,
                "message": result.stdout.strip()[-200:] if result.stdout else ""
            }

        except subprocess.TimeoutExpired:
            tlog.error("❌ [Vercel] 部署超时 (>300s)。")
            return {"status": "error", "message": "Vercel deploy timed out after 300 seconds."}
        except FileNotFoundError:
            tlog.error(f"❌ [Vercel] 找不到 Vercel CLI: '{self.vercel_path}'")
            return {"status": "error", "message": f"Vercel CLI not found: '{self.vercel_path}'"}
        except Exception as e:
            healed_err = self._add_autotherapy_suggestion(str(e))
            tlog.error(f"❌ [Vercel] 部署异常: {healed_err}")
            return {"status": "error", "message": healed_err}

    def _add_autotherapy_suggestion(self, err_msg: str) -> str:
        """💡 为 Vercel 错误注入友好免密授权物理自愈提示。"""
        return add_autotherapy_suggestion(err_msg)

    def is_healthy(self) -> bool:
        """检查 Vercel CLI 可用性与自愈"""
        self.ensure_npm_dependency("vercel")
        for bin_name in [self.vercel_path, os.path.join(os.getcwd(), "node_modules", ".bin", "vercel"), "npx"]:
            try:
                cmd = [bin_name, "--version"] if bin_name != "npx" else ["npx", "-y", "vercel", "--version"]
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
                if res.returncode == 0:
                    return True
            except Exception:
                continue
        return False

    def validate_config(self) -> List[str]:
        """校验配置完整性，返回错误信息列表"""
        errors = []
        if not self.token:
            errors.append("缺少必填配置: token")
        return errors

    def get_deploy_url(self) -> Optional[str]:
        """返回预期的部署 URL（基于项目名推导）"""
        if self.project_name:
            return f"https://{self.project_name}.vercel.app"
        return None

    def _resolve_executable(self) -> list:
        """自愈解析 Vercel 可执行命令，优先使用指定路径，缺失时自动降级到 npx -y vercel"""
        import shutil
        if shutil.which(self.vercel_path):
            return [self.vercel_path]
        local_bin = os.path.join(os.getcwd(), "node_modules", ".bin", "vercel")
        if os.path.exists(local_bin) and os.access(local_bin, os.X_OK):
            return [local_bin]
        return ["npx", "-y", "vercel"]

    def _auto_create_project(self) -> bool:
        """🚀 [V48.4] 远端项目自动创建自愈：委托至 vercel_utils 模块"""
        return auto_create_project(self._resolve_executable(), self.project_name, self.token, self.org_id)

    def _resolve_proxy_env(self, env: dict) -> dict:
        """注入代理环境变量，委托至 vercel_utils 模块"""
        return resolve_proxy_env(self.proxy, env)

    def _build_vercel_command(self, bundle_path: str) -> list:
        """组装 vercel deploy 命令参数"""
        cmd = self._resolve_executable() + [
            "deploy",
            bundle_path,
            "--yes",
            f"--token={self.token}"
        ]
        if self.prod:
            cmd.append("--prod")
        if self.project_name:
            cmd.extend(["--project", self.project_name])
        return cmd

    @staticmethod
    def _sanitize_cmd_for_log(cmd: list) -> str:
        """脱敏命令行日志（隐藏 Token）"""
        return sanitize_cmd_for_log(cmd)

    @staticmethod
    def _extract_deploy_url(stdout: str) -> Optional[str]:
        """从 Vercel CLI stdout 中解析部署 URL"""
        return extract_deploy_url(stdout)
