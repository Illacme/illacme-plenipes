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

    def upload(self, local_path: str) -> str:
        """
        物理上传本地相对图片至 GitHub 仓库
        """
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
