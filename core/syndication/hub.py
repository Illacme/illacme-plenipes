#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Content Syndicator (分发调度器)
模块职责：负责将内容异步分发至多个社交/发布平台。
🚀 [V33 终极纯净版]：实现 Zero-Touch 分发自发现。
"""

import os
import logging
from core.utils.plugin_loader import PluginLoader
from plugins.publishers.base import BasePublisher
from core.utils.tracing import Tracer, tlog

class ContentSyndicator:
    """
    🚀 内容分发调度中心 (V17.0 模块化版)
    负责从 plugins/publishers/ 动态加载插件并执行分发。
    """
    def __init__(self, syndication_cfg, site_url, sys_tuning_cfg=None, meta=None):
        self.cfg = syndication_cfg
        self.site_url = site_url
        self.sys_tuning = sys_tuning_cfg or {}
        self.meta = meta
        self.breaker = None

        # 🚀 [V17.0] 动态加载外部插件
        self.plugins = []
        plugin_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "plugins", "publishers")
        discovered_classes = PluginLoader.load_plugins(plugin_dir, BasePublisher)
        
        for p_cls in discovered_classes:
            plugin_id = getattr(p_cls, "PLUGIN_ID", p_cls.__name__.lower())
            platform_cfg = getattr(self.cfg, plugin_id, None)
            
            if platform_cfg and getattr(platform_cfg, 'enabled', False):
                self.plugins.append(p_cls(platform_cfg, sys_tuning_cfg))
                tlog.info(f"📡 [分发引擎] 已激活外部插件: {plugin_id}")

    def syndicate(self, title, slug, content, metadata=None, rel_path=None, lang_code=None, is_dry_run=False, **kwargs):
        """
        🚀 广播发射：并发调用所有已激活的插件
        🚀 [V11.1] 接入全局调度执行器，实现统一优先级流控
        """
        if not self.plugins:
            return

        from core.logic.orchestration.task_orchestrator import global_executor, TaskPriority

        trace_id = Tracer.get_id() or "AEL-SYNDICATE"
        for plugin in self.plugins:
            # 🚀 [V12.0] 注入熔断保护包装
            call_fn = self.breaker.call if self.breaker else lambda f, *a, **k: f(*a, **k)

            global_executor.submit(
                call_fn,
                self._dispatch_to_plugin,
                plugin, title, slug, content, metadata, rel_path, lang_code, is_dry_run,
                priority=TaskPriority.SYNDICATION,
                task_name=f"Syndicate-{plugin.__class__.__name__}-{slug}"
            )

    def _dispatch_to_plugin(self, plugin, title, slug, content, metadata, rel_path, lang_code, is_dry_run):
        """🛡️ 扁平化重构：原子化执行单平台分发"""
        try:
            if not plugin.is_enabled(rel_path, lang_code):
                return

            # 🚀 [V11.1] 接入分发账本，实现断点续传与增量同步
            target_id = plugin.__class__.__name__
            source_hash = metadata.get('source_hash', '') if metadata else ''

            if not is_dry_run and self.meta and rel_path:
                prev = self.meta.get_syndication_status(rel_path, target_id)
                if prev and prev.get('hash') == source_hash and prev.get('status') == "DONE":
                    tlog.debug(f"⏭️ [分发跳过] {target_id} 对 {rel_path} 的同步已是最新。")
                    return

            if is_dry_run:
                tlog.info(f"🧪 [分发模拟] {plugin.__class__.__name__} -> {title}")
                return

            payload = plugin.format_payload(title, slug, content, metadata)
            plugin.push(payload)

            # 🚀 [V11.1] 记录分发成功状态
            if not is_dry_run and self.meta and rel_path:
                self.meta.register_syndication(rel_path, target_id, source_hash)

        except Exception as e:
            tlog.error(f"❌ [分发失败] {plugin.__class__.__name__}: {e}")

    def list_all_plugins(self):
        """🚀 [V17.0] 枚举所有已发现的外部插件及其状态"""
        report = []
        plugin_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "plugins", "publishers")
        discovered_classes = PluginLoader.load_plugins(plugin_dir, BasePublisher)

        for p_cls in discovered_classes:
            plugin_id = getattr(p_cls, "PLUGIN_ID", p_cls.__name__.lower())
            platform_cfg = getattr(self.cfg, plugin_id, None)
            is_enabled = platform_cfg and getattr(platform_cfg, 'enabled', False)

            # 检查依赖 (V11.3 契约)
            reqs = getattr(p_cls, 'REQUIRED_PACKAGES', [])
            missing_reqs = []
            import importlib.util
            for req in reqs:
                if importlib.util.find_spec(req) is None:
                    missing_reqs.append(req)

            status = "ACTIVE" if is_enabled and not missing_reqs else "INACTIVE"
            if is_enabled and missing_reqs: status = "DEP_MISSING"

            report.append({
                "id": plugin_id,
                "class": p_cls.__name__,
                "status": status,
                "missing": missing_reqs
            })
        return report
