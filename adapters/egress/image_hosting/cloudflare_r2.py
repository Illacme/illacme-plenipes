#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes Cloudflare R2 Image Hosting Plugin
职责：专为 Cloudflare R2 定制的对象存储图床驱动，免去手动输入 Endpoint，享受每月 10GB 免费与 0 出口流量费。
🛡️ [SOP-01] 物理行数限制：保持在 300 行以内。
"""

import os
import hashlib
from typing import Dict, Any, Optional

from core.adapters.image_hosting.base import BaseImageHost
from core.utils.tracing import tlog


class CloudflareR2ImageHost(BaseImageHost):
    """
    🚀 Cloudflare R2 专属开箱即用对象存储驱动
    """
    DISPLAY_NAME = "Cloudflare R2"
    DESCRIPTION = "Cloudflare R2 对象存储，每月 10GB 永久免费存储且 0 出口流量费，支持绑定个人域名。"
    VERSION = "V1.0"
    PLUGIN_ID = "cloudflare_r2"

    def __init__(self, config: Dict[str, Any], sys_tuning: Optional[Dict[str, Any]] = None):
        super().__init__(config, sys_tuning)
        self.account_id = (self.config.get("account_id") or "").strip()
        self.access_key_id = (self.config.get("access_key_id") or self.config.get("access_key") or "").strip()
        self.secret_access_key = (self.config.get("secret_access_key") or self.config.get("secret_key") or "").strip()
        self.bucket = (self.config.get("bucket") or "").strip()
        self.public_url = (self.config.get("public_url") or "").rstrip("/")
        self.path_prefix = (self.config.get("path_prefix") or self.config.get("prefix") or "images").strip("/")

        # 智能合成 Cloudflare R2 Endpoint
        if self.account_id:
            self.endpoint_url = f"https://{self.account_id}.r2.cloudflarestorage.com"
        else:
            self.endpoint_url = (self.config.get("endpoint_url") or "").strip()

    def upload(self, local_path: str) -> Optional[str]:
        """
        物理上传本地图片至 Cloudflare R2
        """
        if not self.bucket or not self.access_key_id or not self.secret_access_key or not self.endpoint_url:
            tlog.warning("⚠️ [图床-R2] 配置不完整 (缺少 Account ID、Bucket 或 Access/Secret Key)，跳过上传。")
            return None

        if not os.path.exists(local_path):
            tlog.error(f"❌ [图床-R2] 找不到待上传的本地图片文件: {local_path}")
            return None

        try:
            import boto3
            from botocore.config import Config
        except ImportError:
            tlog.error("❌ [图床-R2] boto3 未安装，无法执行 R2 上传。")
            return None

        try:
            # 1. 计算文件哈希
            hasher = hashlib.md5()
            with open(local_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096 * 1024), b""):
                    hasher.update(chunk)
            file_hash = hasher.hexdigest()
            ext = os.path.splitext(local_path)[1].lower()

            shard_dir = file_hash[:2]
            actual_hash = file_hash[2:10]
            name_base = os.path.splitext(os.path.basename(local_path))[0]

            s3_key = f"{self.path_prefix}/{shard_dir}/{name_base}_{actual_hash}{ext}".lstrip("/")

            # 2. 构建 Boto3 R2 S3 客户端
            s3_client = boto3.client(
                "s3",
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.access_key_id,
                aws_secret_access_key=self.secret_access_key,
                region_name="auto",
                config=Config(signature_version="s3v4")
            )

            # 3. 确定 Content-Type
            import mimetypes
            content_type, _ = mimetypes.guess_type(local_path)
            extra_args = {}
            if content_type:
                extra_args["ContentType"] = content_type

            # 4. 执行上传
            with open(local_path, "rb") as f:
                s3_client.upload_fileobj(f, self.bucket, s3_key, ExtraArgs=extra_args)

            # 5. 组装直链 CDN URL
            if self.public_url:
                img_url = f"{self.public_url}/{s3_key}"
            else:
                img_url = f"{self.endpoint_url}/{self.bucket}/{s3_key}"

            tlog.info(f"✅ [图床-R2] 上传成功: {local_path} -> {img_url}")
            return img_url

        except Exception as e:
            tlog.error(f"🛑 [图床-R2] 上传发生异常: {e}")
            return None
