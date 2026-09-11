#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes GitHub Image Hosting Plugin
职责：利用 GitHub Contents API 将本地文稿相对图片上传至指定 GitHub 仓库。
🛡️ [SOP-01] 物理行数限制：保持在 300 行以内。
"""

import os
import base64
import requests
import hashlib
from typing import Dict, Any

from core.adapters.image_hosting.base import BaseImageHost
from core.utils.tracing import tlog

class GitHubImageHost(BaseImageHost):
    """
    🚀 GitHub 仓库图床插件
    """
    PLUGIN_ID = "github"

    def __init__(self, config: Dict[str, Any], sys_tuning: Dict[str, Any] = None):
        super().__init__(config, sys_tuning)
        self.repo = self.config.get("repo", "")
        self.branch = self.config.get("branch", "main")
        self.token = self.config.get("token", "")
        self.path = self.config.get("path", "images").strip("/")
        self.cdn_url = self.config.get("cdn_url", "").rstrip("/")

    def _resolve_repo(self):
        """🚀 [V114.0] 零配置自动推导：若未显式指定 repo，优先继承 GitHub Pages 已绑定的仓库"""
        if self.repo:
            return self.repo
        if not self.token:
            return ""

        import re
        # 1. 尝试从上下文中的 GitHub Pages 配置提取
        pub_ctrl = self.sys_tuning.get("publish_control", {})
        if hasattr(pub_ctrl, "direct_upload"):
            direct_upload = getattr(pub_ctrl, "direct_upload", {})
        elif isinstance(pub_ctrl, dict):
            direct_upload = pub_ctrl.get("direct_upload", {})
        else:
            direct_upload = {}

        gh_pages = direct_upload.get("github_pages", {}) if isinstance(direct_upload, dict) else getattr(direct_upload, "github_pages", {})
        if hasattr(gh_pages, "__dict__"):
            gh_pages = gh_pages.__dict__
        repo_url = gh_pages.get("repo_url", "") if isinstance(gh_pages, dict) else ""

        if repo_url and "github.com" in repo_url:
            m = re.search(r'github\.com[/:]([^/]+/[^/]+?)(?:\.git)?$', repo_url)
            if m:
                self.repo = m.group(1)
                tlog.info(f"✨ [图床-GitHub] 自动继承 GitHub Pages 仓库: {self.repo}")
                return self.repo

        # 2. 通过 GitHub API /user 动态推导用户空间仓库
        try:
            resp = requests.get(
                "https://api.github.com/user",
                headers={"Authorization": f"token {self.token}", "User-Agent": "Illacme-Plenipes-Client"},
                timeout=8
            )
            if resp.status_code == 200:
                user_login = resp.json().get("login")
                if user_login:
                    self.repo = f"{user_login}/illacme-press"
                    tlog.info(f"✨ [图床-GitHub] 零配置自动推导图床仓库: {self.repo}")
                    return self.repo
        except Exception:
            pass

        return ""

    def upload(self, local_path: str) -> str:
        """
        物理上传本地相对图片至 GitHub 仓库
        """
        if not self.repo:
            self._resolve_repo()

        if not self.repo or not self.token:
            tlog.warning("⚠️ GitHub 图床凭证/仓库未配置，跳过上传。")
            return None

        if not os.path.exists(local_path):
            tlog.error(f"❌ 找不到待上传的本地图片文件: {local_path}")
            return None

        try:
            filename = os.path.basename(local_path)
            # 计算 md5 摘要去重
            hasher = hashlib.md5()
            with open(local_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096 * 1024), b""):
                    hasher.update(chunk)
            file_hash = hasher.hexdigest()
            ext = os.path.splitext(local_path)[1].lower()
            name_base = os.path.splitext(filename)[0]
            actual_name = f"{name_base}_{file_hash[:8]}{ext}"

            dest_path = f"{self.path}/{actual_name}" if self.path else actual_name
            url = f"https://api.github.com/repos/{self.repo}/contents/{dest_path}"

            with open(local_path, "rb") as f:
                content_b64 = base64.b64encode(f.read()).decode("utf-8")

            payload = {
                "message": f"upload image: {actual_name}",
                "content": content_b64,
                "branch": self.branch
            }

            headers = {
                "Authorization": f"token {self.token}",
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "Illacme-Plenipes-Client"
            }

            resp = requests.put(url, json=payload, headers=headers, timeout=30)
            if resp.status_code in (201, 200):
                tlog.info(f"✅ [图床-GitHub] 上传成功: {local_path} -> {dest_path}")
                if self.cdn_url:
                    return f"{self.cdn_url}/{dest_path}"
                return f"https://cdn.jsdelivr.net/gh/{self.repo}@{self.branch}/{dest_path}"
            elif resp.status_code == 422 and "already exists" in resp.text:
                tlog.info("ℹ️ [图床-GitHub] 图片已存在，使用默认 CDN 链接。")
                if self.cdn_url:
                    return f"{self.cdn_url}/{dest_path}"
                return f"https://cdn.jsdelivr.net/gh/{self.repo}@{self.branch}/{dest_path}"
            else:
                tlog.warning(f"⚠️ [图床-GitHub] 上传响应异常 ({resp.status_code}): {resp.text}")
                return None

        except Exception as e:
            tlog.error(f"🛑 [图床-GitHub] 上传异常: {e}")
            return None
