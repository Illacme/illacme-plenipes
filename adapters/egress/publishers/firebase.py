#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes — Firebase Hosting Publisher Plugin
🚀 [V24.0]：通过 Firebase CLI (firebase-tools) 将静态站点物理部署至 Firebase Hosting。
"""

import os
import shutil
import subprocess
import tempfile
import json
from typing import Dict, Any, List

from core.adapters.egress.publishers.base import BasePublisher
from core.utils.tracing import tlog


class FirebaseHostingPublisher(BasePublisher):
    """
    🚀 [V24.0] Firebase Hosting 发布插件
    """
    PLUGIN_ID = "firebase"
    DISPLAY_NAME = "Firebase Hosting"
    VERSION = "V1.0"
    DESCRIPTION = "通过 Firebase CLI 将站点资产物理部署至 Google Firebase Hosting。"

    def __init__(self, config: Dict[str, Any], sys_config: Dict[str, Any] = None):
        super().__init__(config, sys_config)
        self.project = config.get("project", "")
        self.token = config.get("token", "") or config.get("firebase_token", "")
        self.site = config.get("site", "")
        self.firebase_path = config.get("firebase_path", "firebase")
        self.deploy_timeout = int(config.get("deploy_timeout", 300))

    def _mask_token(self, text: str) -> str:
        """
        🔒 抹除文本中可能夹带的明文 Firebase Token。
        """
        if not text:
            return text
        if self.token and len(self.token) > 4:
            return text.replace(self.token, "***")
        return text

    def push(self, bundle_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        🚀 执行物理发布：通过 Firebase deploy 命令将 bundle_path 下的静态产物部署至 Firebase Hosting。
        """
        if not self.project:
            return {"status": "skipped", "message": "Firebase project not configured."}

        if not os.path.isdir(bundle_path):
            return {"status": "error", "message": f"Bundle path does not exist: {bundle_path}"}

        # 确保 Wrangler 类似的依赖环境就绪
        self.ensure_npm_dependency("firebase-tools")

        temp_dir = tempfile.mkdtemp(prefix="plenipes_firebase_")
        try:
            # 建立临时沙盒，拷贝 bundle_path 到子目录 public，并写入 firebase.json
            public_dir = os.path.join(temp_dir, "public")
            shutil.copytree(bundle_path, public_dir)

            fb_json_path = os.path.join(temp_dir, "firebase.json")
            fb_config = {
                "hosting": {
                    "public": "public",
                    "ignore": [
                        "firebase.json",
                        "**/.*",
                        "**/node_modules/**"
                    ]
                }
            }
            if self.site:
                fb_config["hosting"]["site"] = self.site

            with open(fb_json_path, "w", encoding="utf-8") as f:
                json.dump(fb_config, f, indent=2)

            # 组装命令，若支持本地 npx 执行则使用 npx firebase
            cmd = ["npx", "firebase", "deploy", "--only", "hosting", "--project", self.project]

            env = os.environ.copy()
            # 过滤 Token 占位符
            token = self.token
            if token and not any(ph in token.lower() for ph in ["your_token", "placeholder", "undefined"]):
                env["FIREBASE_TOKEN"] = token

            tlog.info(f"🚀 [Firebase] 正在以 npx 方式启动部署至 Firebase 项目 '{self.project}'...")
            
            proxy = self.get_proxy()
            if proxy:
                tlog.info(f"🔌 [Firebase] 检测到代理配置，正在强制注入子进程: {proxy}")
                env["HTTP_PROXY"] = proxy
                env["HTTPS_PROXY"] = proxy
                env["http_proxy"] = proxy
                env["https_proxy"] = proxy
            
            result = subprocess.run(
                cmd,
                cwd=temp_dir,
                env=env,
                capture_output=True, text=True,
                timeout=self.deploy_timeout
            )

            if result.returncode != 0:
                masked_stdout = self._mask_token(result.stdout or "")
                masked_stderr = self._mask_token(result.stderr or "")
                tlog.error(f"❌ [Firebase] 部署失败 (Exit code {result.returncode})。")
                if masked_stdout:
                    tlog.error(f"📋 Captured Stdout:\n{masked_stdout}")
                if masked_stderr:
                    tlog.error(f"📋 Captured Stderr:\n{masked_stderr}")

                err_msg = masked_stderr.strip() or masked_stdout.strip() or "Unknown error"
                return {"status": "error", "message": f"Firebase deploy failed: {err_msg}"}

            deploy_url = f"https://{self.project}.web.app"
            if self.site:
                deploy_url = f"https://{self.site}.web.app"

            tlog.success(f"✅ [Firebase] 部署成功！URL: {deploy_url}")
            return {
                "status": "success",
                "project": self.project,
                "url": deploy_url,
                "message": result.stdout.strip()[-200:] if result.stdout else ""
            }

        except subprocess.TimeoutExpired as e:
            stdout_str = e.stdout or ""
            stderr_str = e.stderr or ""
            masked_stdout = self._mask_token(stdout_str)
            masked_stderr = self._mask_token(stderr_str)
            tlog.error(f"❌ [Firebase] 部署超时 (>{self.deploy_timeout}s)。")
            if masked_stdout:
                tlog.error(f"📋 Captured Stdout:\n{masked_stdout}")
            if masked_stderr:
                tlog.error(f"📋 Captured Stderr:\n{masked_stderr}")
            return {
                "status": "error",
                "message": (
                    f"Firebase deploy timed out after {self.deploy_timeout} seconds.\n\n"
                    f"📋 Stdout:\n{masked_stdout}\n\n"
                    f"📋 Stderr:\n{masked_stderr}"
                )
            }
        except Exception as e:
            tlog.error(f"❌ [Firebase] 部署异常: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def is_healthy(self) -> bool:
        self.ensure_npm_dependency("firebase-tools")
        try:
            res = subprocess.run(["npx", "firebase", "--version"], capture_output=True, text=True, timeout=15)
            return res.returncode == 0
        except Exception:
            return False

    def validate_config(self) -> List[str]:
        errors = []
        if not self.project:
            errors.append("缺少必填配置: project")
        return errors
