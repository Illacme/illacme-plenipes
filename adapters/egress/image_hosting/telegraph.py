#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes Telegraph Image Hosting Plugin
职责：利用 Telegraph upload API 将本地文稿相对图片匿名上传至 Telegraph 存储。
🛡️ [SOP-01] 物理行数限制：保持在 300 行以内。
"""

import os
import requests
from typing import Dict, Any

from core.adapters.image_hosting.base import BaseImageHost
from core.utils.tracing import tlog

class TelegraphImageHost(BaseImageHost):
    """
    🚀 Telegraph 匿名免配图床插件 (Telegra.ph)
    """
    PLUGIN_ID = "telegraph"

    def __init__(self, config: Dict[str, Any], sys_tuning: Dict[str, Any] = None):
        super().__init__(config, sys_tuning)
        # 允许通过配置自定义 telegraph 域名 (例如反代域名)
        self.endpoint = self.config.get("endpoint", "https://telegra.ph").rstrip("/")

    def upload(self, local_path: str) -> str:
        """
        物理上传本地相对图片至 Telegraph
        """
        if not os.path.exists(local_path):
            tlog.error(f"❌ 找不到待上传的本地图片文件: {local_path}")
            return None

        try:
            url = f"{self.endpoint}/upload"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }

            with open(local_path, "rb") as f:
                files = {"file": f}
                resp = requests.post(url, files=files, headers=headers, timeout=30)

            if resp.status_code == 200:
                res_data = resp.json()
                if isinstance(res_data, list) and len(res_data) > 0:
                    src = res_data[0].get("src")
                    if src:
                        img_url = f"{self.endpoint}{src}"
                        tlog.info(f"✅ [图床-Telegraph] 上传成功: {local_path} -> {img_url}")
                        return img_url
                    
                # 错误处理
                tlog.warning(f"⚠️ [图床-Telegraph] 平台返回格式未知: {res_data}")
                return None
            else:
                tlog.warning(f"⚠️ [图床-Telegraph] HTTP 请求异常 ({resp.status_code}): {resp.text}")
                return None

        except Exception as e:
            tlog.error(f"🛑 [图床-Telegraph] 上传异常: {e}")
            return None
