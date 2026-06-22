#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes Superbed (聚合图床) Image Hosting Plugin
职责：利用聚合图床 API 将本地图片上传。
🛡️ [SOP-01] 物理行数限制：保持在 300 行以内。
"""

import os
import requests
from typing import Dict, Any

from core.adapters.image_hosting.base import BaseImageHost
from core.utils.tracing import tlog

class SuperbedImageHost(BaseImageHost):
    """
    🚀 聚合图床 (Superbed) 图床插件
    """
    DISPLAY_NAME = "聚合图床"
    DESCRIPTION = "聚合图床 (Superbed) 物理通道，支持高速国内 CDN 加速与稳定分发。"
    VERSION = "V1.0"
    PLUGIN_ID = "superbed"

    def __init__(self, config: Dict[str, Any], sys_tuning: Dict[str, Any] = None):
        super().__init__(config, sys_tuning)
        self.token = self.config.get("token", "")
        self.endpoint = self.config.get("endpoint", "https://api.superbed.cn/upload").strip()

    def upload(self, local_path: str) -> str:
        """
        物理上传本地图片至聚合图床
        """
        if not self.token:
            tlog.warning("⚠️ 聚合图床 API Token 未配置，跳过上传。")
            return None

        if not os.path.exists(local_path):
            tlog.error(f"❌ 找不到待上传的本地图片文件: {local_path}")
            return None

        try:
            # 聚合图床标准协议：POST https://api.superbed.cn/upload
            # 表单字段包含：token，file
            data = {"token": self.token}
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }

            with open(local_path, "rb") as f:
                files = {"file": f}
                resp = requests.post(self.endpoint, data=data, files=files, headers=headers, timeout=45)

            if resp.status_code == 200:
                res_data = resp.json()
                # 聚合图床成功时 err == 0 或 0 为整型/字符
                if str(res_data.get("err")) == "0":
                    img_url = res_data.get("url")
                    if img_url:
                        tlog.info(f"✅ [图床-聚合图床] 上传成功: {local_path} -> {img_url}")
                        return img_url
                tlog.warning(f"⚠️ [图床-聚合图床] 平台返回异常: {res_data.get('msg') or res_data}")
                return None
            else:
                tlog.warning(f"⚠️ [图床-聚合图床] HTTP 请求异常 ({resp.status_code}): {resp.text}")
                return None

        except Exception as e:
            tlog.error(f"🛑 [图床-聚合图床] 上传发生异常: {e}")
            return None
