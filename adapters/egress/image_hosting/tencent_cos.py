#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes Tencent Cloud COS Image Hosting Plugin
职责：利用 cos-python-sdk-v5 (qcloud_cos) 将本地图片上传至腾讯云 COS 存储桶。
🛡️ [SOP-01] 物理行数限制：保持在 300 行以内。
"""

import os
import hashlib
from typing import Dict, Any

from core.adapters.image_hosting.base import BaseImageHost
from core.utils.tracing import tlog

class TencentCosImageHost(BaseImageHost):
    """
    🚀 腾讯云 COS 对象存储图床插件
    """
    DISPLAY_NAME = "腾讯云 COS"
    DESCRIPTION = "腾讯云对象存储 (COS) 图床，高安全性、高性能图片分发解决方案。"
    VERSION = "V1.0"
    PLUGIN_ID = "tencent_cos"

    def __init__(self, config: Dict[str, Any], sys_tuning: Dict[str, Any] = None):
        super().__init__(config, sys_tuning)
        self.bucket = self.config.get("bucket", "")
        self.region = self.config.get("region", "")
        self.secret_id = self.config.get("secret_id", "")
        self.secret_key = self.config.get("secret_key", "")
        self.path = self.config.get("path", "images").strip("/")
        self.cdn_url = self.config.get("cdn_url", "").rstrip("/")

    def upload(self, local_path: str) -> str:
        """
        物理上传本地图片至腾讯云 COS
        """
        if not self.bucket or not self.region or not self.secret_id or not self.secret_key:
            tlog.warning("⚠️ 腾讯云 COS 凭证或 Region 未配置，跳过上传。")
            return None

        if not os.path.exists(local_path):
            tlog.error(f"❌ 找不到待上传的本地图片文件: {local_path}")
            return None

        try:
            from qcloud_cos import CosConfig
            from qcloud_cos import CosS3Client
        except ImportError:
            tlog.error("❌ qcloud_cos 未安装，无法执行腾讯云 COS 上传。请运行 'pip install cos-python-sdk-v5' 安装。")
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
            
            cos_key = f"{name_base}_{file_hash[:8]}{ext}"
            if self.path:
                cos_key = f"{self.path}/{cos_key}"

            # 配置 COS 客户端
            config = CosConfig(Region=self.region, SecretId=self.secret_id, SecretKey=self.secret_key)
            client = CosS3Client(config)

            # 执行上传
            with open(local_path, 'rb') as f:
                client.put_object(
                    Bucket=self.bucket,
                    Body=f,
                    Key=cos_key
                )

            tlog.info(f"✅ [图床-腾讯云COS] 上传成功: {local_path} -> {cos_key}")

            if self.cdn_url:
                return f"{self.cdn_url}/{cos_key}"

            # 默认 COS 域名拼接
            return f"https://{self.bucket}.cos.{self.region}.myqcloud.com/{cos_key}"

        except Exception as e:
            tlog.error(f"🛑 [图床-腾讯云COS] 上传发生异常: {e}")
            return None
