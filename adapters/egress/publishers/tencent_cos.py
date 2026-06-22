#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes Tencent COS Publisher Plugin
🚀 [V1.0]：将静态站点资产包物理同步至腾讯云 COS 存储桶，支持静态网站托管。
"""

import os
from typing import Dict, Any, List, Optional
from core.adapters.egress.publishers.base import BasePublisher, PublisherRegistry
from core.utils.tracing import tlog

# MIME 类型映射
MIME_TYPE_MAP = {
    ".html": "text/html; charset=utf-8",
    ".htm": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".mjs": "application/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".xml": "application/xml; charset=utf-8",
    ".txt": "text/plain; charset=utf-8",
    ".md": "text/markdown; charset=utf-8",
    ".svg": "image/svg+xml",
    ".webp": "image/webp",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".ico": "image/x-icon",
    ".woff": "font/woff",
    ".woff2": "font/woff2",
    ".ttf": "font/ttf",
    ".eot": "application/vnd.ms-fontobject",
    ".pdf": "application/pdf",
    ".zip": "application/zip",
    ".map": "application/json",
}

def _get_content_type(filename: str) -> str:
    """
    根据文件名后缀映射 HTTP 传输所需的 Content-Type。

    :param filename: 文件名字符串
    :return: 对应的 MIME-Type 类型串
    """
    ext = os.path.splitext(filename)[1].lower()
    return MIME_TYPE_MAP.get(ext, "application/octet-stream")

@PublisherRegistry.register("tencent_cos")
class TencentCosPublisher(BasePublisher):
    """腾讯云 COS 静态全站托管分发适配器驱动"""
    PLUGIN_ID = "tencent_cos"
    DISPLAY_NAME = "Tencent COS"
    VERSION = "V1.0"
    DESCRIPTION = "将静态资产上传至腾讯云 COS 存储桶，支持自动 Content-Type 映射与加速域名。"

    def __init__(self, config: Dict[str, Any], sys_config: Dict[str, Any] = None):
        super().__init__(config, sys_config)
        self.bucket = config.get("bucket", "")
        self.region = config.get("region", "").strip()
        self.secret_id = config.get("secret_id", "")
        self.secret_key = config.get("secret_key", "")
        self.prefix = config.get("prefix", "").strip("/")
        self.public_url = config.get("public_url", "").rstrip("/")

    def push(self, bundle_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        validation_errors = self.validate_config()
        if validation_errors:
            return {"status": "skipped", "message": f"腾讯云 COS 配置不完整: {'; '.join(validation_errors)}"}

        if not os.path.isdir(bundle_path):
            return {"status": "error", "message": f"Bundle path 不存在: {bundle_path}"}

        try:
            from qcloud_cos import CosConfig, CosS3Client
        except ImportError:
            tlog.error("❌ [Tencent COS] qcloud_cos 未安装，无法执行 COS 上传。请运行: pip install cos-python-sdk-v5")
            return {"status": "error", "message": "cos-python-sdk-v5 未安装，请运行 pip install cos-python-sdk-v5"}

        tlog.info(f"🚀 [Tencent COS] 正在上传至 bucket '{self.bucket}'...")

        try:
            cos_config = CosConfig(Region=self.region, SecretId=self.secret_id, SecretKey=self.secret_key)
            client = CosS3Client(cos_config)

            file_count = 0
            error_count = 0

            for root, dirs, files in os.walk(bundle_path):
                dirs[:] = [d for d in dirs if not d.startswith(".")]

                for file in files:
                    if file.startswith("."):
                        continue

                    local_path = os.path.join(root, file)
                    relative_path = os.path.relpath(local_path, bundle_path)
                    cos_key = relative_path.replace("\\", "/")
                    if self.prefix:
                        cos_key = f"{self.prefix}/{cos_key}"

                    content_type = _get_content_type(file)

                    try:
                        client.upload_file(
                            Bucket=self.bucket,
                            LocalFilePath=local_path,
                            Key=cos_key,
                            ExtraArgs={"ContentType": content_type}
                        )
                        file_count += 1
                    except Exception as upload_err:
                        tlog.warning(f"⚠️ [Tencent COS] 文件上传失败 ({cos_key}): {upload_err}")
                        error_count += 1

            if error_count > 0:
                tlog.warning(f"⚠️ [Tencent COS] 部分上传完成: {file_count} 成功，{error_count} 失败。")
                return {
                    "status": "partial",
                    "files": file_count,
                    "errors": error_count,
                    "bucket": self.bucket,
                }

            tlog.info(f"✅ [Tencent COS] 全量上传成功！共 {file_count} 个文件 → bucket: {self.bucket}")
            return {
                "status": "success",
                "files": file_count,
                "bucket": self.bucket,
                "url": self.get_deploy_url(),
            }

        except Exception as e:
            tlog.error(f"❌ [Tencent COS] 上传失败: {e}")
            return {"status": "error", "message": str(e)}

    def is_healthy(self) -> bool:
        if not self.secret_id or not self.secret_key or not self.bucket or not self.region:
            return False
        try:
            from qcloud_cos import CosConfig, CosS3Client
            cos_config = CosConfig(Region=self.region, SecretId=self.secret_id, SecretKey=self.secret_key)
            client = CosS3Client(cos_config)
            # 测试连通性
            client.bucket_exists(Bucket=self.bucket)
            return True
        except Exception:
            return False

    def validate_config(self) -> List[str]:
        errors: List[str] = []
        if not self.bucket:
            errors.append("缺少必填配置: bucket")
        if not self.region:
            errors.append("缺少必填配置: region")
        if not self.secret_id:
            errors.append("缺少必填配置: secret_id")
        if not self.secret_key:
            errors.append("缺少必填配置: secret_key")
        return errors

    def get_deploy_url(self) -> Optional[str]:
        if self.public_url:
            return self.public_url
        if self.bucket and self.region:
            return f"https://{self.bucket}.cos.{self.region}.myqcloud.com"
        return None
