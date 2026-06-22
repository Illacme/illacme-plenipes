#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes SM.MS Image Hosting Plugin
职责：利用 SM.MS API v2 将本地文稿相对图片上传至 SM.MS 平台。
🛡️ [SOP-01] 物理行数限制：保持在 300 行以内。
"""

import os
import requests
from typing import Dict, Any

from core.adapters.image_hosting.base import BaseImageHost
from core.utils.tracing import tlog

class SmMsImageHost(BaseImageHost):
    """
    🚀 SM.MS 图床插件
    """
    PLUGIN_ID = "sm_ms"

    def __init__(self, config: Dict[str, Any], sys_tuning: Dict[str, Any] = None):
        super().__init__(config, sys_tuning)
        self.token = self.config.get("token", "")

    def upload(self, local_path: str) -> str:
        """
        物理上传本地相对图片至 SM.MS
        """
        if not self.token:
            tlog.warning("⚠️ SM.MS 图床 Secret Token 未配置，跳过上传。")
            return None

        if not os.path.exists(local_path):
            tlog.error(f"❌ 找不到待上传的本地图片文件: {local_path}")
            return None

        try:
            url = "https://sm.ms/api/v2/upload"
            headers = {
                "Authorization": self.token,
                "User-Agent": "Illacme-Plenipes-Client"
            }

            with open(local_path, "rb") as f:
                files = {"smfile": f}
                resp = requests.post(url, files=files, headers=headers, timeout=45)

            if resp.status_code == 200:
                res_data = resp.json()
                if res_data.get("success"):
                    img_url = res_data.get("data", {}).get("url")
                    tlog.info(f"✅ [图床-SM.MS] 上传成功: {local_path} -> {img_url}")
                    return img_url
                elif res_data.get("code") == "image_repeated":
                    img_url = res_data.get("images")
                    tlog.info(f"ℹ️ [图床-SM.MS] 检测到重复图片，已自动重用链接: {img_url}")
                    return img_url
                else:
                    tlog.warning(f"⚠️ [图床-SM.MS] 平台返回异常: {res_data.get('message')}")
                    return None
            else:
                tlog.warning(f"⚠️ [图床-SM.MS] HTTP 请求异常 ({resp.status_code}): {resp.text}")
                return None

        except Exception as e:
            tlog.error(f"🛑 [图床-SM.MS] 上传异常: {e}")
            return None
