#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes Aliyun OSS Publisher Plugin
🚀 [V1.0]：将静态站点资产包物理同步至阿里云 OSS 存储桶，支持静态网站托管。
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

@PublisherRegistry.register("aliyun_oss")
class AliyunOssPublisher(BasePublisher):
    """阿里云 OSS 静态全站托管分发适配器驱动"""
    PLUGIN_ID = "aliyun_oss"
    DISPLAY_NAME = "Aliyun OSS"
    VERSION = "V1.0"
    DESCRIPTION = "将静态资产上传至阿里云 OSS 存储桶，支持自动 Content-Type 映射与加速域名。"

    def __init__(self, config: Dict[str, Any], sys_config: Dict[str, Any] = None):
        super().__init__(config, sys_config)
        self.bucket = config.get("bucket", "")
        self.endpoint = config.get("endpoint", "").strip()
        self.access_key_id = config.get("access_key_id", "")
        self.access_key_secret = config.get("access_key_secret", "")
        self.prefix = config.get("prefix", "").strip("/")
        self.public_url = config.get("public_url", "").rstrip("/")

    def push(self, bundle_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        validation_errors = self.validate_config()
        if validation_errors:
            return {"status": "skipped", "message": f"阿里云 OSS 配置不完整: {'; '.join(validation_errors)}"}

        if not os.path.isdir(bundle_path):
            return {"status": "error", "message": f"Bundle path 不存在: {bundle_path}"}

        try:
            import oss2
        except ImportError:
            tlog.error("❌ [Aliyun OSS] oss2 未安装，无法执行 OSS 上传。请运行: pip install oss2")
            return {"status": "error", "message": "oss2 未安装，请运行 pip install oss2"}

        tlog.info(f"🚀 [Aliyun OSS] 正在上传至 bucket '{self.bucket}'...")

        try:
            endpoint_url = self.endpoint
            if not (endpoint_url.startswith("http://") or endpoint_url.startswith("https://")):
                endpoint_url = f"https://{endpoint_url}"

            auth = oss2.Auth(self.access_key_id, self.access_key_secret)
            bucket = oss2.Bucket(auth, endpoint_url, self.bucket)

            file_count = 0
            error_count = 0

            for root, dirs, files in os.walk(bundle_path):
                dirs[:] = [d for d in dirs if not d.startswith(".")]

                for file in files:
                    if file.startswith("."):
                        continue

                    local_path = os.path.join(root, file)
                    relative_path = os.path.relpath(local_path, bundle_path)
                    oss_key = relative_path.replace("\\", "/")
                    if self.prefix:
                        oss_key = f"{self.prefix}/{oss_key}"

                    content_type = _get_content_type(file)
                    headers = {"Content-Type": content_type}

                    try:
                        bucket.put_object_from_file(oss_key, local_path, headers=headers)
                        file_count += 1
                    except Exception as upload_err:
                        tlog.warning(f"⚠️ [Aliyun OSS] 文件上传失败 ({oss_key}): {upload_err}")
                        error_count += 1

            if error_count > 0:
                tlog.warning(f"⚠️ [Aliyun OSS] 部分上传完成: {file_count} 成功，{error_count} 失败。")
                return {
                    "status": "partial",
                    "files": file_count,
                    "errors": error_count,
                    "bucket": self.bucket,
                }

            tlog.info(f"✅ [Aliyun OSS] 全量上传成功！共 {file_count} 个文件 → bucket: {self.bucket}")
            return {
                "status": "success",
                "files": file_count,
                "bucket": self.bucket,
                "url": self.get_deploy_url(),
            }

        except Exception as e:
            tlog.error(f"❌ [Aliyun OSS] 上传失败: {e}")
            return {"status": "error", "message": str(e)}

    def is_healthy(self) -> bool:
        if not self.access_key_id or not self.access_key_secret or not self.bucket or not self.endpoint:
            return False
        try:
            import oss2
            endpoint_url = self.endpoint
            if not (endpoint_url.startswith("http://") or endpoint_url.startswith("https://")):
                endpoint_url = f"https://{endpoint_url}"
            auth = oss2.Auth(self.access_key_id, self.access_key_secret)
            bucket = oss2.Bucket(auth, endpoint_url, self.bucket)
            # 测试连通性
            bucket.get_bucket_info()
            return True
        except Exception:
            return False

    def validate_config(self) -> List[str]:
        errors: List[str] = []
        if not self.bucket:
            errors.append("缺少必填配置: bucket")
        if not self.endpoint:
            errors.append("缺少必填配置: endpoint")
        if not self.access_key_id:
            errors.append("缺少必填配置: access_key_id")
        if not self.access_key_secret:
            errors.append("缺少必填配置: access_key_secret")
        return errors

    def get_deploy_url(self) -> Optional[str]:
        if self.public_url:
            return self.public_url
        if self.bucket and self.endpoint:
            clean_endpoint = self.endpoint.replace("https://", "").replace("http://", "")
            return f"https://{self.bucket}.{clean_endpoint}"
        return None
