#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes Aliyun OSS Image Hosting Plugin
职责：利用 aliyun-sdk-oss (oss2) 将本地图片上传至阿里云 OSS 存储桶。
🛡️ [SOP-01] 物理行数限制：保持在 300 行以内。
"""

import os
import hashlib
from typing import Dict, Any

from core.adapters.image_hosting.base import BaseImageHost
from core.utils.tracing import tlog

class AliyunOssImageHost(BaseImageHost):
    """
    🚀 阿里云 OSS 对象存储图床插件
    """
    DISPLAY_NAME = "阿里云 OSS"
    DESCRIPTION = "阿里云对象存储 (OSS) 图床，支持高可用网络分发与 CDN 域名加速。"
    VERSION = "V1.0"
    PLUGIN_ID = "aliyun_oss"

    def __init__(self, config: Dict[str, Any], sys_tuning: Dict[str, Any] = None):
        super().__init__(config, sys_tuning)
        self.bucket_name = self.config.get("bucket", "")
        self.endpoint = self.config.get("endpoint", "").strip()
        self.access_key_id = self.config.get("access_key_id", "")
        self.access_key_secret = self.config.get("access_key_secret", "")
        self.path = self.config.get("path", "images").strip("/")
        self.cdn_url = self.config.get("cdn_url", "").rstrip("/")

    def upload(self, local_path: str) -> str:
        """
        物理上传本地图片至阿里云 OSS
        """
        if not self.bucket_name or not self.endpoint or not self.access_key_id or not self.access_key_secret:
            tlog.warning("⚠️ 阿里云 OSS 凭证或 Endpoint 未配置，跳过上传。")
            return None

        if not os.path.exists(local_path):
            tlog.error(f"❌ 找不到待上传的本地图片文件: {local_path}")
            return None

        try:
            import oss2
        except ImportError:
            tlog.error("❌ oss2 未安装，无法执行阿里云 OSS 上传。请运行 'pip install oss2' 安装。")
            return None

        try:
            # 计算文件哈希防重复
            hasher = hashlib.md5()
            with open(local_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096 * 1024), b""):
                    hasher.update(chunk)
            file_hash = hasher.hexdigest()
            ext = os.path.splitext(local_path)[1].lower()
            name_base = os.path.splitext(os.path.basename(local_path))[0]
            
            oss_key = f"{name_base}_{file_hash[:8]}{ext}"
            if self.path:
                oss_key = f"{self.path}/{oss_key}"

            # 初始化 OSS 授权和存储桶
            # 协议前缀补全
            endpoint_url = self.endpoint
            if not (endpoint_url.startswith("http://") or endpoint_url.startswith("https://")):
                endpoint_url = f"https://{endpoint_url}"

            auth = oss2.Auth(self.access_key_id, self.access_key_secret)
            bucket = oss2.Bucket(auth, endpoint_url, self.bucket_name)

            # 上传文件
            with open(local_path, 'rb') as fileobj:
                bucket.put_object(oss_key, fileobj)

            tlog.info(f"✅ [图床-阿里云OSS] 上传成功: {local_path} -> {oss_key}")

            # 返回 CDN 链接或 OSS 链接
            if self.cdn_url:
                return f"{self.cdn_url}/{oss_key}"

            # 去除 endpoint 头部的 http:// 或 https:// 协议部分用以拼接
            clean_endpoint = self.endpoint.replace("https://", "").replace("http://", "")
            return f"https://{self.bucket_name}.{clean_endpoint}/{oss_key}"

        except Exception as e:
            tlog.error(f"🛑 [图床-阿里云OSS] 上传发生异常: {e}")
            return None
