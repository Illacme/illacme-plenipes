#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes Telegraph Self-Hosted Image Hosting Plugin
职责：基于 Telegraph-Image 开源协议的自建图床驱动，支持 Cloudflare Pages/Workers 节点。
🛡️ [SOP-01] 物理行数限制：保持在 300 行以内。
"""

import os
import requests
from typing import Dict, Any, Optional

from core.adapters.image_hosting.base import BaseImageHost
from core.utils.tracing import tlog


class TelegraphImageHost(BaseImageHost):
    """
    🚀 Telegraph 自建图床物理通道 (基于 Telegraph-Image 协议)
    """
    DISPLAY_NAME = "Telegraph 自建图床"
    DESCRIPTION = "基于开源 Telegraph-Image 协议的自建图床网关，配合 Cloudflare 实现免费无限图床托管。"
    VERSION = "V2.0"
    PLUGIN_ID = "telegraph"

    def __init__(self, config: Dict[str, Any], sys_tuning: Optional[Dict[str, Any]] = None):
        super().__init__(config, sys_tuning)
        self.endpoint = (self.config.get("endpoint") or "").strip().rstrip("/")
        self.proxy = self.config.get("proxy", "").strip()

    def upload(self, local_path: str) -> Optional[str]:
        """
        物理上传本地图片至自建 Telegraph 网关
        """
        if not self.endpoint or "telegra.ph" in self.endpoint:
            err_msg = (
                "Telegraph 官方已全面关闭公网匿名上传通道 (400 Unknown error)。"
                "请在图床配置中填入您自建的 Cloudflare Workers / Pages 网关端点 (如 https://my-img.pages.dev)；"
                "或切换至 GitHub、ImgBB、Cloudflare R2 等图床驱动。"
            )
            tlog.warning(f"⚠️ [图床-Telegraph自建] {err_msg}")
            raise RuntimeError(err_msg)

        if not os.path.exists(local_path):
            tlog.error(f"❌ [图床-Telegraph自建] 找不到待上传的本地图片文件: {local_path}")
            return None

        proxies = {}
        if self.proxy:
            proxies = {"http": self.proxy, "https": self.proxy}

        try:
            url = f"{self.endpoint}/upload"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }

            with open(local_path, "rb") as f:
                files = {"file": f}
                resp = requests.post(url, files=files, headers=headers, proxies=proxies, timeout=45)

            if resp.status_code == 200:
                res_data = resp.json()
                if isinstance(res_data, list) and len(res_data) > 0:
                    src = res_data[0].get("src")
                    if src:
                        img_url = f"{self.endpoint}{src}" if src.startswith("/") else f"{self.endpoint}/{src}"
                        tlog.info(f"✅ [图床-Telegraph自建] 上传成功: {local_path} -> {img_url}")
                        return img_url
                tlog.warning(f"⚠️ [图床-Telegraph自建] 平台返回格式未知: {res_data}")
                return None
            else:
                err_msg = f"HTTP 请求异常 ({resp.status_code}): {resp.text}"
                tlog.warning(f"⚠️ [图床-Telegraph自建] {err_msg}")
                raise RuntimeError(err_msg)

        except Exception as e:
            tlog.error(f"🛑 [图床-Telegraph自建] 上传异常: {e}")
            raise
