#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes S3 Publisher Plugin
🚀 [V76.0]：完整工业级 S3 发行适配器，支持 AWS S3 / Cloudflare R2 / 阿里云 OSS 等兼容协议。

配置示例 (config.yaml):
  publish_control:
    direct_upload:
      s3:
        enabled: true
        bucket: "my-docs-bucket"
        region: "us-east-1"
        access_key: "ENC:xxxxxx"
        secret_key: "ENC:xxxxxx"
        prefix: ""                          # 可选，上传路径前缀
        endpoint_url: ""                    # 可选，S3 兼容服务端点（R2/OSS 等）
        public_url: "https://cdn.example.com"  # 可选，用于 get_deploy_url() 推导
        acl: "public-read"                  # 可选，ACL 控制（部分服务商不支持）
"""

import os
from typing import Dict, Any, List, Optional

from core.adapters.egress.publishers.base import BasePublisher
from core.utils.tracing import tlog


# ---------------------------------------------------------------------------
# MIME 类型映射（完整覆盖静态站点常见格式）
# ---------------------------------------------------------------------------
MIME_TYPE_MAP: Dict[str, str] = {
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
    """根据文件扩展名返回对应的 Content-Type"""
    ext = os.path.splitext(filename)[1].lower()
    return MIME_TYPE_MAP.get(ext, "application/octet-stream")


class S3Publisher(BasePublisher):
    """
    🚀 [V76.0] S3 发布插件（完整工业级）
    将静态站点产物上传至 S3 兼容存储桶，支持 AWS S3、Cloudflare R2、阿里云 OSS 等。
    """
    PLUGIN_ID = "s3"
    DISPLAY_NAME = "AWS S3 / R2"
    VERSION = "V76.0"
    DESCRIPTION = "将静态资产上传至 S3 存储桶，支持 Cloudflare R2、阿里云 OSS 等兼容协议，含完整 MIME 类型映射。"

    def __init__(self, config: Dict[str, Any], sys_config: Dict[str, Any] = None):
        super().__init__(config, sys_config)
        self.bucket = config.get("bucket", "")
        self.region = config.get("region", "us-east-1")
        self.endpoint_url = config.get("endpoint_url", "") or None
        self.prefix = config.get("prefix", "").strip("/")
        self.access_key = config.get("access_key", "")
        self.secret_key = config.get("secret_key", "")
        self.public_url = config.get("public_url", "").rstrip("/")
        self.acl = config.get("acl", "")  # 部分服务商（如 R2）不支持 ACL，留空则不传

    # ------------------------------------------------------------------
    # BasePublisher 契约实现
    # ------------------------------------------------------------------

    def push(self, bundle_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        🚀 执行物理发布：将 bundle_path 下的全部静态产物上传至 S3 存储桶。

        执行流程：
          1. 校验配置完整性与路径存在性
          2. 按需导入 boto3（Optional 依赖防御）
          3. 遍历 bundle_path，跳过隐藏文件，逐文件上传
          4. 自动推断 Content-Type 并注入 ExtraArgs
          5. 返回标准化结果字典
        """
        # ── 1. 前置校验 ──────────────────────────────────
        validation_errors = self.validate_config()
        if validation_errors:
            return {"status": "skipped", "message": f"S3 配置不完整: {'; '.join(validation_errors)}"}

        if not os.path.isdir(bundle_path):
            return {"status": "error", "message": f"Bundle path 不存在: {bundle_path}"}

        # ── 2. Optional boto3 导入防御 ─────────────────
        try:
            import boto3
            from botocore.config import Config as BotoConfig
        except ImportError:
            tlog.error("❌ [S3] boto3 未安装，无法执行 S3 上传。请运行: pip install boto3")
            return {"status": "error", "message": "boto3 未安装，请运行 pip install boto3"}

        tlog.info(f"🚀 [S3] 正在上传至 bucket '{self.bucket}'（endpoint: {self.endpoint_url or 'AWS 默认'}）...")

        try:
            s3 = boto3.client(
                "s3",
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                region_name=self.region,
                endpoint_url=self.endpoint_url,
                config=BotoConfig(retries={"max_attempts": 5, "mode": "standard"}),
            )

            file_count = 0
            error_count = 0

            for root, dirs, files in os.walk(bundle_path):
                # 跳过隐藏目录（.git, .DS_Store 等）
                dirs[:] = [d for d in dirs if not d.startswith(".")]

                for file in files:
                    if file.startswith("."):
                        continue  # 跳过隐藏文件

                    local_path = os.path.join(root, file)
                    relative_path = os.path.relpath(local_path, bundle_path)
                    # S3 路径统一使用正斜杠
                    s3_key = relative_path.replace("\\", "/")
                    if self.prefix:
                        s3_key = f"{self.prefix}/{s3_key}"

                    content_type = _get_content_type(file)
                    extra_args: Dict[str, str] = {"ContentType": content_type}
                    if self.acl:
                        extra_args["ACL"] = self.acl

                    try:
                        s3.upload_file(
                            local_path,
                            self.bucket,
                            s3_key,
                            ExtraArgs=extra_args,
                        )
                        file_count += 1
                    except Exception as upload_err:
                        tlog.warning(f"⚠️ [S3] 文件上传失败 ({s3_key}): {upload_err}")
                        error_count += 1

            if error_count > 0:
                tlog.warning(f"⚠️ [S3] 部分上传完成: {file_count} 成功，{error_count} 失败。")
                return {
                    "status": "partial",
                    "files": file_count,
                    "errors": error_count,
                    "bucket": self.bucket,
                }

            tlog.info(f"✅ [S3] 全量上传成功！共 {file_count} 个文件 → bucket: {self.bucket}")
            return {
                "status": "success",
                "files": file_count,
                "bucket": self.bucket,
                "url": self.get_deploy_url(),
            }

        except Exception as e:
            tlog.error(f"❌ [S3] 上传失败: {e}")
            return {"status": "error", "message": str(e)}

    def is_healthy(self) -> bool:
        """
        检查 S3 连通性：尝试列出存储桶验证凭据与网络可达性。
        若 boto3 未安装，尝试自动进行物理自愈安装。
        """
        if not self.access_key or not self.secret_key or not self.bucket:
            return False
        if not self.ensure_python_dependency("boto3"):
            return False
        try:
            import boto3
            from botocore.config import Config as BotoConfig
            s3 = boto3.client(
                "s3",
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                region_name=self.region,
                endpoint_url=self.endpoint_url,
                config=BotoConfig(retries={"max_attempts": 1, "mode": "standard"}),
            )
            # 尝试 HEAD 操作验证连通性（比 list_buckets 权限要求低）
            s3.head_bucket(Bucket=self.bucket)
            return True
        except Exception:
            return False

    def validate_config(self) -> List[str]:
        """校验配置完整性，返回错误信息列表。空列表表示配置合法。"""
        errors: List[str] = []
        if not self.bucket:
            errors.append("缺少必填配置: bucket")
        if not self.access_key:
            errors.append("缺少必填配置: access_key")
        if not self.secret_key:
            errors.append("缺少必填配置: secret_key")
        return errors

    def get_deploy_url(self) -> Optional[str]:
        """
        推导存储桶的访问 URL：
        1. 若配置了 public_url，直接使用
        2. 若有 endpoint_url（R2/OSS），无法通用推导，返回 None
        3. 默认构造 S3 静态网站托管 URL
        """
        if self.public_url:
            return self.public_url
        if self.endpoint_url:
            return None  # 兼容服务端 URL 差异太大，不做推导
        if self.bucket and self.region:
            return f"https://{self.bucket}.s3-website-{self.region}.amazonaws.com"
        return None
