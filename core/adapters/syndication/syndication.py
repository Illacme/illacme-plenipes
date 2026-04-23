#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Content Syndicator (分发调度器)
模块职责：负责将内容异步分发至多个社交/发布平台。
🚀 [V33 终极纯净版]：实现 Zero-Touch 分发自发现。
"""

import logging
from .targets import TARGET_REGISTRY

logger = logging.getLogger("Illacme.plenipes")

class ContentSyndicator:
    """
    🚀 内容分发调度中心
    不再包含任何平台逻辑，只负责根据 TARGET_REGISTRY 动态装载并执行。
    """
    def __init__(self, syndication_cfg, site_url, sys_tuning_cfg=None):
        self.cfg = syndication_cfg
        self.site_url = site_url
        self.sys_tuning = sys_tuning_cfg or {}
        
        # 🚀 动态加载已注册的平台插件
        self.plugins = []
        for name, provider_cls in TARGET_REGISTRY.items():
            # 动态获取平台配置 (如 self.cfg.wordpress)
            platform_cfg = getattr(self.cfg, name, None)
            if platform_cfg and getattr(platform_cfg, 'enabled', False):
                self.plugins.append(provider_cls(platform_cfg, site_url))
                logger.debug(f"📡 [分发引擎] 已激活平台插件: {name}")

    def syndicate(self, title, slug, content, metadata=None, rel_path=None, lang_code=None, is_dry_run=False, **kwargs):
        """
        🚀 广播发射：并发调用所有已激活的插件
        """
        if not self.plugins:
            return

        for plugin in self.plugins:
            self._dispatch_to_plugin(plugin, title, slug, content, metadata, rel_path, lang_code, is_dry_run)

    def _dispatch_to_plugin(self, plugin, title, slug, content, metadata, rel_path, lang_code, is_dry_run):
        """🛡️ 扁平化重构：原子化执行单平台分发"""
        try:
            if not plugin.is_enabled(rel_path, lang_code):
                return

            if is_dry_run:
                logger.info(f"🧪 [分发模拟] {plugin.__class__.__name__} -> {title}")
                return

            payload = plugin.format_payload(title, slug, content, metadata)
            plugin.push(payload)
            
        except Exception as e:
            logger.error(f"❌ [分发失败] {plugin.__class__.__name__}: {e}")