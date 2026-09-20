#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Content Syndicator Dispatcher Mixin
职责：提供单插件分发调度、幂等查重、AST 格式适配、账本写入与失败死信队列重试调度。
"""

import hashlib
from core.editorial.ast_processor import MarkdownASTProcessor
from core.utils.tracing import tlog
from core.utils.language_hub import LanguageHub


class HubDispatcherMixin:
    """分发调度与重试流水线 Mixin"""

    def _dispatch_to_plugin(self, plugin, title, slug, content, metadata, rel_path, lang_code, is_dry_run, **kwargs):
        """🛡️ 扁平化重构：原子化执行单平台分发"""
        target_id = getattr(plugin, 'PLUGIN_ID', None) or plugin.__class__.__name__
        try:
            force_push = kwargs.get('force_push', False)
            if not force_push and not plugin.is_enabled(rel_path, lang_code):
                return

            if not is_dry_run and getattr(self, "meta", None) and rel_path:
                self.meta.mark_syndication_success(rel_path, target_id)

            cur_lang = lang_code
            if not cur_lang or str(cur_lang).lower() in ("auto", "source", ""):
                cur_lang = LanguageHub.resolve_document_language(
                    content=content,
                    fm=metadata,
                    default_fallback="zh-Hans"
                )

            try:
                processor = MarkdownASTProcessor()
                content = processor.adapt_format(
                    content,
                    target_platform=getattr(plugin, 'PLUGIN_ID', target_id),
                    site_url=getattr(self, 'site_url', ''),
                    slug=slug,
                    fm=metadata
                )
                metadata = processor.sanitize_metadata(
                    metadata=metadata,
                    target_platform=getattr(plugin, 'PLUGIN_ID', target_id),
                    site_url=getattr(self, 'site_url', ''),
                    slug=slug,
                    doc_id=rel_path,
                    lang_code=cur_lang
                )
            except Exception as pe:
                tlog.warning(f"⚠️ [分发引擎] 单通道格式转换异常: {pe}")

            content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
            source_hash = metadata.get('source_hash', content_hash) if metadata else content_hash
            existing_record = self.meta.get_syndication_record(rel_path, cur_lang, target_id) if (getattr(self, "meta", None) and rel_path) else None
            remote_id = existing_record.get('remote_article_id') if existing_record else None

            if not is_dry_run and existing_record and not kwargs.get('force_push', False):
                if existing_record.get('content_hash') == content_hash:
                    tlog.info(f"✨ [分发对正] {target_id} 对 {rel_path} ({cur_lang}) 内容无变动，自动跳过 (Remote ID: {remote_id})")
                    if self.meta and rel_path:
                        self.meta.update_egress_status(
                            rel_path, target_id, "SKIPPED",
                            url=existing_record.get('remote_url')
                        )
                    return

            if is_dry_run:
                action_type = "UPDATE" if remote_id else "CREATE"
                tlog.info(f"🧪 [分发模拟] [{action_type}] {plugin.__class__.__name__} -> {title} (Remote ID: {remote_id})")
                return

            canonical_url = None
            site_url = getattr(self, "site_url", "")
            if site_url:
                base_url = site_url.rstrip('/')
                if cur_lang and cur_lang.lower() not in ("zh", "zh-hans", "zh-cn", "default"):
                    canonical_url = f"{base_url}/{cur_lang}/posts/{slug}"
                else:
                    canonical_url = f"{base_url}/posts/{slug}"

            payload = plugin.format_payload(title, slug, content, metadata, canonical_url=canonical_url)
            try:
                res = plugin.push(payload, remote_id=remote_id)
            except TypeError as te:
                if "remote_id" in str(te):
                    res = plugin.push(payload)
                else:
                    raise te

            published_url = None
            is_draft = False
            dashboard_url = None
            res_remote_id = remote_id
            if isinstance(res, dict):
                if "url" in res:
                    published_url = res["url"]
                is_draft = bool(res.get("draft"))
                dashboard_url = res.get("dashboard_url")
                if res.get("remote_id"):
                    res_remote_id = str(res["remote_id"])
                elif res.get("media_id"):
                    res_remote_id = str(res["media_id"])

            if not is_dry_run and getattr(self, "meta", None) and rel_path:
                self.meta.register_syndication(rel_path, target_id, source_hash)
                if res_remote_id:
                    self.meta.save_syndication_record(
                        rel_path=rel_path,
                        lang_code=cur_lang,
                        target_id=target_id,
                        remote_article_id=res_remote_id,
                        remote_url=published_url or (existing_record.get('remote_url') if existing_record else None),
                        content_hash=content_hash
                    )
                if is_draft:
                    self.meta.update_egress_status(rel_path, target_id, "DRAFT", url=dashboard_url or published_url)
                else:
                    self.meta.update_egress_status(rel_path, target_id, "DONE", url=published_url)
                if hasattr(self.meta, "save"):
                    self.meta.save()

        except Exception as e:
            tlog.error(f"❌ [分发失败] {target_id}: {e}")
            if not is_dry_run and getattr(self, "meta", None) and rel_path:
                try:
                    self.meta.update_egress_status(rel_path, target_id, "FAILED", error=str(e))
                    if hasattr(self.meta, "save"):
                        self.meta.save()
                except Exception as ue:
                    tlog.error(f"❌ [分发状态写盘异常] {ue}")

                try:
                    safe_meta = {}
                    if isinstance(metadata, dict):
                        for k, v in metadata.items():
                            if isinstance(v, (str, int, float, bool, list, dict)) or v is None:
                                safe_meta[k] = v
                    self.meta.enqueue_syndication_retry(
                        rel_path=rel_path,
                        target_id=target_id,
                        title=title,
                        slug=slug,
                        content=content,
                        metadata=safe_meta,
                        lang_code=lang_code,
                        error_msg=str(e)
                    )
                except Exception as qe:
                    tlog.warning(f"⚠️ [分发入队重试忽略] {qe}")

    def process_pending_retries(self):
        """🚀 扫描持久化重试队列，取出待执行 of 重试任务并调度执行"""
        if not getattr(self, "meta", None):
            return

        from core.logic.orchestration.task_orchestrator import global_executor, TaskPriority

        pending_tasks = self.meta.get_pending_syndication_tasks()
        if not pending_tasks:
            return

        tlog.info(f"🔄 [分发引擎] 发现 {len(pending_tasks)} 个待重试的持久化分发任务，正在拉起重试...")

        plugins = getattr(self, "plugins", [])
        for task in pending_tasks:
            target_id = task.get("target_id")
            plugin = next((p for p in plugins if getattr(p, 'PLUGIN_ID', p.__class__.__name__) == target_id or p.__class__.__name__ == target_id), None)
            if not plugin:
                tlog.warning(f"⚠️ [分发重试] 无法重试：对应的分发插件未激活或不存在: {target_id}")
                continue

            breaker = getattr(self, "breaker", None)
            call_fn = breaker.call if breaker else lambda f, *a, **k: f(*a, **k)
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
                if getattr(self, "meta", None):
                    self.meta.mark_syndication_success(rel_path, target_id)
                return

            try:
                processor = MarkdownASTProcessor()
                content = processor.adapt_format(content, plugin.PLUGIN_ID if hasattr(plugin, 'PLUGIN_ID') else target_id)
            except Exception as pe:
                tlog.warning(f"⚠️ [分发引擎] 重试通道格式转换异常: {pe}")

            canonical_url = None
            site_url = getattr(self, "site_url", "")
            if site_url:
                base_url = site_url.rstrip('/')
                canonical_url = f"{base_url}/posts/{slug}"

            payload = plugin.format_payload(title, slug, content, metadata, canonical_url=canonical_url)
            res = plugin.push(payload)
            published_url = None
            if isinstance(res, dict) and "url" in res:
                published_url = res["url"]

            if getattr(self, "meta", None) and rel_path:
                source_hash = metadata.get('source_hash', '') if metadata else ''
                self.meta.register_syndication(rel_path, target_id, source_hash)
                self.meta.mark_syndication_success(rel_path, target_id)
                self.meta.update_egress_status(rel_path, target_id, "DONE", url=published_url)
                tlog.info(f"✅ [重试成功] {target_id} 对 {rel_path} 的分发已成功重试并移出队列。")

        except Exception as e:
            tlog.error(f"❌ [重试失败] {target_id} -> {title}: {e}")
            if getattr(self, "meta", None) and rel_path:
                retry_count = task.get("retry_count", 0) + 1
                backoff_seconds = (2 ** retry_count) * 10
                self.meta.mark_syndication_failure(rel_path, target_id, str(e), backoff_seconds)
                self.meta.update_egress_status(rel_path, target_id, "FAILED", error=str(e))
