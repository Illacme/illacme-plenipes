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
            plugin_id = getattr(plugin, 'PLUGIN_ID', plugin.__class__.__name__).lower()
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
                task_name=f"Syndicate-{plugin.__class__.__name__}-{slug}"
            )

        if not is_dry_run and trigger_global_retry:
            global_executor.submit(
                self.process_pending_retries,
                priority=TaskPriority.SYNDICATION,
                task_name="Syndicate-Retry-Queue"
            )

    def _dispatch_to_plugin(self, plugin, title, slug, content, metadata, rel_path, lang_code, is_dry_run, **kwargs):
        """🛡️ 扁平化重构：原子化执行单平台分发"""
        target_id = getattr(plugin, 'PLUGIN_ID', plugin.__class__.__name__)
        try:
            if not plugin.is_enabled(rel_path, lang_code):
                return
                
            # 🚀 [V89.4] 物理幂等防重：首发启动前，先从待重试死信队列中将该文的老任务抹除，杜绝对端并发冲突
            if not is_dry_run and self.meta and rel_path:
                self.meta.mark_syndication_success(rel_path, target_id)

            try:
                processor = MarkdownASTProcessor()
                content = processor.adapt_format(content, plugin.PLUGIN_ID if hasattr(plugin, 'PLUGIN_ID') else target_id)
            except Exception as pe:
                tlog.warning(f"⚠️ [分发引擎] 单通道格式转换异常: {pe}")

            # 🚀 [V120.0] 全渠道生命周期物权检索：判断是否存在远程 ID 与内容哈希变动
            import hashlib
            cur_lang = lang_code or "zh"
            content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
            source_hash = metadata.get('source_hash', content_hash) if metadata else content_hash
            existing_record = self.meta.get_syndication_record(rel_path, cur_lang, target_id) if (self.meta and rel_path) else None
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
            if self.site_url:
                base_url = self.site_url.rstrip('/')
                if cur_lang and cur_lang.lower() not in ("zh", "zh-hans", "zh-cn", "default"):
                    canonical_url = f"{base_url}/{cur_lang}/posts/{slug}"
                else:
                    canonical_url = f"{base_url}/posts/{slug}"

            payload = plugin.format_payload(title, slug, content, metadata, canonical_url=canonical_url)
            res = plugin.push(payload, remote_id=remote_id)
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

            # 🚀 [V120.0] 记录分发成功及物权映射记录
            if not is_dry_run and self.meta and rel_path:
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
            if not is_dry_run and self.meta and rel_path:
                try:
                    self.meta.update_egress_status(rel_path, target_id, "FAILED", error=str(e))
                    if hasattr(self.meta, "save"):
                        self.meta.save()
                except Exception as ue:
                    tlog.error(f"❌ [分发状态写盘异常] {ue}")

                try:
                    # 过滤 metadata，确保可 json 序列化
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
        if not self.meta:
            return

        from core.logic.orchestration.task_orchestrator import global_executor, TaskPriority

        pending_tasks = self.meta.get_pending_syndication_tasks()
        if not pending_tasks:
            return

        tlog.info(f"🔄 [分发引擎] 发现 {len(pending_tasks)} 个待重试的持久化分发任务，正在拉起重试...")

        for task in pending_tasks:
            target_id = task.get("target_id")
            plugin = next((p for p in self.plugins if getattr(p, 'PLUGIN_ID', p.__class__.__name__) == target_id or p.__class__.__name__ == target_id), None)
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
            res = plugin.push(payload)
            published_url = None
            if isinstance(res, dict) and "url" in res:
                published_url = res["url"]

            if self.meta and rel_path:
                source_hash = metadata.get('source_hash', '') if metadata else ''
                self.meta.register_syndication(rel_path, target_id, source_hash)
                self.meta.mark_syndication_success(rel_path, target_id)
                self.meta.update_egress_status(rel_path, target_id, "DONE", url=published_url)
                tlog.info(f"✅ [重试成功] {target_id} 对 {rel_path} 的分发已成功重试并移出队列。")

        except Exception as e:
            tlog.error(f"❌ [重试失败] {target_id} -> {title}: {e}")
            if self.meta and rel_path:
                retry_count = task.get("retry_count", 0) + 1
                backoff_seconds = (2 ** retry_count) * 10
                self.meta.mark_syndication_failure(rel_path, target_id, str(e), backoff_seconds)
                self.meta.update_egress_status(rel_path, target_id, "FAILED", error=str(e))

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

    def delete_remote_article(self, rel_path: str, lang_code: str, target_id: str) -> dict:
        """🚀 [V120.0] 远程下架：调起插件的 delete 接口并清除物理账本映射"""
        if not self.meta: return {"ok": False, "error": "Meta ledger not initialized"}
        rec = self.meta.get_syndication_record(rel_path, lang_code, target_id)
        if not rec or not rec.get("remote_article_id"):
            return {"ok": False, "error": "未找到对应的远程文章映射记录"}

        remote_id = rec["remote_article_id"]
        plugin = next((p for p in self.plugins if getattr(p, 'PLUGIN_ID', p.__class__.__name__).lower() == target_id.lower()), None)
        if not plugin:
            return {"ok": False, "error": f"渠道插件 {target_id} 未激活或未装载"}

        if not hasattr(plugin, "delete"):
            return {
                "ok": False,
                "error": f"{target_id} 平台官方 API 不支持远程删除，建议点击右侧「🔗 解绑」并在该平台后台手动处理。"
            }

        try:
            success = plugin.delete(remote_id)
            if success:
                self.meta.delete_syndication_record(rel_path, lang_code, target_id)
                if hasattr(self.meta, "update_egress_status"):
                    self.meta.update_egress_status(rel_path, target_id, "pending", url="")
                    self.meta.save()
                tlog.info(f"🗑️ [物理下架与解绑成功] {rel_path} ({lang_code}) -> {target_id} (ID: {remote_id})")
                return {"ok": True, "message": f"文章 (ID: {remote_id}) 已从 {target_id} 成功物理下架。"}
            else:
                return {"ok": False, "error": f"{target_id} 平台返回下架失败。"}
        except NotImplementedError:
            return {
                "ok": False,
                "error": f"{target_id} 平台官方 API 不支持远程删除，建议点击右侧「🔗 解绑」并在该平台后台手动处理。"
            }
        except Exception as e:
            tlog.error(f"🛑 [远程下架异常] {target_id}: {e}")
            return {"ok": False, "error": str(e)}

    def unlink_remote_article(self, rel_path: str, lang_code: str, target_id: str) -> dict:
        """🚀 [V120.0] 本地解绑：仅从 SQLite 账本删除物理映射，不影响对端已发布的文章"""
        if not self.meta: return {"ok": False, "error": "Meta ledger not initialized"}
        self.meta.delete_syndication_record(rel_path, lang_code, target_id)
        if hasattr(self.meta, "update_egress_status"):
            self.meta.update_egress_status(rel_path, target_id, "pending", url="")
            self.meta.save()
        tlog.info(f"🔗 [本地解绑成功] {rel_path} ({lang_code}) -> {target_id}")
        return {"ok": True, "message": f"已解除 {target_id} 与该文章的本地绑定。"}
