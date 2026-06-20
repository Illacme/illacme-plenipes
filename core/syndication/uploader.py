#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Syndication Image Uploader (分发图片上传中枢)
职责：负责动态载入图床插件并进行文稿相对路径图片的物理委托上传。
🛡️ [SOP-01] 物理行数限制：保持在 300 行以内。
"""

from core.utils.tracing import tlog
from core.adapters.image_hosting.targets import IMAGE_HOST_REGISTRY

class ImageUploader:
    def __init__(self, syndication_cfg, sys_tuning):
        self.cfg = syndication_cfg or {}
        self.sys_tuning = sys_tuning or {}
        self.host_instance = None
        self._initialize_host()

    def _initialize_host(self):
        """动态检测并装配图床驱动插件"""
        s3_cfg = None
        # 1. 优先尝试提取向后兼容的 S3 图床设置
        for root in [self.sys_tuning, self.cfg]:
            if not isinstance(root, dict):
                continue
            s3 = root.get("publish_control", {}).get("direct_upload", {}).get("s3")
            if s3: s3_cfg = s3
            s3 = root.get("direct_upload", {}).get("s3")
            if s3: s3_cfg = s3
            s3 = root.get("s3")
            if s3: s3_cfg = s3

        # 2. 对准驱动类型
        if s3_cfg and s3_cfg.get("enabled"):
            provider = "s3"
            host_cfg = s3_cfg
        else:
            image_host_cfg = self.sys_tuning.get("image_hosting", {}) or self.cfg.get("image_hosting", {})
            provider = image_host_cfg.get("provider")
            host_cfg = image_host_cfg

        if not provider:
            tlog.warning("⚠️ [图床中枢] 未配置启用的图床服务提供商。")
            return

        # 3. 动态自注册挂载
        host_cls = IMAGE_HOST_REGISTRY.get(provider)
        if host_cls:
            try:
                self.host_instance = host_cls(host_cfg, self.sys_tuning)
                tlog.info(f"📡 [图床中枢] 已动态挂载图床驱动: {provider}")
            except Exception as e:
                tlog.error(f"🛑 [图床中枢] 图床驱动 '{provider}' 初始化失败: {e}")
        else:
            tlog.warning(f"⚠️ [图床中枢] 无法找到图床驱动: {provider}")

    def upload_image(self, local_path: str) -> str:
        """委托具体的图床驱动插件物理上传图片"""
        if not self.host_instance:
            tlog.warning(f"⚠️ [图床中枢] 图床驱动未挂载，跳过图片上云: {local_path}")
            return None
        return self.host_instance.upload(local_path)
