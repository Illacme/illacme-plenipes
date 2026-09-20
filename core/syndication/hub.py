#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Content Syndicator (分发调度器)
模块职责：负责将内容异步分发至多个社交/发布平台。
🚀 [V33 终极纯净版]：实现 Zero-Touch 分发自发现。
"""

import os
from core.adapters.egress.publishers.base import BasePublisher
from core.adapters.syndication.targets import TARGET_REGISTRY
from core.utils.tracing import Tracer, tlog
from core.editorial.ast_processor import MarkdownASTProcessor
from core.syndication.hub_dispatcher_mixin import HubDispatcherMixin
from core.syndication.hub_management_mixin import HubManagementMixin

__all__ = ["ContentSyndicator", "HubDispatcherMixin", "HubManagementMixin"]


class ContentSyndicator(HubDispatcherMixin, HubManagementMixin):
    """
    全网聚合分发调度中枢。
    继承 HubDispatcherMixin 获得单通道流控与重试流水线能力；
    继承 HubManagementMixin 获得插件探查与文章生命周期管理能力。
    """

    def __init__(self, syndication_cfg, site_url, sys_tuning_cfg=None, meta=None):
        self.cfg = syndication_cfg
        self.site_url = site_url
        self.sys_tuning = sys_tuning_cfg or {}
        self.meta = meta
        self.breaker = None

        # 🚀 [V18.0] 主权复用：支持多账号/多站点动态映射
        self.plugins = []

        # 🚀 [V75.0] 深度架构对齐：直接从全局分发注册中心获取驱动
        class_map = TARGET_REGISTRY

        # 遍历配置字典，支持自定义键名 (如 devto_personal)
        for entry_id, entry_cfg in self.cfg.items():
            if not isinstance(entry_cfg, dict):
                continue

            has_credentials = any(
                k not in ("enabled", "proxy", "force_push", "published") and v and str(v).strip()
                for k, v in entry_cfg.items()
            )
            is_enabled = bool(entry_cfg.get('enabled', False))

            if not (is_enabled or has_credentials):
                continue

            # 推断平台类型：优先使用显式的 platform 字段，否则尝试从 ID 中提取
            platform_type = entry_cfg.get("platform")
            if not platform_type:
                for pid in class_map.keys():
                    if pid in entry_id.lower():
                        platform_type = pid
                        break

            p_cls = class_map.get(platform_type or entry_id)
            if p_cls:
                try:
                    # 🚀 [V75.1] 注入 site_url 以确保下游子插件自愈访问
                    if isinstance(self.sys_tuning, dict):
                        self.sys_tuning["site_url"] = self.site_url

                    # 实例化插件，传入该条目专属配置
                    instance = p_cls(entry_cfg, self.sys_tuning)
                    instance.instance_id = entry_id
                    self.plugins.append(instance)

                    tlog.info(f"📡 [分发引擎] 已激活主权节点: {entry_id} (类型: {platform_type or entry_id})")
                except Exception as e:
                    tlog.error(f"🛑 [分发引擎] 节点 {entry_id} 初始化失败: {e}")
            else:
                tlog.warning(f"⚠️ [分发引擎] 无法识别的节点类型: {entry_id}")

    def syndicate(self, title, slug, content, metadata=None, rel_path=None, lang_code=None, is_dry_run=False, trigger_global_retry=True, **kwargs):
        """
        🚀 广播发射：并发调用所有已激活的插件
        🚀 [V11.1] 接入全局调度执行器，实现统一优先级流控
        """
        if not self.plugins:
            return

        # 🚀 [阶段二：自动图床托管]
        vault_root = self.sys_tuning.get("vault_root") or os.getcwd()
        if rel_path:
            doc_abs_path = os.path.join(vault_root, rel_path)
            doc_dir = os.path.dirname(doc_abs_path)
        else:
            doc_dir = os.getcwd()

        try:
            from core.syndication.uploader import ImageUploader
            uploader = ImageUploader(self.cfg, self.sys_tuning)
            processor = MarkdownASTProcessor()
            content = processor.process_images(content, doc_dir, uploader.upload_image)

            # 🚀 [阶段二.1：全渠道封面公网转存防线]
            if metadata and isinstance(metadata, dict):
                raw_cov = metadata.get("cover") or metadata.get("cover_image") or metadata.get("banner")
                if raw_cov:
                    uploaded_cov = uploader.upload_cover(raw_cov, doc_dir=doc_dir)
                    if uploaded_cov:
                        metadata["cover"] = uploaded_cov
                        metadata["cover_image"] = uploaded_cov
                        metadata["banner"] = uploaded_cov
                        tlog.info(f"✨ [分发引擎] 封面图已成功转存公网直链: {uploaded_cov}")
        except Exception as pe:
            tlog.error(f"🛑 [分发引擎] AST 图片处理异常: {pe}")

        from core.logic.orchestration.task_orchestrator import global_executor, TaskPriority

        trace_id = Tracer.get_id() or "AEL-SYNDICATE"
        target_plugins = kwargs.get("target_plugins") or kwargs.get("platforms")
        if target_plugins and isinstance(target_plugins, list):
            target_plugins_lower = [str(p).lower() for p in target_plugins]
        else:
            target_plugins_lower = None

        for plugin in self.plugins:
            plugin_id = (getattr(plugin, 'PLUGIN_ID', None) or plugin.__class__.__name__).lower()
            instance_id = getattr(plugin, 'instance_id', plugin_id).lower()
            if target_plugins_lower is not None:
                if plugin_id not in target_plugins_lower and instance_id not in target_plugins_lower:
                    continue

            # 🚀 [V12.0] 注入熔断保护包装
            call_fn = self.breaker.call if self.breaker else lambda f, *a, **k: f(*a, **k)

            global_executor.submit(
                call_fn,
                self._dispatch_to_plugin,
                plugin, title, slug, content, metadata, rel_path, lang_code, is_dry_run,
                priority=TaskPriority.SYNDICATION,
                task_name=f"Syndicate-{plugin.__class__.__name__}-{slug}",
                **kwargs
            )

        if not is_dry_run and trigger_global_retry:
            global_executor.submit(
                self.process_pending_retries,
                priority=TaskPriority.SYNDICATION,
                task_name="Syndicate-Retry-Queue"
            )
