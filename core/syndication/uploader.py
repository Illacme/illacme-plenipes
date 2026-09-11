#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Syndication Image Uploader (分发图片上传中枢)
职责：负责动态载入图床插件并进行文稿相对路径图片的物理委托上传。
🛡️ [SOP-01] 物理行数限制：保持在 300 行以内。
"""

import os
from core.utils.tracing import tlog
from core.adapters.image_hosting.targets import IMAGE_HOST_REGISTRY

class ImageUploader:
    def __init__(self, syndication_cfg, sys_tuning):
        self.cfg = syndication_cfg or {}
        self.sys_tuning = sys_tuning or {}
        self.host_instance = None
        self.site_url = (self.sys_tuning.get("site_url") or "").rstrip("/")
        self.vault_root = self.sys_tuning.get("vault_root") or os.getcwd()
        self._initialize_host()

    def _initialize_host(self):
        """动态检测并装配图床驱动插件"""
        s3_cfg = None
        # 1. 优先尝试提取向后兼容的 S3 图床设置
        for root in [self.sys_tuning, self.cfg]:
            if not isinstance(root, dict):
                continue
            pub_ctrl = root.get("publish_control", {})
            if hasattr(pub_ctrl, "direct_upload"):
                direct_upload = getattr(pub_ctrl, "direct_upload", {})
            elif isinstance(pub_ctrl, dict):
                direct_upload = pub_ctrl.get("direct_upload", {})
            else:
                direct_upload = {}
            if hasattr(direct_upload, "s3"):
                s3 = getattr(direct_upload, "s3", None)
            elif isinstance(direct_upload, dict):
                s3 = direct_upload.get("s3")
            else:
                s3 = None
            if s3: s3_cfg = s3

            d_up = root.get("direct_upload", {})
            if isinstance(d_up, dict) and d_up.get("s3"):
                s3_cfg = d_up.get("s3")
            if root.get("s3"):
                s3_cfg = root.get("s3")

        # 2. 对准驱动类型
        if s3_cfg and s3_cfg.get("enabled"):
            provider = "s3"
            host_cfg = s3_cfg
        else:
            image_host_cfg = self.sys_tuning.get("image_hosting", {}) or self.cfg.get("image_hosting", {})
            if "provider" in image_host_cfg:
                provider = image_host_cfg.get("provider")
                host_cfg = image_host_cfg
            else:
                provider = None
                host_cfg = {}
                # 遍历查找显式 enabled 的驱动
                for p_id, p_cfg in image_host_cfg.items():
                    if isinstance(p_cfg, dict) and p_cfg.get("enabled"):
                        provider = p_id
                        host_cfg = p_cfg
                        break
                # 若无显式 enabled，但有唯一配置且具备 token/api_key/secret 则自动推导
                if not provider:
                    for p_id, p_cfg in image_host_cfg.items():
                        if isinstance(p_cfg, dict) and (p_cfg.get("token") or p_cfg.get("api_key") or p_cfg.get("secret")):
                            provider = p_id
                            host_cfg = p_cfg
                            break

        if not provider:
            if self.site_url:
                tlog.info(f"🌐 [图床中枢] 未配置外部图床驱动，将自动回退至独立站原生 CDN 模式 ({self.site_url})。")
            else:
                tlog.warning("⚠️ [图床中枢] 未配置启用的图床服务提供商，亦未感知到独立站公网域名。")
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
        """
        委托图床驱动物理上传图片，若未配置则智能回退至独立站原生托管 CDN 外链
        """
        # 1. 优先调用已挂载的第三方图床插件
        if self.host_instance:
            try:
                res = self.host_instance.upload(local_path)
                if res:
                    return res
            except Exception as e:
                tlog.error(f"🛑 [图床中枢] 第三方图床上传失败: {e}")

        # 2. 🚀 [Hosting CDN Fallback] 独立站原生静态资产外链智能回退
        if self.site_url and os.path.exists(local_path):
            try:
                norm_local = os.path.abspath(local_path)
                norm_vault = os.path.abspath(self.vault_root)
                if norm_local.startswith(norm_vault):
                    rel = os.path.relpath(norm_local, norm_vault)
                else:
                    rel = os.path.basename(local_path)
                    rel = f"assets/{rel}"
                rel_url = rel.replace(os.sep, '/').lstrip('/')
                cdn_url = f"{self.site_url}/{rel_url}"
                tlog.info(f"🌐 [图床中枢-CDN回退] 自动映射独立站资产外链: {cdn_url}")
                return cdn_url
            except Exception as fe:
                tlog.warning(f"⚠️ [图床中枢-CDN回退] 计算独立站资产 URL 失败: {fe}")

        tlog.warning(f"⚠️ [图床中枢] 无可用图床或独立站外链，跳过图片上云: {local_path}")
        return None
