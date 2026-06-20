#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes S3 Image Hosting Plugin (S3 图床物理插件)
职责：利用 boto3 将本地文稿相对图片上传至兼容 S3/R2/OSS 存储桶。
🛡️ [SOP-01] 物理行数限制：保持在 300 行以内。
"""

import os
import hashlib
from typing import Dict, Any

from core.adapters.image_hosting.base import BaseImageHost
from core.utils.tracing import tlog

class S3ImageHost(BaseImageHost):
    """
    🚀 S3 / R2 / OSS 兼容对象存储图床插件
    """
    PLUGIN_ID = "s3"

    def __init__(self, config: Dict[str, Any], sys_tuning: Dict[str, Any] = None):
        super().__init__(config, sys_tuning)
        self.bucket = self.config.get("bucket", "")
        self.region = self.config.get("region", "us-east-1")
        self.endpoint_url = self.config.get("endpoint_url", "") or None
        self.prefix = self.config.get("prefix", "").strip("/")
        self.access_key = self.config.get("access_key", "")
        self.secret_key = self.config.get("secret_key", "")
        self.public_url = self.config.get("public_url", "").rstrip("/")
        self.acl = self.config.get("acl", "")

    def upload(self, local_path: str) -> str:
        """
        物理上传本地相对图片至公网 S3，返回其 CDN URL
        """
        if not self.bucket or not self.access_key or not self.secret_key:
            tlog.warning("⚠️ S3 图床凭证不完整，跳过上传。")
            return None

        try:
            import boto3
        except ImportError:
            tlog.error("❌ boto3 未安装，无法执行图床 S3 上传。")
            return None

        try:
            # 1. 计算文件 MD5 校验和用于去重和唯一键值命名
            hasher = hashlib.md5()
            with open(local_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096 * 1024), b""):
                    hasher.update(chunk)
            file_hash = hasher.hexdigest()
            ext = os.path.splitext(local_path)[1].lower()

            shard_dir = file_hash[:2]
            actual_hash = file_hash[2:10]
            name_base = os.path.splitext(os.path.basename(local_path))[0]
            
            s3_key = f"cdn/images/{shard_dir}/{name_base}_{actual_hash}{ext}"
            if self.prefix:
                s3_key = f"{self.prefix}/{s3_key}"

            # 2. 创建 boto3 client
            s3_client = boto3.client(
                "s3",
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                region_name=self.region,
                endpoint_url=self.endpoint_url,
            )

            mime_types = {
                ".png": "image/png",
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".gif": "image/gif",
                ".webp": "image/webp",
                ".svg": "image/svg+xml"
            }
            content_type = mime_types.get(ext, "application/octet-stream")
            extra_args = {"ContentType": content_type}
            if self.acl:
                extra_args["ACL"] = self.acl

            s3_client.upload_file(local_path, self.bucket, s3_key, ExtraArgs=extra_args)
            tlog.info(f"✅ [图床-S3] 上传成功: {local_path} -> {s3_key}")

            # 3. 拼接 CDN URL
            if self.public_url:
                return f"{self.public_url}/{s3_key}"
            
            if self.endpoint_url and "amazonaws.com" not in self.endpoint_url:
                return f"{self.endpoint_url.rstrip('/')}/{self.bucket}/{s3_key}"

            return f"https://{self.bucket}.s3.{self.region}.amazonaws.com/{s3_key}"

        except Exception as e:
            tlog.error(f"🛑 [图床-S3] 上传异常 ({local_path}): {e}")
            return None
