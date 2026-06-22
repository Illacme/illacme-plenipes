#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes Upyun USS Image Hosting Plugin
职责：使用原生 HTTP REST API 将本地图片上传至又拍云 USS 存储空间（无需第三方依赖）。
🛡️ [SOP-01] 物理行数限制：保持在 300 行以内。
"""

import os
import base64
import requests
import hashlib
from typing import Dict, Any

from core.adapters.image_hosting.base import BaseImageHost
from core.utils.tracing import tlog

class UpyunUssImageHost(BaseImageHost):
    """
    🚀 又拍云 USS 存储空间图床插件 (原生 HTTP 驱动)
    """
    DISPLAY_NAME = "又拍云 USS"
    DESCRIPTION = "又拍云云存储 (USS) 图床，基于原生高效 HTTP REST 通信，零三方库依赖。"
    VERSION = "V1.0"
    PLUGIN_ID = "upyun_uss"

    def __init__(self, config: Dict[str, Any], sys_tuning: Dict[str, Any] = None):
        super().__init__(config, sys_tuning)
        self.bucket = self.config.get("bucket", "")
        self.operator = self.config.get("operator", "")
        self.password = self.config.get("password", "")
        self.path = self.config.get("path", "images").strip("/")
        self.domain = self.config.get("domain", "").strip().rstrip("/")

    def upload(self, local_path: str) -> str:
        """
        物理上传本地图片至又拍云 USS
        """
        if not self.bucket or not self.operator or not self.password or not self.domain:
            tlog.warning("⚠️ 又拍云 USS 凭证、服务名称或加速域名未配置，跳过上传。")
            return None

        if not os.path.exists(local_path):
            tlog.error(f"❌ 找不到待上传的本地图片文件: {local_path}")
            return None

        try:
            # 计算文件哈希
            hasher = hashlib.md5()
            with open(local_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096 * 1024), b""):
                    hasher.update(chunk)
            file_hash = hasher.hexdigest()
            ext = os.path.splitext(local_path)[1].lower()
            name_base = os.path.splitext(os.path.basename(local_path))[0]
            
            uss_key = f"{name_base}_{file_hash[:8]}{ext}"
            if self.path:
                uss_key = f"{self.path}/{uss_key}"

            # 使用又拍云 HTTP REST API (v0.api.upyun.com)
            url = f"https://v0.api.upyun.com/{self.bucket}/{uss_key}"
            
            # 组装 Basic Auth 凭证
            auth_str = f"{self.operator}:{self.password}"
            auth_b64 = base64.b64encode(auth_str.encode("utf-8")).decode("utf-8")
            
            headers = {
                "Authorization": f"Basic {auth_b64}",
                "User-Agent": "Illacme-Plenipes-Client"
            }

            with open(local_path, "rb") as f:
                resp = requests.put(url, data=f, headers=headers, timeout=30)

            if resp.status_code == 200:
                tlog.info(f"✅ [图床-又拍云USS] 上传成功: {local_path} -> {uss_key}")
                final_domain = self.domain
                if not (final_domain.startswith("http://") or final_domain.startswith("https://")):
                    final_domain = f"https://{final_domain}"
                return f"{final_domain}/{uss_key}"
            else:
                tlog.warning(f"⚠️ [图床-又拍云USS] 上传响应异常 ({resp.status_code}): {resp.text}")
                return None

        except Exception as e:
            tlog.error(f"🛑 [图床-又拍云USS] 上传发生异常: {e}")
            return None
