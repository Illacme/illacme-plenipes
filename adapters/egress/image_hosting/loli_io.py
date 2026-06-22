#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes Loli.io (路过图床) Image Hosting Plugin
职责：利用路过图床/img.lol API 将本地图片上传。
🛡️ [SOP-01] 物理行数限制：保持在 300 行以内。
"""

import os
import requests
from typing import Dict, Any

from core.adapters.image_hosting.base import BaseImageHost
from core.utils.tracing import tlog

class LoliIoImageHost(BaseImageHost):
    """
    🚀 路过图床 (loli.io) 图床插件
    """
    DISPLAY_NAME = "路过图床"
    DESCRIPTION = "路过图床 (loli.io) 免置云存储托管服务，国内网络访问极佳。"
    VERSION = "V1.0"
    PLUGIN_ID = "loli_io"

    def __init__(self, config: Dict[str, Any], sys_tuning: Dict[str, Any] = None):
        super().__init__(config, sys_tuning)
        self.token = self.config.get("token", "")
        # 支持自定义接口 URL 以免路过图床域名更换或反代
        self.endpoint = self.config.get("endpoint", "https://img.lol/api/v1/upload").strip()

    def upload(self, local_path: str) -> str:
        """
        物理上传本地图片至路过图床
        """
        if not self.token:
            tlog.warning("⚠️ 路过图床 API Token 未配置，跳过上传。")
            return None

        if not os.path.exists(local_path):
            tlog.error(f"❌ 找不到待上传的本地图片文件: {local_path}")
            return None

        try:
            # 常见基于 Chevereto/ImgTP 的接口契约
            headers = {
                "X-API-Token": self.token,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }

            with open(local_path, "rb") as f:
                # Chevereto 使用 source 字段上传文件，或者 file 字段
                files = {"source": f}
                resp = requests.post(self.endpoint, files=files, headers=headers, timeout=45)

            if resp.status_code == 200:
                res_data = resp.json()
                # 兼容不同系统的 JSON 响应格式
                if res_data.get("status") == 200 or res_data.get("success"):
                    # Chevereto 格式: res_data["image"]["url"]
                    # 或者 img.lol 格式: res_data["data"]["url"]
                    img_url = (res_data.get("image", {}).get("url") or
                               res_data.get("data", {}).get("url") or
                               res_data.get("url"))
                    if img_url:
                        tlog.info(f"✅ [图床-路过图床] 上传成功: {local_path} -> {img_url}")
                        return img_url
                tlog.warning(f"⚠️ [图床-路过图床] 平台返回异常: {res_data}")
                return None
            else:
                tlog.warning(f"⚠️ [图床-路过图床] HTTP 请求异常 ({resp.status_code}): {resp.text}")
                return None

        except Exception as e:
            tlog.error(f"🛑 [图床-路过图床] 上传发生异常: {e}")
            return None
