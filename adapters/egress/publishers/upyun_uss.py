#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes Upyun USS Publisher Plugin
🚀 [V1.0]：使用原生 HTTP REST API 将静态站点资产包物理同步至又拍云 USS 存储空间（零三方库依赖）。
"""

import os
import base64
import requests
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

@PublisherRegistry.register("upyun_uss")
class UpyunUssPublisher(BasePublisher):
    """又拍云 USS 静态全站托管分发适配器驱动"""
    PLUGIN_ID = "upyun_uss"
    DISPLAY_NAME = "又拍云 USS"
    VERSION = "V1.0"
    DESCRIPTION = "将静态资产上传至又拍云 USS 存储空间，无需任何第三方包依赖，极速轻量。"

    def __init__(self, config: Dict[str, Any], sys_config: Dict[str, Any] = None):
        super().__init__(config, sys_config)
        self.bucket = config.get("bucket", "")
        self.operator = config.get("operator", "")
        self.password = config.get("password", "")
        self.prefix = config.get("prefix", "").strip("/")
        self.public_url = config.get("public_url", "").rstrip("/")

    def push(self, bundle_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        validation_errors = self.validate_config()
        if validation_errors:
            return {"status": "skipped", "message": f"又拍云 USS 配置不完整: {'; '.join(validation_errors)}"}

        if not os.path.isdir(bundle_path):
            return {"status": "error", "message": f"Bundle path 不存在: {bundle_path}"}

        tlog.info(f"🚀 [又拍云 USS] 正在同步静态资源至空间 '{self.bucket}'...")

        try:
            # 准备 Basic Auth 凭证
            auth_str = f"{self.operator}:{self.password}"
            auth_b64 = base64.b64encode(auth_str.encode("utf-8")).decode("utf-8")
            auth_header = f"Basic {auth_b64}"

            file_count = 0
            error_count = 0

            for root, dirs, files in os.walk(bundle_path):
                dirs[:] = [d for d in dirs if not d.startswith(".")]

                for file in files:
                    if file.startswith("."):
                        continue

                    local_path = os.path.join(root, file)
                    relative_path = os.path.relpath(local_path, bundle_path)
                    uss_key = relative_path.replace("\\", "/")
                    if self.prefix:
                        uss_key = f"{self.prefix}/{uss_key}"

                    # 物理请求又拍云 REST 节点
                    url = f"https://v0.api.upyun.com/{self.bucket}/{uss_key}"
                    content_type = _get_content_type(file)

                    headers = {
                        "Authorization": auth_header,
                        "Content-Type": content_type,
                        "User-Agent": "Illacme-Plenipes-Client"
                    }

                    try:
                        with open(local_path, "rb") as fileobj:
                            resp = requests.put(url, data=fileobj, headers=headers, timeout=20)
                        
                        if resp.status_code == 200:
                            file_count += 1
                        else:
                            tlog.warning(f"⚠️ [又拍云 USS] 文件上传失败 ({uss_key})，状态码: {resp.status_code}")
                            error_count += 1
                    except Exception as upload_err:
                        tlog.warning(f"⚠️ [又拍云 USS] 上传异常 ({uss_key}): {upload_err}")
                        error_count += 1

            if error_count > 0:
                tlog.warning(f"⚠️ [又拍云 USS] 部分同步完成: {file_count} 成功，{error_count} 失败。")
                return {
                    "status": "partial",
                    "files": file_count,
                    "errors": error_count,
                    "bucket": self.bucket,
                }

            tlog.info(f"✅ [又拍云 USS] 全量同步成功！共 {file_count} 个文件 → 空间: {self.bucket}")
            return {
                "status": "success",
                "files": file_count,
                "bucket": self.bucket,
                "url": self.get_deploy_url(),
            }

        except Exception as e:
            tlog.error(f"❌ [又拍云 USS] 同步失败: {e}")
            return {"status": "error", "message": str(e)}

    def is_healthy(self) -> bool:
        if not self.operator or not self.password or not self.bucket:
            return False
        try:
            # 校验鉴权有效性：尝试获取 Bucket 下的顶级目录列表
            url = f"https://v0.api.upyun.com/{self.bucket}/"
            auth_str = f"{self.operator}:{self.password}"
            auth_b64 = base64.b64encode(auth_str.encode("utf-8")).decode("utf-8")
            headers = {
                "Authorization": f"Basic {auth_b64}",
                "User-Agent": "Illacme-Plenipes-Client",
                "X-List-Limit": "1"
            }
            resp = requests.get(url, headers=headers, timeout=5)
            # 又拍云空桶或有文件通常会返回 200，若未配置静态页面托管目录可能会返回 404，但鉴权失败肯定是 401/403
            return resp.status_code in [200, 404]
        except Exception:
            return False

    def validate_config(self) -> List[str]:
        errors: List[str] = []
        if not self.bucket:
            errors.append("缺少必填配置: bucket")
        if not self.operator:
            errors.append("缺少必填配置: operator")
        if not self.password:
            errors.append("缺少必填配置: password")
        return errors

    def get_deploy_url(self) -> Optional[str]:
        if self.public_url:
            return self.public_url
        return None
