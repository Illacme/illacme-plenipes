#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Content Syndicator (分发调度器)
模块职责：负责将内容异步分发至多个社交/发布平台。
🚀 [V33 终极纯净版]：实现 Zero-Touch 分发自发现。
"""

import os
import logging
import hashlib
from core.adapters.egress.publishers.base import BasePublisher
from core.adapters.syndication.targets import TARGET_REGISTRY
from core.utils.tracing import Tracer, tlog
from core.editorial.ast_processor import MarkdownASTProcessor
class ContentSyndicator:
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
            if not isinstance(entry_cfg, dict) or not entry_cfg.get('enabled', False):
                continue
            
            # 推断平台类型：优先使用显式的 platform 字段，否则尝试从 ID 中提取
            platform_type = entry_cfg.get("platform")
            if not platform_type:
                # 模糊匹配：如果 entry_id 包含 wordpress，则推断为 wordpress
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
                    # 强制注入实例 ID (以便在审计时区分)
                    instance.instance_id = entry_id
                    self.plugins.append(instance)

                    tlog.info(f"📡 [分发引擎] 已激活主权节点: {entry_id} (类型: {platform_type or entry_id})")
                except Exception as e:
                    tlog.error(f"🛑 [分发引擎] 节点 {entry_id} 初始化失败: {e}")
            else:
                tlog.warning(f"⚠️ [分发引擎] 无法识别的节点类型: {entry_id}")

    def syndicate(self, title, slug, content, metadata=None, rel_path=None, lang_code=None, is_dry_run=False, **kwargs):
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
        except Exception as pe:
            tlog.error(f"🛑 [分发引擎] AST 图片处理异常: {pe}")

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

        if not is_dry_run:
            global_executor.submit(
                self.process_pending_retries,
                priority=TaskPriority.SYNDICATION,
                task_name="Syndicate-Retry-Queue"
            )

    def _dispatch_to_plugin(self, plugin, title, slug, content, metadata, rel_path, lang_code, is_dry_run):
        """🛡️ 扁平化重构：原子化执行单平台分发"""
        target_id = plugin.__class__.__name__
        try:
            if not plugin.is_enabled(rel_path, lang_code):
                return

            try:
                processor = MarkdownASTProcessor()
                content = processor.adapt_format(content, plugin.PLUGIN_ID if hasattr(plugin, 'PLUGIN_ID') else target_id)
            except Exception as pe:
                tlog.warning(f"⚠️ [分发引擎] 单通道格式转换异常: {pe}")

            # 🚀 [V11.1] 接入分发账本，实现断点续传与增量同步
            source_hash = metadata.get('source_hash', '') if metadata else ''

            if not is_dry_run and self.meta and rel_path:
                prev = self.meta.get_syndication_status(rel_path, target_id)
                if prev and prev.get('status') == "DONE" and prev.get('hash') == source_hash:
                    tlog.debug(f"⏭️ [分发跳过] {target_id} 对 {rel_path} 的同步已是最新。")
                    return

            if is_dry_run:
                tlog.info(f"🧪 [分发模拟] {plugin.__class__.__name__} -> {title}")
                return

            canonical_url = None
            if self.site_url:
                base_url = self.site_url.rstrip('/')
                canonical_url = f"{base_url}/posts/{slug}"

            payload = plugin.format_payload(title, slug, content, metadata, canonical_url=canonical_url)
            plugin.push(payload)

            # 🚀 [V11.1] 记录分发成功状态
            if not is_dry_run and self.meta and rel_path:
                self.meta.register_syndication(rel_path, target_id, source_hash)

        except Exception as e:
            tlog.error(f"❌ [分发失败] {target_id}: {e}")
            if not is_dry_run and self.meta and rel_path:
                self.meta.enqueue_syndication_retry(
                    rel_path=rel_path,
                    target_id=target_id,
                    title=title,
                    slug=slug,
                    content=content,
                    metadata=metadata,
                    lang_code=lang_code,
                    error_msg=str(e)
                )

    def process_pending_retries(self):
        """🚀 扫描持久化重试队列，取出待执行 of 重试任务并调度执行"""
        if not self.meta:
            return

        from core.logic.orchestration.task_orchestrator import global_executor, TaskPriority

        pending_tasks = self.meta.get_pending_syndication_tasks()
        if not pending_tasks:
            return

        tlog.info(f"🔄 [分发引擎] 发现 {len(pending_tasks)} 个待重试的持久化分发任务，正在拉起重试...")

        for task in pending_tasks:
            target_id = task.get("target_id")
            plugin = next((p for p in self.plugins if p.__class__.__name__ == target_id), None)
            if not plugin:
                tlog.warning(f"⚠️ [分发重试] 无法重试：对应的分发插件未激活或不存在: {target_id}")
                continue

            call_fn = self.breaker.call if self.breaker else lambda f, *a, **k: f(*a, **k)
            global_executor.submit(
                call_fn,
                self._dispatch_retry_task,
                plugin, task,
                priority=TaskPriority.SYNDICATION,
                task_name=f"Retry-Syndicate-{target_id}-{task.get('slug')}"
            )

    def _dispatch_retry_task(self, plugin, task):
        """🛡️ 执行单个重试任务"""
        rel_path = task.get("rel_path")
        target_id = task.get("target_id")
        title = task.get("title")
        slug = task.get("slug")
        content = task.get("content")
        metadata = task.get("metadata")
        lang_code = task.get("lang_code")

        try:
            if not plugin.is_enabled(rel_path, lang_code):
                self.meta.mark_syndication_success(rel_path, target_id)
                return

            try:
                processor = MarkdownASTProcessor()
                content = processor.adapt_format(content, plugin.PLUGIN_ID if hasattr(plugin, 'PLUGIN_ID') else target_id)
            except Exception as pe:
                tlog.warning(f"⚠️ [分发引擎] 重试通道格式转换异常: {pe}")

            canonical_url = None
            if self.site_url:
                base_url = self.site_url.rstrip('/')
                canonical_url = f"{base_url}/posts/{slug}"

            payload = plugin.format_payload(title, slug, content, metadata, canonical_url=canonical_url)
            plugin.push(payload)

            if self.meta and rel_path:
                source_hash = metadata.get('source_hash', '') if metadata else ''
                self.meta.register_syndication(rel_path, target_id, source_hash)
                self.meta.mark_syndication_success(rel_path, target_id)
                tlog.info(f"✅ [重试成功] {target_id} 对 {rel_path} 的分发已成功重试并移出队列。")

        except Exception as e:
            tlog.error(f"❌ [重试失败] {target_id} -> {title}: {e}")
            retry_count = task.get("retry_count", 0) + 1
            backoff_seconds = (2 ** retry_count) * 10
            self.meta.mark_syndication_failure(rel_path, target_id, str(e), backoff_seconds)

    def list_all_plugins(self):
        """🚀 [V17.0] 枚举所有已发现的外部插件及其状态"""
        report = []
        # 🚀 [V75.0] 对正：从注册中心枚举
        for p_id, p_cls in TARGET_REGISTRY.items():
            platform_cfg = getattr(self.cfg, p_id, None)
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
                "id": p_id,
                "class": p_cls.__name__,
                "status": status,
                "missing": missing_reqs
            })
        return report
