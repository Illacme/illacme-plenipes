#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes — Netlify Publisher Plugin
🚀 [V48.3]：通过 Netlify CLI 将站点资产物理同步至 Netlify CDN 网络。

功能：
  1. 调用 `netlify deploy` 将构建产物上传至 Netlify
  2. 支持生产 (--prod) 与草稿 (draft) 模式
  3. 通过环境变量安全传递 Auth Token（不暴露于命令行）
  4. 自动解析 Live URL 与 Deploy URL
  5. 支持自定义 Netlify CLI 路径

配置示例 (config.yaml):
  netlify:
    enabled: true
    site_id: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"  # 必填
    auth_token: "ENC:xxxxxx"                          # 必填，支持加密
    prod: true                                         # 可选，默认 true
    message: "deploy: {timestamp}"                     # 可选
    netlify_path: "netlify"                            # 可选
"""

import os
import re
import subprocess
from typing import Dict, Any, Optional, List

from core.adapters.egress.publishers.base import BasePublisher
from core.utils.tracing import tlog
from .netlify_utils import deploy_via_direct_api, add_autotherapy_suggestion


class NetlifyPublisher(BasePublisher):
    """
    🚀 [V48.3] Netlify 发布插件
    通过 Netlify CLI 将静态站点产物部署至 Netlify CDN 网络。
    """
    PLUGIN_ID = "netlify"
    DISPLAY_NAME = "Netlify"
    VERSION = "V3.5"
    DESCRIPTION = "通过 Netlify CLI 将站点资产物理同步至 Netlify 全球 CDN 网络。"

    # ==========================================
    # 生命周期
    # ==========================================

    def __init__(self, config: Dict[str, Any], sys_config: Dict[str, Any] = None):
        super().__init__(config, sys_config)
        self.site_id = config.get("site_id", "")
        self.auth_token = config.get("auth_token", "")
        self.prod = config.get("prod", True)
        self.message = config.get("message", "")
        self.netlify_path = config.get("netlify_path", "netlify")

    # ==========================================
    # BasePublisher 契约实现
    # ==========================================

    def push(self, bundle_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        🚀 执行物理发布：通过 Netlify CLI 将 bundle_path 下的产物上传至 Netlify。

        执行流程：
          1. 校验配置完整性 (site_id + auth_token 必填)
          2. 校验 bundle_path 物理存在性
          3. 组装 netlify deploy 命令
          4. 通过环境变量 NETLIFY_AUTH_TOKEN 安全传递凭据
          5. 执行子进程 (超时 300s)
          6. 解析 stdout 提取 Live URL
          7. 返回标准化结果字典

        :param bundle_path: 本地构建产物目录（SSG 输出目录）
        :param metadata: 任务元数据
        :return: 发布结果字典
        """
        # ── 1. 前置校验 ──────────────────────────────────
        if not self.site_id:
            return {"status": "skipped", "message": "Netlify site_id not configured."}

        if not self.auth_token:
            return {"status": "skipped", "message": "Netlify auth_token not configured."}

        if not os.path.isdir(bundle_path):
            return {"status": "error", "message": f"Bundle path does not exist: {bundle_path}"}

        # ── 2. 依赖自闭环决策：若显式开启 direct_api 或宿主机完全无 CLI 与 npx 时走原生 Direct API ────
        import shutil
        use_direct = getattr(self, "direct_api", False) or (self.config.get("direct_api") if isinstance(self.config, dict) else False)
        if use_direct or (not self._has_cli() and not shutil.which("npx")):
            tlog.info("📡 [Netlify] 已激活【原生 Direct REST API 直传引擎】...")
            return deploy_via_direct_api(self, bundle_path, metadata)

        mode_label = "生产" if self.prod else "草稿"
        tlog.info(f"🚀 [Netlify] 正在以 {mode_label} 模式部署至站点 '{self.site_id}'...")

        try:
            # ── 3. 组装命令 ──────────────────────────────
            cmd = self._build_netlify_command(bundle_path, metadata)
            tlog.debug(f"📋 [Netlify] 执行命令: {' '.join(cmd)}")

            # ── 4. 准备安全环境变量 ──────────────────────
            env = os.environ.copy()
            env["NETLIFY_AUTH_TOKEN"] = self.auth_token

            # ── 5. 执行部署 ──────────────────────────────
            result = subprocess.run(
                cmd,
                capture_output=True, text=True,
                timeout=300,
                env=env
            )

            if result.returncode != 0:
                error_msg = result.stderr.strip() or result.stdout.strip() or "Unknown error"
                healed_err = self._add_autotherapy_suggestion(error_msg)
                tlog.error(f"❌ [Netlify] 部署失败: {healed_err}")
                return {"status": "error", "message": f"Netlify deploy failed: {healed_err}"}

            # ── 6. 解析部署 URL ──────────────────────────
            live_url = self._extract_url(result.stdout, "Website URL" if self.prod else "Website draft URL")
            deploy_url = self._extract_url(result.stdout, "Unique Deploy URL")

            tlog.success(f"✅ [Netlify] 部署成功！URL: {live_url or deploy_url or '(未解析)'}")
            return {
                "status": "success",
                "site_id": self.site_id,
                "mode": "production" if self.prod else "draft",
                "url": live_url,
                "deploy_url": deploy_url,
                "message": result.stdout.strip()[-200:] if result.stdout else ""
            }

        except subprocess.TimeoutExpired:
            tlog.error("❌ [Netlify] 部署超时 (>300s)。")
            return {"status": "error", "message": "Netlify deploy timed out after 300 seconds."}
        except FileNotFoundError:
            tlog.info(f"💡 [Netlify] 未找到 CLI '{self.netlify_path}'，自动激活【原生零依赖 Direct API 直传引擎】...")
            return deploy_via_direct_api(self, bundle_path, metadata)
        except Exception as e:
            healed_err = self._add_autotherapy_suggestion(str(e))
            tlog.error(f"❌ [Netlify] 部署异常: {healed_err}")
            return {"status": "error", "message": healed_err}

    def _add_autotherapy_suggestion(self, err_msg: str) -> str:
        """💡 为 Netlify 错误注入友好免密授权物理自愈提示"""
        return add_autotherapy_suggestion(err_msg)

    def _has_cli(self) -> bool:
        """检测宿主机是否存在可用 Netlify CLI"""
        import shutil
        for bin_name in [self.netlify_path, os.path.join(os.getcwd(), "node_modules", ".bin", "netlify")]:
            if shutil.which(bin_name):
                return True
        return False

    def is_healthy(self) -> bool:
        """检查 Netlify 发布通道健康度（CLI 或 Direct API 双模就绪均视为可用）"""
        if self._has_cli():
            return True
        # 🛡️ [依赖自闭环] 宿主机即使未安装 Node/npm/CLI，配置完整即可走原生 Direct API 直传
        if self.site_id and self.auth_token:
            return True
        return False

    def validate_config(self) -> List[str]:
        """校验配置完整性，返回错误信息列表"""
        errors = []
        if not self.site_id:
            errors.append("缺少必填配置: site_id")
        if not self.auth_token:
            errors.append("缺少必填配置: auth_token")
        return errors

    def get_deploy_url(self) -> Optional[str]:
        """返回预期的部署 URL（基于 site_id 推导）"""
        if self.site_id:
            return f"https://{self.site_id}.netlify.app"
        return None

    # ==========================================
    # 内部实现
    # ==========================================

    def _resolve_executable(self) -> list:
        """自愈解析 Netlify CLI 可执行命令，优先使用指定路径，缺失时自动降级到 npx -y netlify-cli"""
        import shutil
        if shutil.which(self.netlify_path):
            return [self.netlify_path]
        local_bin = os.path.join(os.getcwd(), "node_modules", ".bin", "netlify")
        if os.path.exists(local_bin) and os.access(local_bin, os.X_OK):
            return [local_bin]
        return ["npx", "-y", "netlify-cli"]

    def _build_netlify_command(self, bundle_path: str, metadata: Dict[str, Any]) -> list:
        """组装 netlify deploy 命令参数"""
        cmd = self._resolve_executable() + [
            "deploy",
            f"--dir={bundle_path}",
            f"--site={self.site_id}",
            "--json"  # 以 JSON 格式输出结果
        ]

        if self.prod:
            cmd.append("--prod")

        if self.message:
            # 支持模板变量替换
            msg = self.message
            ts = metadata.get("timestamp", "")
            if ts:
                msg = msg.replace("{timestamp}", str(ts))
            cmd.append(f"--message={msg}")

        return cmd

    @staticmethod
    def _extract_url(stdout: str, label: str) -> Optional[str]:
        """
        从 Netlify CLI 的 stdout 中根据标签解析对应 URL。
        Netlify CLI 输出格式通常为:
          Website URL: https://xxx.netlify.app
          Unique Deploy URL: https://xxx--yyy.netlify.app
        JSON 模式下会以 JSON 结构输出。
        """
        if not stdout:
            return None

        # 优先尝试 JSON 解析 (--json 模式)
        try:
            import json
            data = json.loads(stdout)
            if label == "Website URL":
                return data.get("url") or data.get("ssl_url")
            elif label == "Unique Deploy URL":
                return data.get("deploy_url") or data.get("deploy_ssl_url")
            elif label == "Website draft URL":
                return data.get("deploy_url") or data.get("deploy_ssl_url")
        except (json.JSONDecodeError, ValueError):
            pass

        # 兜底：文本模式解析
        pattern = re.compile(rf'{re.escape(label)}:\s*(https://\S+)', re.IGNORECASE)
        match = pattern.search(stdout)
        return match.group(1) if match else None
