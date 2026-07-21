#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes — Vercel Publisher Plugin
🚀 [V48.3]：通过 Vercel CLI 将站点资产物理同步至 Vercel Edge Network。

功能：
  1. 调用 `vercel deploy` 将构建产物上传至 Vercel
  2. 支持生产 (--prod) 与预览 (preview) 部署
  3. 通过 --token 参数安全传递认证凭据
  4. 支持组织级项目 (org_id) 绑定
  5. 自动解析部署 URL

配置示例 (config.yaml):
  vercel:
    enabled: true
    token: "ENC:xxxxxx"                 # 必填，支持加密
    project_name: "my-docs"             # 可选
    org_id: ""                          # 可选，组织 ID
    prod: true                          # 可选，默认 true
    vercel_path: "vercel"               # 可选
"""

import os
import re
import subprocess
from typing import Dict, Any, Optional, List

from core.adapters.egress.publishers.base import BasePublisher
from core.utils.tracing import tlog


class VercelPublisher(BasePublisher):
    """
    🚀 [V48.3] Vercel 发布插件
    通过 Vercel CLI 将静态站点产物部署至 Vercel Edge Network。
    """
    PLUGIN_ID = "vercel"
    DISPLAY_NAME = "Vercel"
    VERSION = "V3.5"
    DESCRIPTION = "通过 Vercel CLI 将站点资产物理同步至 Vercel Edge Network。"

    # ==========================================
    # 生命周期
    # ==========================================

    def __init__(self, config: Dict[str, Any], sys_config: Dict[str, Any] = None):
        super().__init__(config, sys_config)
        self.token = config.get("token", "")
        self.project_name = config.get("project_name", "")
        self.org_id = config.get("org_id", "")
        self.prod = config.get("prod", True)
        self.vercel_path = config.get("vercel_path", "vercel")

    # ==========================================
    # BasePublisher 契约实现
    # ==========================================

    def push(self, bundle_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        🚀 执行物理发布：通过 Vercel CLI 将 bundle_path 下的产物上传至 Vercel。

        执行流程：
          1. 校验配置完整性 (token 必填)
          2. 校验 bundle_path 物理存在性
          3. 组装 vercel deploy 命令
          4. 执行子进程 (超时 300s)
          5. 解析 stdout 提取部署 URL
          6. 返回标准化结果字典

        :param bundle_path: 本地构建产物目录（SSG 输出目录）
        :param metadata: 任务元数据
        :return: 发布结果字典
        """
        # ── 1. 前置校验 ──────────────────────────────────
        if not self.token:
            return {"status": "skipped", "message": "Vercel token not configured."}

        if not os.path.isdir(bundle_path):
            return {"status": "error", "message": f"Bundle path does not exist: {bundle_path}"}

        mode_label = "生产" if self.prod else "预览"
        tlog.info(f"🚀 [Vercel] 正在以 {mode_label} 模式部署...")

        try:
            # ── 2. 组装命令 ──────────────────────────────
            cmd = self._build_vercel_command(bundle_path)
            tlog.debug(f"📋 [Vercel] 执行命令: {self._sanitize_cmd_for_log(cmd)}")

            # ── 3. 准备环境变量 ──────────────────────────
            env = os.environ.copy()
            # 禁止交互式提示
            env["CI"] = "1"
            if self.org_id:
                env["VERCEL_ORG_ID"] = self.org_id

            # ── 4. 执行部署 ──────────────────────────────
            result = subprocess.run(
                cmd,
                capture_output=True, text=True,
                timeout=300,
                env=env
            )

            if result.returncode != 0:
                error_msg = result.stderr.strip() or result.stdout.strip() or "Unknown error"
                tlog.error(f"❌ [Vercel] 部署失败: {error_msg}")
                return {"status": "error", "message": f"Vercel deploy failed: {error_msg}"}

            # ── 5. 解析部署 URL ──────────────────────────
            # Vercel CLI 在成功时会将部署 URL 输出到 stdout
            deploy_url = self._extract_deploy_url(result.stdout)

            tlog.success(f"✅ [Vercel] 部署成功！URL: {deploy_url or '(未解析)'}")
            return {
                "status": "success",
                "project": self.project_name,
                "mode": "production" if self.prod else "preview",
                "url": deploy_url,
                "message": result.stdout.strip()[-200:] if result.stdout else ""
            }

        except subprocess.TimeoutExpired:
            tlog.error("❌ [Vercel] 部署超时 (>300s)。")
            return {"status": "error", "message": "Vercel deploy timed out after 300 seconds."}
        except FileNotFoundError:
            tlog.error(f"❌ [Vercel] 找不到 Vercel CLI: '{self.vercel_path}'")
            return {"status": "error", "message": f"Vercel CLI not found: '{self.vercel_path}'"}
        except Exception as e:
            tlog.error(f"❌ [Vercel] 部署异常: {e}")
            return {"status": "error", "message": str(e)}

    def is_healthy(self) -> bool:
        """检查 Vercel CLI 可用性与自愈"""
        self.ensure_npm_dependency("vercel")
        for bin_name in [self.vercel_path, os.path.join(os.getcwd(), "node_modules", ".bin", "vercel"), "npx"]:
            try:
                cmd = [bin_name, "--version"] if bin_name != "npx" else ["npx", "vercel", "--version"]
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

    # ==========================================
    # 内部实现
    # ==========================================

    def _build_vercel_command(self, bundle_path: str) -> list:
        """组装 vercel deploy 命令参数"""
        cmd = [
            self.vercel_path,
            "deploy",
            bundle_path,
            "--yes",  # 跳过确认提示
            f"--token={self.token}"
        ]

        if self.prod:
            cmd.append("--prod")

        if self.project_name:
            cmd.extend(["--name", self.project_name])

        return cmd

    @staticmethod
    def _sanitize_cmd_for_log(cmd: list) -> str:
        """脱敏命令行日志（隐藏 Token）"""
        sanitized = []
        for arg in cmd:
            if arg.startswith("--token="):
                sanitized.append("--token=***")
            else:
                sanitized.append(arg)
        return " ".join(sanitized)

    @staticmethod
    def _extract_deploy_url(stdout: str) -> Optional[str]:
        """
        从 Vercel CLI stdout 中解析部署 URL。
        Vercel CLI 成功部署后通常直接输出 URL (如 https://xxx.vercel.app)。
        """
        if not stdout:
            return None

        # Vercel CLI 的 stdout 通常最后一行就是部署 URL
        lines = stdout.strip().split('\n')
        for line in reversed(lines):
            line = line.strip()
            if line.startswith("https://"):
                return line

        # 兜底正则匹配
        url_pattern = re.compile(r'(https://[\w\-\.]+\.vercel\.app\S*)', re.IGNORECASE)
        match = url_pattern.search(stdout)
        if match:
            return match.group(1)

        # 最终兜底：匹配任何 https URL
        fallback_pattern = re.compile(r'(https://\S+)')
        match = fallback_pattern.search(stdout)
        return match.group(1) if match else None
