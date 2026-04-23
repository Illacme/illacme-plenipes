#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Pipeline Steps
模块职责：单向流水线的具体加工工序。
🛡️ [AEL-Iter-v5.3]：基于分层架构的 TDR 复健版本。
"""

import os
import re
import time
import hashlib
import logging
import shutil
from ..utils import extract_frontmatter, strip_technical_noise, normalize_keywords
from .runner import PipelineStep
from .image_step import ContextualImageAltStep

logger = logging.getLogger("Illacme.plenipes")

class ReadAndNormalizeStep(PipelineStep):
    """阶段 3-4: 物理读取与编辑器方言抹平"""
    PLUGIN_ID = "read_normalize"
    def process(self, ctx):
        try:
            with open(ctx.src_path, 'r', encoding='utf-8') as f:
                ctx.raw_content = f.read()
        except Exception as e:
            logger.error(f"🛑 读取失败 {ctx.src_path}: {e}")
            ctx.is_aborted = True
            return

        fm_dict, raw_body = extract_frontmatter(ctx.raw_content)
        ctx.raw_body, ctx.fm_dict = ctx.engine.input_adapter.normalize(raw_body, fm_dict)
        
        raw_ai_sync = ctx.fm_dict.get('ai_sync')
        ctx.is_silent_edit = (str(raw_ai_sync).lower() == 'false') if raw_ai_sync is not None else False

class ASTAndPurifyStep(PipelineStep):
    """阶段 6-7: AST 降维与语义提纯"""
    PLUGIN_ID = "purify"
    def process(self, ctx):
        ctx.body_content = ctx.engine.transclusion_resolver.expand(ctx.raw_body)
        if ctx.services.staticizer:
            ctx.services.staticizer.staticize_callouts(ctx.body_content, ctx.engine.ssg_adapter)

        purify_opts = ctx.engine.config.system.ai_context_purification
        ctx.ai_pure_body = strip_technical_noise(ctx.body_content, purify_opts)
        
        substance_threshold = ctx.engine.config.translation.empty_content_threshold
        is_empty = len(ctx.ai_pure_body.strip()) < substance_threshold
        is_draft = str(ctx.fm_dict.get('draft')).lower() == 'true' or str(ctx.fm_dict.get('publish')).lower() == 'false'
        
        if is_empty or is_draft:
            if ctx.engine.meta.get_doc_info(ctx.rel_path):
                ctx.engine.janitor.gc_node(ctx.rel_path, ctx.route_prefix, ctx.route_source, ctx.is_dry_run)
            ctx.is_aborted = True

class MetadataAndHashStep(PipelineStep):
    """阶段 8-9: 元数据注入与指纹核验"""
    PLUGIN_ID = "metadata_hash"
    def process(self, ctx):
        defaults = ctx.engine.fm_defaults or {}
        ctx.base_fm = {k: v for k, v in defaults.items() if v is not None and str(v).strip() != ""}
        ctx.base_fm.update(ctx.fm_dict)
        
        for f in ['keywords', 'tags', 'categories']:
            if f in ctx.base_fm: ctx.base_fm[f] = normalize_keywords(ctx.base_fm.get(f))
        
        if 'slug' in ctx.base_fm: ctx.base_fm.pop('slug', None)
        ctx.current_hash = hashlib.md5((str(ctx.base_fm) + ctx.body_content).encode('utf-8')).hexdigest()
        
        old_info = ctx.engine.meta.get_doc_info(ctx.rel_path)
        ctx.engine.meta.register_document(ctx.rel_path, ctx.title, source_hash=ctx.current_hash)
        ctx.doc_info = ctx.engine.meta.get_doc_info(ctx.rel_path)
        
        if not old_info.get("slug"):
            hit = ctx.engine.meta.find_by_hash(ctx.current_hash)
            if hit and hit.get("slug"):
                ctx.engine.meta.register_document(ctx.rel_path, ctx.title, slug=hit.get("slug"), seo_data=hit.get("seo"), shadow_hash=hit.get("shadow_hash"))
                self._handle_shadow_roaming(ctx, hit)
                ctx.doc_info = ctx.engine.meta.get_doc_info(ctx.rel_path)

        if not ctx.force_sync and old_info.get("source_hash") == ctx.current_hash: 
            ctx.is_skipped = True
            ctx.is_aborted = True

    def _handle_shadow_roaming(self, ctx, hit):
        try:
            ext = os.path.splitext(ctx.rel_path)[1].lower()
            vault_path = ctx.engine.paths.get('vault', '.')
            shadow_path = ctx.engine.paths.get('shadow')
            if not shadow_path: return

            for t in ctx.engine.config.i18n_settings.targets:
                code = t.get('lang_code')
                if not code: continue
                
                old_rel = hit.get('_rel_path')
                old_src = hit.get('source')
                old_sub = os.path.dirname(os.path.relpath(os.path.join(vault_path, old_rel), os.path.join(vault_path, old_src))).replace('\\', '/')
                if old_sub == '.': old_sub = ""
                old_mapped = ctx.engine.route_manager.get_mapped_sub_dir(old_sub, allow_ai=False)
                
                old_shadow = ctx.engine.route_manager.resolve_physical_path(shadow_path, code, hit.get('prefix'), old_mapped, hit.get('slug'), ext)
                if os.path.exists(old_shadow):
                    sub = os.path.dirname(os.path.relpath(ctx.src_path, os.path.join(vault_path, ctx.route_source))).replace('\\', '/')
                    if sub == '.': sub = ""
                    new_mapped = ctx.engine.route_manager.get_mapped_sub_dir(sub, allow_ai=False)
                    new_shadow = ctx.engine.route_manager.resolve_physical_path(shadow_path, code, ctx.route_prefix, new_mapped, hit.get('slug'), ext)
                    
                    if old_shadow != new_shadow:
                        os.makedirs(os.path.dirname(new_shadow), exist_ok=True)
                        shutil.copy2(old_shadow, new_shadow)
        except Exception: pass

class AISlugAndSEOStep(PipelineStep):
    """阶段 11-12: Slug 重塑与 SEO 引擎"""
    PLUGIN_ID = "ai_slug_seo"
    def process(self, ctx):
        slug_raw = ctx.doc_info.get("slug")
        if slug_raw and ('%' in slug_raw or bool(re.search(r'[\u4e00-\u9fa5]', slug_raw)) or len(slug_raw) > 100):
            slug_raw = None
        
        if not slug_raw:
            slug_mode = ctx.engine.config.translation.slug_mode
            if slug_mode == 'ai' and not ctx.is_silent_edit:
                if ctx.is_dry_run: slug_raw, slug_success = f"dry-run-{int(time.time())}", True
                else:
                    try: slug_raw, slug_success = ctx.engine.translator.generate_slug(ctx.title, is_dry_run=False)
                    except Exception: slug_success, slug_raw = False, None
                if not slug_success: ctx.ai_health_flag[0] = False
            else:
                english_only = re.sub(r'[^a-z0-9\-]', '', ctx.title.lower().replace(' ', '-'))
                slug_raw = re.sub(r'-+', '-', english_only).strip('-') or f"doc-{hashlib.md5(ctx.title.encode('utf-8')).hexdigest()[:6]}"
                
        ctx.slug = slug_raw
        ctx.seo_data = ctx.doc_info.get("seo", {})
        if not ctx.is_silent_edit and ('description' in ctx.seo_data or 'keywords' in ctx.seo_data): ctx.seo_data = {}

class MaskingAndRoutingStep(PipelineStep):
    """阶段 13-14: 物理遮蔽与动态路由推导"""
    PLUGIN_ID = "masking_routing"
    def process(self, ctx):
        def mask_fn(m):
            matched = m.group(0)
            link_match = re.match(r'^(\!?\[.*?\]\()([^)]+)(\))$', matched)
            if link_match:
                prefix, url_part, suffix = link_match.groups()
                if prefix.startswith('!['):
                    ctx.masks.append(matched)
                    return f"[[STB_MASK_{len(ctx.masks)-1}]]"
                else:
                    ctx.masks.append(f"URL_ONLY_LNK:{url_part}")
                    return f"{prefix}[[STB_MASK_{len(ctx.masks)-1}]]{suffix}"
            ctx.masks.append(matched)
            return f"[[STB_MASK_{len(ctx.masks)-1}]]"
        
        mask_pattern = r'\$\$.*?\$\$|\$[^\$]+\$|\!\[\[[^\]]+\]\]|\[\[[^\]]+\]\]|\!\[[^\]]*\]\([^)]+\)|\[[^\]]*\]\([^)]+\)|\\[!"#$%&\'()*+,\-./:;<=>?@[\\\]^_`{|}~]'
        ctx.masked_source = re.sub(mask_pattern, mask_fn, ctx.body_content, flags=re.DOTALL)

        vault_path = ctx.engine.paths.get('vault', '.')
        sub = os.path.dirname(os.path.relpath(ctx.src_path, os.path.join(vault_path, ctx.route_source))).replace('\\', '/')
        if sub == '.': sub = ""
        ctx.mapped_sub_dir = ctx.engine.route_manager.get_mapped_sub_dir(sub, allow_ai=not ctx.is_silent_edit)
        
        ctx.engine.meta.register_document(ctx.rel_path, ctx.title, slug=ctx.slug, route_prefix=ctx.route_prefix, route_source=ctx.route_source)