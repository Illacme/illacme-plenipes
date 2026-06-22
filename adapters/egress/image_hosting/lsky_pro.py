#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes Lsky Pro (兰空图床) Image Hosting Plugin
职责：上传本地图片至自建或第三方的兰空图床服务 (Lsky Pro)。
🛡️ [SOP-01] 物理行数限制：保持在 300 行以内。
"""

import os
import requests
from typing import Dict, Any

from core.adapters.image_hosting.base import BaseImageHost
from core.utils.tracing import tlog

class LskyProImageHost(BaseImageHost):
    """
    🚀 兰空图床 (Lsky Pro) 物理驱动插件
    """
    DISPLAY_NAME = "兰空图床"
    DESCRIPTION = "自建或第三方兰空图床 (Lsky Pro) 驱动，支持多相册、多存储策略分流。"
    VERSION = "V1.0"
    PLUGIN_ID = "lsky_pro"

    def __init__(self, config: Dict[str, Any], sys_tuning: Dict[str, Any] = None):
        super().__init__(config, sys_tuning)
        self.endpoint = self.config.get("endpoint", "").strip().rstrip("/")
        self.token = self.config.get("token", "").strip()
        self.strategy_id = self.config.get("strategy_id", "")
        self.album_id = self.config.get("album_id", "")

    def upload(self, local_path: str) -> str:
        """
        物理上传本地图片至兰空图床
        """
        if not self.endpoint or not self.token:
            tlog.warning("⚠️ 兰空图床 Endpoint 或 API Token 未配置，跳过上传。")
            return None

        if not os.path.exists(local_path):
            tlog.error(f"❌ 找不到待上传的本地图片文件: {local_path}")
            return None

        try:
            # 拼接 Lsky Pro API v1 上传地址
            upload_url = f"{self.endpoint}/api/v1/upload"
            
            # 鉴权 Token (Bearer)
            headers = {
                "Authorization": f"Bearer {self.token}" if not self.token.startswith("Bearer ") else self.token,
                "Accept": "application/json",
                "User-Agent": "Illacme-Plenipes-Client"
            }

            # 表单参数
            data = {}
            if self.strategy_id:
                data["strategy_id"] = str(self.strategy_id)
            if self.album_id:
                data["album_id"] = str(self.album_id)

            with open(local_path, "rb") as f:
                files = {"file": f}
                resp = requests.post(upload_url, data=data, files=files, headers=headers, timeout=45)

            if resp.status_code == 200:
                res_data = resp.json()
                if res_data.get("status"):
                    # 成功返回 url，结构为 res_data["data"]["links"]["url"]
                    img_url = res_data.get("data", {}).get("links", {}).get("url")
                    if img_url:
                        tlog.info(f"✅ [图床-兰空] 上传成功: {local_path} -> {img_url}")
                        return img_url
                tlog.warning(f"⚠️ [图床-兰空] 平台上传失败: {res_data.get('message') or res_data}")
                return None
            else:
                tlog.warning(f"⚠️ [图床-兰空] HTTP 请求异常 ({resp.status_code}): {resp.text}")
                return None

        except Exception as e:
            tlog.error(f"🛑 [图床-兰空] 上传发生异常: {e}")
            return None
