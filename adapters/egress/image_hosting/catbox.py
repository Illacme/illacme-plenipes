#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes Catbox Image Hosting Plugin
职责：利用 Catbox API 将本地图片上传并获取无防盗链永久直链。
🛡️ [SOP-01] 物理行数限制：保持在 300 行以内。
"""

import os
import requests
from typing import Dict, Any, Optional

from core.adapters.image_hosting.base import BaseImageHost
from core.utils.tracing import tlog


class CatboxImageHost(BaseImageHost):
    """
    🚀 Catbox 极客永久图床物理通道
    """
    DISPLAY_NAME = "Catbox 图床"
    DESCRIPTION = "极客圈老牌永久直链图床，单文件上限 200MB，支持匿名直接上传或绑定 Userhash。"
    VERSION = "V1.0"
    PLUGIN_ID = "catbox"

    def __init__(self, config: Dict[str, Any], sys_tuning: Optional[Dict[str, Any]] = None):
        super().__init__(config, sys_tuning)
        # userhash 为可选参数；不填时为公共匿名上传
        self.userhash = self.config.get("userhash") or self.config.get("token") or ""
        self.endpoint = self.config.get("endpoint", "https://catbox.moe/user/api.php").strip()
        self.proxy = self.config.get("proxy", "").strip()

    def upload(self, local_path: str) -> Optional[str]:
        """
        物理上传本地图片至 Catbox
        """
        if not os.path.exists(local_path):
            tlog.error(f"❌ [图床-Catbox] 找不到待上传的本地图片文件: {local_path}")
            return None

        proxies = {}
        if self.proxy:
            proxies = {"http": self.proxy, "https": self.proxy}

        try:
            data = {"reqtype": "fileupload"}
            if self.userhash:
                data["userhash"] = self.userhash

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }

            with open(local_path, "rb") as f:
                files = {"fileToUpload": f}
                resp = requests.post(
                    self.endpoint,
                    data=data,
                    files=files,
                    headers=headers,
                    proxies=proxies,
                    timeout=60
                )

            if resp.status_code == 200:
                result_text = resp.text.strip()
                if result_text.startswith("http://") or result_text.startswith("https://"):
                    tlog.info(f"✅ [图床-Catbox] 上传成功: {local_path} -> {result_text}")
                    return result_text
                tlog.warning(f"⚠️ [图床-Catbox] 平台返回异常内容: {result_text}")
                return None
            else:
                tlog.warning(f"⚠️ [图床-Catbox] HTTP 请求异常 ({resp.status_code}): {resp.text}")
                return None

        except Exception as e:
            tlog.error(f"🛑 [图床-Catbox] 上传异常: {e}")
            return None
