#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes ImgBB Image Hosting Plugin
职责：利用 ImgBB 官方 API 将本地图片上传并获取全球永久直链。
🛡️ [SOP-01] 物理行数限制：保持在 300 行以内。
"""

import os
import requests
from typing import Dict, Any, Optional

from core.adapters.image_hosting.base import BaseImageHost
from core.utils.tracing import tlog


class ImgBBImageHost(BaseImageHost):
    """
    🚀 ImgBB 国际免维护图床物理通道
    """
    DISPLAY_NAME = "ImgBB 图床"
    DESCRIPTION = "ImgBB 国际知名公共图床，免复杂云存储配置，只需 1 个 API Key 即可永久托管。"
    VERSION = "V1.0"
    PLUGIN_ID = "imgbb"

    def __init__(self, config: Dict[str, Any], sys_tuning: Optional[Dict[str, Any]] = None):
        super().__init__(config, sys_tuning)
        self.api_key = self.config.get("api_key") or self.config.get("token") or ""
        self.endpoint = self.config.get("endpoint", "https://api.imgbb.com/1/upload").strip()
        self.proxy = self.config.get("proxy", "").strip()

    def upload(self, local_path: str) -> Optional[str]:
        """
        物理上传本地图片至 ImgBB
        """
        if not self.api_key:
            tlog.warning("⚠️ [图床-ImgBB] API Key 未配置，跳过上传。")
            return None

        if not os.path.exists(local_path):
            tlog.error(f"❌ [图床-ImgBB] 找不到待上传的本地图片文件: {local_path}")
            return None

        proxies = {}
        if self.proxy:
            proxies = {"http": self.proxy, "https": self.proxy}

        try:
            params = {"key": self.api_key}
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }

            with open(local_path, "rb") as f:
                files = {"image": f}
                resp = requests.post(
                    self.endpoint,
                    params=params,
                    files=files,
                    headers=headers,
                    proxies=proxies,
                    timeout=45
                )

            if resp.status_code == 200:
                res_data = resp.json()
                if res_data.get("success") and isinstance(res_data.get("data"), dict):
                    # 优先取 display_url 或 direct url
                    img_url = res_data["data"].get("url") or res_data["data"].get("display_url")
                    if img_url:
                        tlog.info(f"✅ [图床-ImgBB] 上传成功: {local_path} -> {img_url}")
                        return img_url
                tlog.warning(f"⚠️ [图床-ImgBB] 平台返回异常: {res_data}")
                return None
            else:
                tlog.warning(f"⚠️ [图床-ImgBB] HTTP 请求异常 ({resp.status_code}): {resp.text}")
                return None

        except Exception as e:
            tlog.error(f"🛑 [图床-ImgBB] 上传异常: {e}")
            return None
