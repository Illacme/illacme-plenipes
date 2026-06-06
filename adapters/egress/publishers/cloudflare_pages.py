#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes — Cloudflare Pages Publisher Plugin
🚀 [V48.3]：通过 Wrangler CLI 将站点资产物理同步至 Cloudflare Edge 网络。

功能：
  1. 调用 `wrangler pages deploy` 将构建产物上传至 Cloudflare Pages
  2. 支持生产 (production) 与预览 (preview) 分支切换
  3. 支持多账号环境 (account_id 指定)
  4. 支持自定义 Wrangler CLI 路径
  5. 自动解析部署 URL

配置示例 (config.yaml):
  cloudflare_pages:
    enabled: true
    project_name: "my-docs-site"        # 必填
    branch: "production"                 # 可选，默认 production
    account_id: ""                       # 可选，多账号环境
    wrangler_path: "wrangler"            # 可选，自定义 CLI 路径
"""

import os
import re
import subprocess
from typing import Dict, Any, Optional, List

from core.adapters.egress.publishers.base import BasePublisher
from core.utils.tracing import tlog


class CloudflarePagesPublisher(BasePublisher):
    """
    🚀 [V48.3] Cloudflare Pages 发布插件
    通过 Wrangler CLI 将静态站点产物部署至 Cloudflare Edge 网络。
    """
    PLUGIN_ID = "cloudflare_pages"
    DISPLAY_NAME = "Cloudflare Pages"
    VERSION = "V3.5"
    DESCRIPTION = "通过 Wrangler 协议将站点资产物理同步至 Cloudflare Edge 网络。"

    # ==========================================
    # 生命周期
    # ==========================================

    def __init__(self, config: Dict[str, Any], sys_config: Dict[str, Any] = None):
        super().__init__(config, sys_config)
        self.project_name = config.get("project_name", "")
        self.branch = config.get("branch", "production")
        self.account_id = config.get("account_id", "")
        self.wrangler_path = config.get("wrangler_path", "wrangler")

    # ==========================================
    # BasePublisher 契约实现
    # ==========================================

    def push(self, bundle_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        🚀 执行物理发布：通过 Wrangler CLI 将 bundle_path 下的产物上传至 Cloudflare Pages。

        执行流程：
          1. 校验配置完整性 (project_name 必填)
          2. 校验 bundle_path 物理存在性
          3. 组装 wrangler pages deploy 命令
          4. 执行子进程 (超时 300s)
          5. 解析 stdout 提取部署 URL
          6. 返回标准化结果字典

        :param bundle_path: 本地构建产物目录（SSG 输出目录）
        :param metadata: 任务元数据
        :return: 发布结果字典
        """
        # ── 1. 前置校验 ──────────────────────────────────
        if not self.project_name:
            return {"status": "skipped", "message": "Cloudflare Pages project_name not configured."}

        if not os.path.isdir(bundle_path):
            return {"status": "error", "message": f"Bundle path does not exist: {bundle_path}"}

        tlog.info(f"🚀 [Cloudflare Pages] 正在部署至项目 '{self.project_name}' ({self.branch})...")

        try:
            # ── 2. 组装命令 ──────────────────────────────
            cmd = self._build_wrangler_command(bundle_path)
            tlog.debug(f"📋 [Cloudflare Pages] 执行命令: {' '.join(cmd)}")

            # ── 3. 执行部署 ──────────────────────────────
            result = subprocess.run(
                cmd,
                capture_output=True, text=True,
                timeout=300
            )

            if result.returncode != 0:
                error_msg = result.stderr.strip() or result.stdout.strip() or "Unknown error"
                tlog.error(f"❌ [Cloudflare Pages] Wrangler 部署失败: {error_msg}")
                return {"status": "error", "message": f"Wrangler deploy failed: {error_msg}"}

            # ── 4. 解析部署 URL ──────────────────────────
            deploy_url = self._extract_deploy_url(result.stdout)

            tlog.success(f"✅ [Cloudflare Pages] 部署成功！URL: {deploy_url or '(未解析)'}")
            return {
                "status": "success",
                "project": self.project_name,
                "branch": self.branch,
                "url": deploy_url,
                "message": result.stdout.strip()[-200:] if result.stdout else ""
            }

        except subprocess.TimeoutExpired:
            tlog.error("❌ [Cloudflare Pages] Wrangler 部署超时 (>300s)。")
            return {"status": "error", "message": "Wrangler deploy timed out after 300 seconds."}
        except FileNotFoundError:
            tlog.error(f"❌ [Cloudflare Pages] 找不到 Wrangler CLI: '{self.wrangler_path}'")
            return {"status": "error", "message": f"Wrangler CLI not found: '{self.wrangler_path}'"}
        except Exception as e:
            tlog.error(f"❌ [Cloudflare Pages] 部署异常: {e}")
            return {"status": "error", "message": str(e)}

    def is_healthy(self) -> bool:
        """检查 Wrangler CLI 可用性"""
        try:
            result = subprocess.run(
                [self.wrangler_path, "--version"],
                capture_output=True, text=True, timeout=10
            )
            return result.returncode == 0
        except Exception:
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

    # ==========================================
    # 内部实现
    # ==========================================

    def _build_wrangler_command(self, bundle_path: str) -> list:
        """组装 wrangler pages deploy 命令参数"""
        cmd = [
            self.wrangler_path,
            "pages", "deploy",
            bundle_path,
            "--project-name", self.project_name,
            "--branch", self.branch
        ]

        if self.account_id:
            cmd.extend(["--account-id", self.account_id])

        return cmd

    @staticmethod
    def _extract_deploy_url(stdout: str) -> Optional[str]:
        """
        从 Wrangler stdout 中解析部署 URL。
        Wrangler 输出通常包含形如 "https://xxx.pages.dev" 的 URL。
        """
        if not stdout:
            return None

        # 匹配 Wrangler 输出中的 pages.dev URL
        url_pattern = re.compile(r'(https://[\w\-]+\.pages\.dev\S*)', re.IGNORECASE)
        match = url_pattern.search(stdout)
        if match:
            return match.group(1)

        # 兜底：匹配任何 https URL
        fallback_pattern = re.compile(r'(https://\S+)')
        match = fallback_pattern.search(stdout)
        return match.group(1) if match else None
