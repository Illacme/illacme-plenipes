#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Syndication Image Uploader (分发图片上传底座)
职责：负责将文稿本地资产上传至公网兼容 S3/R2/OSS 图床。
🛡️ [SOP-01] 物理行数限制：保持在 300 行以内。
"""

import os
import hashlib
from core.utils.tracing import tlog

class ImageUploader:
    def __init__(self, syndication_cfg, sys_tuning):
        self.cfg = syndication_cfg or {}
        self.sys_tuning = sys_tuning or {}

    def _get_s3_config(self):
        """防御式读取 S3 图床配置"""
        for root in [self.sys_tuning, self.cfg]:
            if not isinstance(root, dict):
                continue
            s3 = root.get("publish_control", {}).get("direct_upload", {}).get("s3")
            if s3: return s3
            s3 = root.get("direct_upload", {}).get("s3")
            if s3: return s3
            s3 = root.get("s3")
            if s3: return s3
        return None

    def upload_image(self, local_path: str) -> str:
        """物理上传本地相对图片至公网 S3，返回其 CDN URL"""
        s3_cfg = self._get_s3_config()
        if not s3_cfg or not s3_cfg.get("enabled"):
            tlog.warning(f"⚠️ 图床未启用，跳过图片上云: {local_path}")
            return None

        bucket = s3_cfg.get("bucket")
        access_key = s3_cfg.get("access_key")
        secret_key = s3_cfg.get("secret_key")
        if not bucket or not access_key or not secret_key:
            tlog.warning("⚠️ S3 图床凭证不完整，跳过上传。")
            return None

        try:
            import boto3
        except ImportError:
            tlog.error("❌ boto3 未安装，无法执行图床上传。")
            return None

        try:
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
            if s3_cfg.get("prefix"):
                s3_key = f"{s3_cfg.get('prefix').strip('/')}/{s3_key}"

            s3_client = boto3.client(
                "s3",
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=s3_cfg.get("region", "us-east-1"),
                endpoint_url=s3_cfg.get("endpoint_url") or None,
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
            if s3_cfg.get("acl"):
                extra_args["ACL"] = s3_cfg.get("acl")

            s3_client.upload_file(local_path, bucket, s3_key, ExtraArgs=extra_args)
            tlog.info(f"✅ [图床] 图片上传成功: {local_path} -> {s3_key}")

            public_url = s3_cfg.get("public_url")
            if public_url:
                return f"{public_url.rstrip('/')}/{s3_key}"
            
            endpoint_url = s3_cfg.get("endpoint_url")
            if endpoint_url and "amazonaws.com" not in endpoint_url:
                return f"{endpoint_url.rstrip('/')}/{bucket}/{s3_key}"

            region = s3_cfg.get("region", "us-east-1")
            return f"https://{bucket}.s3.{region}.amazonaws.com/{s3_key}"

        except Exception as e:
            tlog.error(f"🛑 [图床] 上传异常 ({local_path}): {e}")
            return None
