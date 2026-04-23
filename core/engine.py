#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Main Engine (Pipeline Driven)
模块职责：全局生命周期调度总线。
架构进化：引入 Context + Pipeline 模式，彻底消灭上帝函数。
🛡️ [AEL-Iter-v5.3]：基于 EngineFactory 的架构分层版本。
"""

import os
import time
import fnmatch
import logging
import threading
from datetime import datetime

from .config.config import Configuration
from .utils import normalize_keywords, extract_frontmatter
from .ai_scheduler import AIScheduler
from .pipeline.context import SyncContext
from .pipeline.runner import Pipeline
from .pipeline.staticizer import StaticizerStep
from .pipeline.steps import (
    ReadAndNormalizeStep, 
    ASTAndPurifyStep, 
    MetadataAndHashStep, 
    AISlugAndSEOStep, 
    ContextualImageAltStep,
    MaskingAndRoutingStep
)
from .engine_factory import EngineFactory

logger = logging.getLogger("Illacme.plenipes")

class IllacmeEngine:
    def __init__(self, config_path, no_ai=False):
        # 🚀 [TDR-Iter-021] 初始化锁与状态容器
        self._processing_locks = {}
        self._global_engine_lock = threading.Lock()
        
        # 🚀 [TDR-Iter-021] 委托工厂类执行复杂的组件装配与配置映射
        EngineFactory.assemble_components(self, config_path, no_ai)

    def _get_document_lock(self, rel_path):
        with self._global_engine_lock:
            if rel_path not in self._processing_locks:
                self._processing_locks[rel_path] = threading.Lock()
            return self._processing_locks[rel_path]

    def _is_excluded(self, rel_path):
        for p in self.pub_cfg.exclude_patterns:
            if fnmatch.fnmatch(rel_path, p) or fnmatch.fnmatch(os.path.basename(rel_path), p): return True
        return False

    def get_lang_name_by_code(self, code):
        """🚀 映射助手：根据语种代码获取对应的自然语言名称"""
        src_cfg = self.i18n.source
        if src_cfg.lang_code == code:
            return src_cfg.name or 'Chinese'
        
        for target in self.i18n.targets:
            if target.lang_code == code:
                return target.name or code
        
        fallback_map = {'en': 'English', 'zh-cn': 'Chinese', 'ja': 'Japanese', 'ko': 'Korean'}
        return fallback_map.get(code.lower(), code)

    def sync_document(self, src_path, route_prefix, route_source, is_dry_run=False, force_sync=False):
        """🚀 核心管线调度枢纽"""
        vault_path = self.paths.get('vault', '.')
        rel_path = os.path.relpath(src_path, vault_path).replace('\\', '/')
        if self._is_excluded(rel_path): return

        doc_lock = self._get_document_lock(rel_path)
        if not doc_lock.acquire(blocking=False): return

        try:
            cli_force = force_sync
            
            # 1. 状态自愈探针
            if not force_sync and self.paths.get('target_base'):
                doc_info = self.meta.get_doc_info(rel_path)
                if doc_info and doc_info.get('source_hash') and doc_info.get('slug'):
                    slug = doc_info.get('slug')
                    target_files_missing = False
                    
                    vault_path = self.paths.get('vault', '.')
                    t_abs = os.path.join(vault_path, rel_path)
                    t_sub_dir = os.path.dirname(os.path.relpath(t_abs, os.path.join(vault_path, route_source)).replace('\\', '/')).replace('\\', '/')
                    if t_sub_dir == '.': t_sub_dir = ""
                    mapped_sub_dir = self.route_manager.get_mapped_sub_dir(t_sub_dir, is_dry_run=is_dry_run, allow_ai=False)
                    ext = os.path.splitext(rel_path)[1].lower()
                    
                    langs_to_check = [self.i18n.source.lang_code] if self.i18n.source.lang_code else []
                    if self.i18n.enabled:
                        langs_to_check.extend([t.lang_code for t in self.i18n.targets if t.lang_code])
                            
                    for code in langs_to_check:
                        target_base = self.paths.get('target_base')
                        if not target_base: continue
                        expected_dest = self.route_manager.resolve_physical_path(
                            target_base, code, route_prefix, mapped_sub_dir, slug, ext
                        )
                        if not os.path.exists(expected_dest):
                            target_files_missing = True
                            break
                            
                    if target_files_missing:
                        logger.info(f"🩹 [状态机自愈] {rel_path}：检测到前端物理产物丢失，触发重建！")
                        force_sync = True

            # 2. 组装上下文与管线
            ctx = SyncContext(self, src_path, route_prefix, route_source, is_dry_run, force_sync)
            ctx.services.staticizer = self.staticizer
            ctx.services.translator = self.translator
            ctx.services.meta = self.meta
            
            self.timeline.log_event("SYNC", ctx.rel_path, "PENDING", "管线启动")

            self.timeline.log_event("SYNC", ctx.rel_path, "PENDING", "管线启动")

            # 🚀 [V33] 使用工厂预装配的动态管线，彻底消灭硬编码
            ctx.pipeline = self.pipeline

            if self.no_ai:
                ctx.is_silent_edit = True
                ctx.ai_health_flag[0] = False

            self.pipeline.execute(ctx)
            if ctx.is_aborted: 
                return "SKIP" if getattr(ctx, 'is_skipped', False) else "OFFLINE"

            # 3. 后置阶段：SEO 注入与分发
            if self.no_ai:
                persistence_date = datetime.now().strftime("%Y-%m-%d")
                primary_shadow_hash, persistence_date = self.dispatcher.dispatch(self.asset_index, ctx.title, ctx.slug, ctx.masked_source, ctx.base_fm, rel_path, self.i18n.source.lang_code or 'zh', ctx.route_prefix, ctx.route_source, ctx.mapped_sub_dir, ctx.masks, ctx.is_dry_run, force_persistence_date=persistence_date)
            else:
                def inject_seo(fm, lang_code, text_content):
                    if not self.seo_cfg.enabled: return fm
                    lang_name = self.get_lang_name_by_code(lang_code)
                    seo_data, success = self.translator.generate_seo_metadata(text_content, lang_name, ctx.is_dry_run)
                    if success and seo_data:
                        if self.seo_cfg.generate_description: fm['description'] = seo_data.get('description', '')
                        if self.seo_cfg.generate_keywords: fm['keywords'] = normalize_keywords(seo_data.get('keywords', ''))
                    return fm

                primary_shadow_hash = ""
                src_code = self.i18n.source.lang_code or 'zh-cn'
                src_fm = ctx.base_fm.copy()
                if ctx.seo_data:
                    src_fm.update(ctx.seo_data)
                    if 'keywords' in src_fm: src_fm['keywords'] = normalize_keywords(src_fm['keywords'])
                
                doc_info = self.meta.get_doc_info(rel_path)
                can_recover = (not cli_force and doc_info.get("source_hash") == ctx.current_hash and not ctx.is_silent_edit)
                ext = os.path.splitext(rel_path)[1].lower()
                shadow_path = self.paths.get('shadow')
                if not shadow_path: shadow_src_path = ""
                else: shadow_src_path = self.route_manager.resolve_physical_path(shadow_path, src_code, route_prefix, ctx.mapped_sub_dir, ctx.slug, ext)
                
                if can_recover and os.path.exists(shadow_src_path):
                    logger.debug(f"⚡️ [影子自愈] {rel_path} 命中影子资产。")
                    try:
                        with open(shadow_src_path, 'r', encoding='utf-8') as sf:
                            s_fm, _ = extract_frontmatter(sf.read())
                            src_fm.update({'description': s_fm.get('description', ''), 'keywords': s_fm.get('keywords', [])})
                            ctx.seo_data = {'description': s_fm.get('description', ''), 'keywords': s_fm.get('keywords', [])}
                    except Exception: pass
                elif not ctx.is_silent_edit:
                    src_fm = inject_seo(src_fm, src_code, ctx.body_content)
                    ctx.seo_data = {'description': src_fm.get('description', ''), 'keywords': src_fm.get('keywords', '')}

                if can_recover and shadow_src_path and os.path.exists(shadow_src_path):
                    target_base = self.paths.get('target_base', '.')
                    display_dest = self.route_manager.resolve_physical_path(target_base, src_code, route_prefix, ctx.mapped_sub_dir, ctx.slug, ext)
                    logger.info(f"🔄 [同步跳过] {rel_path} -> {os.path.relpath(display_dest, target_base)}")
                    self.timeline.update_event_status(rel_path, "SKIP", "内容未变")
                    return "SKIP"
                
                primary_shadow_hash, persistence_date = self.dispatcher.dispatch(self.asset_index, ctx.title, ctx.slug, ctx.masked_source, src_fm, rel_path, src_code, ctx.route_prefix, ctx.route_source, ctx.mapped_sub_dir, ctx.masks, ctx.is_dry_run, node_assets=ctx.node_assets, node_ext_assets=ctx.node_ext_assets, node_outlinks=ctx.node_outlinks, assets_lock=ctx.assets_lock)
                AIScheduler.dispatch_targets(self, ctx, inject_seo, route_prefix, route_source, cli_force, rel_path, is_dry_run, persistence_date=persistence_date)

            # 4. 终态记录
            if not ctx.is_dry_run:
                self.meta.register_document(ctx.rel_path, ctx.title, slug=ctx.slug, source_hash=ctx.current_hash if ctx.ai_health_flag[0] else "", shadow_hash=primary_shadow_hash, seo_data=ctx.seo_data, route_prefix=ctx.route_prefix, route_source=ctx.route_source, assets=list(ctx.node_assets), ext_assets=list(ctx.node_ext_assets), outlinks=list(ctx.node_outlinks), persistent_date=persistence_date)
                self.meta.save()
                
                status = "UPDATED" if ctx.ai_health_flag[0] else "DEGRADED"
                self.timeline.update_event_status(ctx.rel_path, status, f"资产: {len(ctx.node_assets)}")
                if status == "UPDATED" and not ctx.is_silent_edit:
                    self.broadcaster.broadcast(ctx.title, ctx.rel_path, src_code, ctx.mapped_sub_dir, ctx.slug)
                return status

            if hasattr(self, 'sentinel'): self.sentinel.verify_docs_sync_hook(rel_path)
            return "UPDATED"

        except Exception as e:
            self.timeline.update_event_status(rel_path, "ERROR", str(e))
            logger.error(f"❌ 处理错误 {rel_path}: {e}")
            return "ERROR"
        finally:
            doc_lock.release()