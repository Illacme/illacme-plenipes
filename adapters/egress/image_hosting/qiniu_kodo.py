#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes Qiniu Kodo Image Hosting Plugin
职责：利用 qiniu SDK 将本地图片上传至七牛云 Kodo 存储空间。
🛡️ [SOP-01] 物理行数限制：保持在 300 行以内。
"""

import os
import hashlib
from typing import Dict, Any

from core.adapters.image_hosting.base import BaseImageHost
from core.utils.tracing import tlog

class QiniuKodoImageHost(BaseImageHost):
    """
    🚀 七牛云 Kodo 存储空间图床插件
    """
    DISPLAY_NAME = "七牛云 Kodo"
    DESCRIPTION = "七牛云对象存储 (Kodo) 图床，支持高可用分发和静态资源访问。"
    VERSION = "V1.0"
    PLUGIN_ID = "qiniu_kodo"

    def __init__(self, config: Dict[str, Any], sys_tuning: Dict[str, Any] = None):
        super().__init__(config, sys_tuning)
        self.bucket = self.config.get("bucket", "")
        self.access_key = self.config.get("access_key", "")
        self.secret_key = self.config.get("secret_key", "")
        self.domain = self.config.get("domain", "").strip().rstrip("/")
        self.path = self.config.get("path", "images").strip("/")

    def upload(self, local_path: str) -> str:
        """
        物理上传本地图片至七牛云 Kodo
        """
        if not self.bucket or not self.access_key or not self.secret_key or not self.domain:
            tlog.warning("⚠️ 七牛云 Kodo 凭证或外链域名未配置，跳过上传。")
            return None

        if not os.path.exists(local_path):
            tlog.error(f"❌ 找不到待上传的本地图片文件: {local_path}")
            return None

        try:
            import qiniu
        except ImportError:
            tlog.error("❌ qiniu 未安装，无法执行七牛云 Kodo 上传。请运行 'pip install qiniu' 安装。")
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
            
            kodo_key = f"{name_base}_{file_hash[:8]}{ext}"
            if self.path:
                kodo_key = f"{self.path}/{kodo_key}"

            # 初始化授权
            q = qiniu.Auth(self.access_key, self.access_key) # Wait, access_key, secret_key!
            # Let me fix that: q = qiniu.Auth(self.access_key, self.secret_key)
            q = qiniu.Auth(self.access_key, self.secret_key)
            token = q.upload_token(self.bucket, kodo_key, 3600)

            # 上传
            ret, info = qiniu.put_file(token, kodo_key, local_path)

            if info.status_code == 200:
                tlog.info(f"✅ [图床-七牛云Kodo] 上传成功: {local_path} -> {kodo_key}")
                # 域名加上协议前缀补全
                final_domain = self.domain
                if not (final_domain.startswith("http://") or final_domain.startswith("https://")):
                    final_domain = f"https://{final_domain}"
                return f"{final_domain}/{kodo_key}"
            else:
                tlog.warning(f"⚠️ [图床-七牛云Kodo] 平台上传失败 ({info.status_code}): {info.text_body}")
                return None

        except Exception as e:
            tlog.error(f"🛑 [图床-七牛云Kodo] 上传发生异常: {e}")
            return None
