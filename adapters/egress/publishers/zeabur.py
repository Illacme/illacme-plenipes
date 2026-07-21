#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes — Zeabur Publisher Plugin
🚀 [V48.5]：通过 Git 增量推送与 Trigger Deploy Hook (Webhook POST) 独立触发 Zeabur 云端构建与静态站点发布。
"""

import os
import requests
import subprocess
from typing import Dict, Any, List

from core.adapters.egress.publishers.base import BasePublisher
from core.adapters.egress.publishers.git_helper import GitPushMixin
from core.utils.tracing import tlog


class ZeaburPublisher(BasePublisher, GitPushMixin):
    """
    🚀 [V48.5] Zeabur 发布插件
    """
    PLUGIN_ID = "zeabur"
    DISPLAY_NAME = "Zeabur"
    VERSION = "V2.0"
    DESCRIPTION = "独立部署静态站点至 Zeabur 并触发云端构建。"

    def __init__(self, config: Dict[str, Any], sys_config: Dict[str, Any] = None):
        super().__init__(config, sys_config)
        self.deploy_hook_url = config.get("deploy_hook_url", "")
        self.repo_url = config.get("repo_url", "")
        self.branch = config.get("branch", "main")
        self.token = config.get("token", "") or config.get("git_token", "")
        self.cname = config.get("cname", "")
        self.force_push = config.get("force_push", False)
        self.git_user_name = config.get("git_user_name", "Plenipes Bot")
        self.git_user_email = config.get("git_user_email", "bot@plenipes.press")

    def push(self, bundle_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        🚀 执行物理发布：先执行自包含 Git 推送（如配置），再向 Zeabur 的 Deploy Hook URL 发送 HTTP POST 请求。
        """
        if not self.deploy_hook_url:
            return {"status": "skipped", "message": "Zeabur deploy_hook_url not configured."}

        if not os.path.isdir(bundle_path):
            return {"status": "error", "message": f"Bundle path does not exist: {bundle_path}"}

        # ── 1. 若配置了 Git 仓库，则进行自包含 Git 部署 ──
        copied_count = 0
        if self.repo_url:
            tlog.info("🚀 [Zeabur] 检测到关联 Git 仓库，正在执行 Git 增量差分推送...")
            import tempfile
            work_dir = tempfile.mkdtemp(prefix="plenipes_zeabur_")
            try:
                # 克隆或初始化分支
                clone_ok = self._clone_target_branch(
                    work_dir, self.repo_url, self.token, self.branch,
                    self.git_user_name, self.git_user_email
                )
                if not clone_ok:
                    self._init_orphan_branch(
                        work_dir, self.repo_url, self.token, self.branch,
                        self.git_user_name, self.git_user_email
                    )

                # 清空工作区并差分复制
                self._clean_work_dir(work_dir, bundle_path)
                copied_count, skipped_count = self._copy_bundle(bundle_path, work_dir)

                # 注入 CNAME (如有)
                if self.cname:
                    cname_path = os.path.join(work_dir, "CNAME")
                    with open(cname_path, 'w') as f:
                        f.write(self.cname.strip())

                # 提交并推送
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                commit_msg = f"deploy(zeabur): {timestamp} (files: {copied_count})"
                pushed = self._commit_and_push(
                    work_dir, commit_msg, self.branch, self.repo_url, self.token,
                    force_push=self.force_push
                )
                if pushed:
                    tlog.success(f"🟢 [Zeabur] Git 增量推送成功！已推送 {copied_count} 个文件至 {self.branch} 分支。")
                else:
                    tlog.info("ℹ️ [Zeabur] Git 无变更需要推送。")
            except subprocess.CalledProcessError as e:
                err_msg = e.stderr or e.stdout or str(e)
                masked_err = self._mask_url_credentials(err_msg, self.token)
                suggested_err = self._add_autotherapy_suggestion(masked_err)
                tlog.error(f"❌ [Zeabur] Git 操作失败: {masked_err}")
                return {"status": "error", "message": f"Git operation failed: {suggested_err}"}
            except Exception as e:
                err_msg = str(e)
                masked_err = self._mask_url_credentials(err_msg, self.token)
                suggested_err = self._add_autotherapy_suggestion(masked_err)
                tlog.error(f"❌ [Zeabur] 部署异常: {masked_err}")
                return {"status": "error", "message": suggested_err}
            finally:
                import shutil
                shutil.rmtree(work_dir, ignore_errors=True)

        # ── 2. 触发 Webhook Deploy Hook ──
        tlog.info("🚀 [Zeabur] 正在向对端 Deploy Hook 发送部署信号...")
        try:
            proxy = self.get_proxy()
            proxies = {"http": proxy, "https": proxy} if proxy else None
            resp = requests.post(self.deploy_hook_url, proxies=proxies, timeout=10)
            resp.raise_for_status()
            tlog.success("✅ [Zeabur] 部署信号发送成功！已触发云端流水线编译。")
            return {
                "status": "success",
                "message": f"Zeabur deploy hook triggered. HTTP {resp.status_code}",
                "url": self.get_deploy_url(),
                "files": copied_count
            }
        except Exception as e:
            tlog.error(f"❌ [Zeabur] 触发部署失败: {e}")
            return {"status": "error", "message": f"Trigger deploy hook failed: {e}"}

    def validate_config(self) -> List[str]:
        errors = []
        if not self.deploy_hook_url:
            errors.append("缺少必填配置: deploy_hook_url")
        return errors
