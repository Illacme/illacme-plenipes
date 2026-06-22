#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes Imgur Image Hosting Plugin
职责：利用 Imgur API v3 将本地文稿相对图片上传至 Imgur 平台。
🛡️ [SOP-01] 物理行数限制：保持在 300 行以内。
"""

import os
import requests
from typing import Dict, Any

from core.adapters.image_hosting.base import BaseImageHost
from core.utils.tracing import tlog

class ImgurImageHost(BaseImageHost):
    """
    🚀 Imgur 图床插件
    """
    PLUGIN_ID = "imgur"

    def __init__(self, config: Dict[str, Any], sys_tuning: Dict[str, Any] = None):
        super().__init__(config, sys_tuning)
        self.client_id = self.config.get("client_id", "")
        self.token = self.config.get("token", "")

    def upload(self, local_path: str) -> str:
        """
        物理上传本地相对图片至 Imgur
        """
        if not self.client_id and not self.token:
            tlog.warning("⚠️ Imgur 图床 Client ID 与 Access Token 均未配置，跳过上传。")
            return None

        if not os.path.exists(local_path):
            tlog.error(f"❌ 找不到待上传的本地图片文件: {local_path}")
            return None

        try:
            url = "https://api.imgur.com/3/image"
            
            # 优先使用 token (OAuth2 Bearer)，其次使用 Client-ID (Anonymous)
            if self.token:
                auth_header = f"Bearer {self.token}"
            else:
                auth_header = f"Client-ID {self.client_id}"

            headers = {
                "Authorization": auth_header,
                "User-Agent": "Illacme-Plenipes-Client"
            }

            with open(local_path, "rb") as f:
                files = {"image": f}
                resp = requests.post(url, files=files, headers=headers, timeout=60)

            if resp.status_code == 200:
                res_data = resp.json()
                if res_data.get("success"):
                    img_url = res_data.get("data", {}).get("link")
                    tlog.info(f"✅ [图床-Imgur] 上传成功: {local_path} -> {img_url}")
                    return img_url
                else:
                    tlog.warning(f"⚠️ [图床-Imgur] 平台返回异常: {res_data.get('data', {}).get('error')}")
                    return None
            else:
                tlog.warning(f"⚠️ [图床-Imgur] HTTP 请求异常 ({resp.status_code}): {resp.text}")
                return None

        except Exception as e:
            tlog.error(f"🛑 [图床-Imgur] 上传异常: {e}")
            return None
