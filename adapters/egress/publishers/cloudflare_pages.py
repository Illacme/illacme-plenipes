#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes — Cloudflare Pages Publisher Plugin
🚀 [V48.3]：通过 Wrangler CLI 将站点资产物理同步至 Cloudflare Edge 网络。

功能：
  1. 调用 `wrangler pages deploy` 将构建产物上传至 Cloudflare Pages
  2. 支持 production 与预览 (preview) 分支切换
  3. 支持多账号环境 (account_id 指定)
  4. 支持自定义 Wrangler CLI 路径
  5. 自动解析部署 URL
"""

import os
import shutil
import subprocess
from typing import Dict, Any, Optional, List

from core.adapters.egress.publishers.base import BasePublisher
from core.utils.tracing import tlog
from adapters.egress.publishers.cloudflare_utils import (
    mask_token,
    align_proxy,
    extract_deploy_url,
    build_wrangler_command,
    auto_fetch_account_id,
    emit_cloudflare_error_diagnostics,
    emit_cloudflare_timeout_diagnostics,
)


class CloudflarePagesPublisher(BasePublisher):
    """
    🚀 [V48.3] Cloudflare Pages 发布插件
    通过 Wrangler CLI 将静态站点产物部署至 Cloudflare Edge 网络。
    """
    PLUGIN_ID = "cloudflare_pages"
    DISPLAY_NAME = "Cloudflare Pages"
    VERSION = "V3.6"
    DESCRIPTION = "通过 Wrangler 协议将站点资产物理同步至 Cloudflare Edge 网络。"

    def __init__(self, config: Dict[str, Any], sys_config: Dict[str, Any] = None):
        super().__init__(config, sys_config)
        self.project_name = config.get("project_name", "")
        self.branch = config.get("branch", "production")
        self.account_id = config.get("account_id", "")
        self.wrangler_path = config.get("wrangler_path", "wrangler")
        self.token = config.get("token", "") or config.get("cloudflare_token", "")
        self.deploy_timeout = int(config.get("deploy_timeout", 300))
        self.api_timeout = int(config.get("api_timeout", 8))
        self.health_check_timeout = int(config.get("health_check_timeout", 15))

    def _mask_token(self, text: str) -> str:
        """🔒 抹除文本中可能夹带的明文 Cloudflare Token。"""
        return mask_token(text, self.token or os.environ.get("CLOUDFLARE_API_TOKEN", ""))

    def _align_proxy(self, proxy_str: str, for_python: bool = False) -> Optional[str]:
        """🔌 [代理协议自愈中枢]：自动对齐代理通道协议。"""
        return align_proxy(proxy_str, for_python=for_python)

    @staticmethod
    def _extract_deploy_url(stdout: str) -> Optional[str]:
        """从 Wrangler stdout 中解析部署 URL。"""
        return extract_deploy_url(stdout)

    def _build_wrangler_command(self, bundle_path: str) -> List[str]:
        """组装 wrangler pages deploy 命令参数。"""
        return build_wrangler_command(
            bundle_path=bundle_path,
            project_name=self.project_name,
            branch=self.branch,
            account_id=self.account_id,
            wrangler_path=self.wrangler_path,
        )

    def _auto_fetch_account_id(self, token: str) -> Optional[str]:
        """🚀 物理自愈：利用 Cloudflare Token 自动获取当前用户账号 ID。"""
        return auto_fetch_account_id(token, self.get_proxy(), self.api_timeout)

    def push(self, bundle_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """🚀 执行物理发布：通过 Wrangler CLI 将 bundle_path 下的产物上传至 Cloudflare Pages。"""
        if not self.project_name:
            return {"status": "skipped", "message": "Cloudflare Pages project_name not configured."}
        if not os.path.isdir(bundle_path):
            return {"status": "error", "message": f"Bundle path does not exist: {bundle_path}"}

        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        is_testing = "PYTEST_CURRENT_TEST" in os.environ
        local_wrangler_bin = os.path.join(project_root, "node_modules", ".bin", "wrangler")
        if not is_testing and not shutil.which("wrangler") and not os.path.exists(local_wrangler_bin):
            tlog.info("📡 [Cloudflare Pages] 未检测到本地或全局 wrangler，正在触发高速本地自愈安装...")
            self.ensure_npm_dependency("wrangler")

        token = self.token or os.environ.get("CLOUDFLARE_API_TOKEN", "")
        if not self.account_id and token and not any(ph in token.lower() for ph in ["your_token", "placeholder", "undefined"]):
            tlog.info("📡 [Cloudflare Pages] 物理自愈：未配置 account_id，正在尝试使用 Token 自动拉取 Cloudflare 账号列表...")
            fetched_id = self._auto_fetch_account_id(token)
            if fetched_id:
                self.account_id = fetched_id
                tlog.success(f"🟢 [Cloudflare Pages] 物理自愈：成功拉取并自动配置账号 ID: {self.account_id}")

        tlog.info(f"🚀 [Cloudflare Pages] 正在部署至项目 '{self.project_name}' ({self.branch})...")
        custom_proxy = self.get_proxy()
        aligned_node_proxy = self._align_proxy(custom_proxy, for_python=False)

        try:
            cmd = self._build_wrangler_command(bundle_path)
            tlog.debug(f"📋 [Cloudflare Pages] 执行命令: {' '.join(cmd)}")
            env = self._build_deploy_env(token, aligned_node_proxy)

            result = subprocess.run(
                cmd, env=env, cwd=project_root,
                capture_output=True, text=True, timeout=self.deploy_timeout
            )

            if result.returncode != 0:
                return self._handle_deploy_failure(result)

            deploy_url = self._extract_deploy_url(result.stdout)
            tlog.success(f"✅ [Cloudflare Pages] 部署成功！URL: {deploy_url or '(未解析)'}")
            return {
                "status": "success", "project": self.project_name,
                "branch": self.branch, "url": deploy_url,
                "message": result.stdout.strip()[-200:] if result.stdout else ""
            }
        except subprocess.TimeoutExpired as e:
            return self._handle_timeout_expired(e, custom_proxy)
        except FileNotFoundError:
            tlog.error(f"❌ [Cloudflare Pages] 找不到 Wrangler CLI: '{self.wrangler_path}'")
            return {"status": "error", "message": f"Wrangler CLI not found: '{self.wrangler_path}'"}
        except Exception as e:
            masked_err = self._mask_token(str(e))
            tlog.error(f"❌ [Cloudflare Pages] 部署异常: {masked_err}")
            return {"status": "error", "message": masked_err}

    def _build_deploy_env(self, token: str, aligned_node_proxy: Optional[str]) -> Dict[str, str]:
        """构建部署子进程的环境变量。"""
        env = os.environ.copy()
        for big_key, small_key in [("HTTPS_PROXY", "https_proxy"), ("HTTP_PROXY", "http_proxy"), ("ALL_PROXY", "all_proxy")]:
            if big_key in env and small_key not in env:
                env[small_key] = env[big_key]
            elif small_key in env and big_key not in env:
                env[big_key] = env[small_key]

        if aligned_node_proxy:
            tlog.info(f"🔌 [Cloudflare Pages] 检测到代理配置，正在强制注入子进程: {aligned_node_proxy}")
            env["HTTP_PROXY"] = aligned_node_proxy
            env["HTTPS_PROXY"] = aligned_node_proxy
            env["http_proxy"] = aligned_node_proxy
            env["https_proxy"] = aligned_node_proxy

        env["CI"] = "true"
        env["WRANGLER_SEND_METRICS"] = "false"
        env["CLOUDFLARE_TELEMETRY_DISABLED"] = "1"
        env["NPM_CONFIG_YES"] = "true"
        env["NPM_CONFIG_REGISTRY"] = "https://registry.npmmirror.com"
        env["NODE_TLS_REJECT_UNAUTHORIZED"] = "0"

        if token and not any(ph in token.lower() for ph in ["your_token", "placeholder", "undefined"]):
            env["CLOUDFLARE_API_TOKEN"] = token
        return env

    def _handle_deploy_failure(self, result: subprocess.CompletedProcess) -> Dict[str, Any]:
        """处理部署失败返回及自愈建议。"""
        masked_stdout = self._mask_token(result.stdout or "")
        masked_stderr = self._mask_token(result.stderr or "")
        tlog.error(f"❌ [Cloudflare Pages] Wrangler 部署失败 (Exit code {result.returncode})。")
        if masked_stdout:
            tlog.error(f"📋 Captured Stdout:\n{masked_stdout}")
        if masked_stderr:
            tlog.error(f"📋 Captured Stderr:\n{masked_stderr}")

        error_msg = masked_stderr.strip() or masked_stdout.strip() or "Unknown error"
        emit_cloudflare_error_diagnostics(error_msg)
        return {"status": "error", "message": f"Wrangler deploy failed: {error_msg}"}

    def _handle_timeout_expired(self, e: subprocess.TimeoutExpired, custom_proxy: Optional[str]) -> Dict[str, Any]:
        """处理部署超时异常。"""
        stdout_str = e.stdout.decode("utf-8", errors="ignore") if isinstance(e.stdout, bytes) else (e.stdout or "")
        stderr_str = e.stderr.decode("utf-8", errors="ignore") if isinstance(e.stderr, bytes) else (e.stderr or "")
        masked_stdout = self._mask_token(stdout_str)
        masked_stderr = self._mask_token(stderr_str)
        tlog.error(f"❌ [Cloudflare Pages] Wrangler 部署超时 (>{self.deploy_timeout}s)。")
        if masked_stdout:
            tlog.error(f"📋 Captured Stdout:\n{masked_stdout}")
        if masked_stderr:
            tlog.error(f"📋 Captured Stderr:\n{masked_stderr}")

        emit_cloudflare_timeout_diagnostics(custom_proxy)
        return {
            "status": "error",
            "message": (
                f"Wrangler deploy timed out after {self.deploy_timeout} seconds.\n\n"
                f"📋 Stdout:\n{masked_stdout}\n\n"
                f"📋 Stderr:\n{masked_stderr}\n\n"
                f"💡 [自愈提示] 当前注入代理: {custom_proxy or '直连'}。请确保代理状态健康，或尝试设置为 'direct' 强制直连。"
            )
        }

    def is_healthy(self) -> bool:
        """检查 Wrangler CLI 可用性与自愈"""
        self.ensure_npm_dependency("wrangler")
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        for bin_name in [self.wrangler_path, os.path.join(project_root, "node_modules", ".bin", "wrangler"), "npx"]:
            try:
                cmd = [bin_name, "--version"] if bin_name != "npx" else ["npx", "-y", "wrangler", "--version"]
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=self.health_check_timeout)
                if res.returncode == 0:
                    return True
            except Exception:
                continue
        return False

    def validate_config(self) -> List[str]:
        """校验配置完整性，返回错误信息列表"""
        errors = []
        if not self.project_name:
            errors.append("缺少必填配置: project_name")
        return errors

    def get_deploy_url(self) -> Optional[str]:
        """返回预期的部署 URL（基于项目名推导）"""
        if self.project_name:
            return f"https://{self.project_name}.pages.dev"
        return None
