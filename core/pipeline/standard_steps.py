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
from core.pipeline.runner import PipelineStep

from core.utils.tracing import tlog

class ReadAndNormalizeStep(PipelineStep):
    """阶段 3-4: 物理读取与编辑器方言抹平"""
    PLUGIN_ID = "read_normalize"
    def process(self, ctx):
        try:
            with open(ctx.src_path, 'r', encoding='utf-8') as f:
                ctx.raw_content = f.read()
        except Exception as e:
            tlog.error(f"🛑 读取失败 {ctx.src_path}: {e}")
            ctx.is_aborted = True
            return

        fm_dict, raw_body = extract_frontmatter(ctx.raw_content)
        ctx.raw_body, ctx.fm_dict = ctx.engine.input_adapter.normalize(raw_body, fm_dict)

        # 🚀 [V15.9] 标题主权对齐：Frontmatter 显式定义优先于物理文件名
        if ctx.fm_dict.get('title'):
            ctx.title = ctx.fm_dict.get('title')

        raw_ai_sync = ctx.fm_dict.get('ai_sync')
        ctx.is_silent_edit = (str(raw_ai_sync).lower() == 'false') if raw_ai_sync is not None else False

        # 🚀 [V7.7] 逐文件语种识别 (Per-Document Granular Detection)
        from core.utils.language_hub import LanguageHub
        # 优先遵循配置，若配置为 auto 则触发动态探测
        config_src = ctx.engine.i18n.source.lang_code
        if config_src == "auto" or not config_src:
            ctx.source_lang = LanguageHub.detect_source_lang(ctx.raw_content, ctx.services.translator)
        else:
            ctx.source_lang = config_src

class ASTAndPurifyStep(PipelineStep):
    """阶段 6-7: AST 降维与语义提纯"""
    PLUGIN_ID = "purify"
    def process(self, ctx):
        # 🚀 [V16.0] 切换至全插件化 AST 解析流水线
        ctx.body_content = ctx.engine.ast_resolver.resolve(
            ctx.raw_body,
            ctx.src_path,
            ctx.engine.paths.get('target_base')
        )
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
                ctx.engine.meta.register_document(ctx.rel_path, ctx.title, slug=hit.get("slug"), seo_data=hit.get("seo_data") or hit.get("seo"), shadow_hash=hit.get("shadow_hash"))
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
        # 🛡️ [V24.6] 首页主权防护：强制锁定 Index.md 的 Slug 为 'index'
        is_homepage = ctx.rel_path.lower().endswith('index.md') or ctx.rel_path.lower().endswith('index.mdx')
        if is_homepage:
            slug_raw = "index"
            tlog.info(f"🏠 [首页防护] 强制将 {ctx.rel_path} 的 Slug 锁定为 'index'")

        # 🚀 [V26.5] 显性重构支持：如果开启了 --re-slug，强制重置非首页的 Slug
        if getattr(ctx.engine, 'args', None) and getattr(ctx.engine.args, 're_slug', False) and not is_homepage:
            tlog.info(f"🔄 [Slug 重塑] 检测到 --re-slug 标志，正在强制重新生成 {ctx.rel_path} 的 URL...")
            slug_raw = None

            is_json_leak = any(k in slug_raw.lower() for k in ["description", "keywords", "{", "\""])
            if is_json_leak or len(slug_raw) > 50 or '%' in slug_raw or bool(re.search(r'[\u4e00-\u9fa5]', slug_raw)):
                tlog.warning(f"⚠️ [Slug 拦截] 侦测到非法 Slug: {slug_raw[:30]}... 已强制重置")
                slug_raw = None

        if not slug_raw:
            slug_mode = ctx.engine.config.translation.slug_mode
            if slug_mode == 'ai' and not ctx.is_silent_edit:
                if ctx.is_dry_run:
                    # 🚀 [V11.8] 修复时间戳碰撞：使用标题指纹
                    slug_raw, slug_success = f"dry-run-{re.sub(r'[^a-z0-9]', '-', ctx.title.lower())[:30]}", True
                else:
                    try:
                        slug_raw, slug_success = ctx.engine.translator.generate_slug(ctx.title, is_dry_run=False)
                        # 🚀 [V24.6] 强制物理合规：AI 返回的 Slug 必须再次经过清洗
                        from core.logic.ai.ai_logic_hub import AILogicHub
                        slug_raw = AILogicHub.clean_slug(slug_raw)
                    except Exception: slug_success, slug_raw = False, None
                if not slug_success: ctx.ai_health_flag[0] = False
            else:
                english_only = re.sub(r'[^a-z0-9\-]', '', ctx.title.lower().replace(' ', '-'))
                slug_raw = re.sub(r'-+', '-', english_only).strip('-') or f"doc-{hashlib.md5(ctx.title.encode('utf-8')).hexdigest()[:6]}"

        ctx.slug = slug_raw.lower() if slug_raw else "index" if is_homepage else None
        if not ctx.seo_data:
            ctx.seo_data = ctx.doc_info.get("seo_data") or ctx.doc_info.get("seo") or {}

        # 🛡️ [V15.5] 逻辑纠偏：如果已经是批处理产物，则不再强制清空（保持其补全属性）
        # [V16.7] 工业化修正：彻底禁用强制清空逻辑，确保增量同步时能正确复用账本中的 SEO 数据。
        # is_batch_hit = hasattr(ctx, '_is_batch_hit') and ctx._is_batch_hit
        # if not ctx.is_silent_edit and not is_batch_hit and ctx.seo_data and ('description' in ctx.seo_data or 'keywords' in ctx.seo_data):
        #     ctx.seo_data = {}

class MaskingAndRoutingStep(PipelineStep):
    """阶段 13-14: 物理遮蔽与动态路由推导"""
    PLUGIN_ID = "masking_routing"
    def process(self, ctx):
        def mask_fn(m):
            matched = m.group(0)

            # [AEL-Iter-v7.5] 语义链接提取钩子 (Graph Link Extraction)
            if matched.startswith('[[') and not matched.startswith('![['):
                # 提取 Wikilink 目标
                target = matched[2:-2].split('|')[0].strip()
                if target: ctx.node_outlinks.add(target)
            elif matched.startswith('[') and '(' in matched and not matched.startswith('!['):
                # 提取标准 MD 链接目标
                link_match = re.match(r'^\[.*?\]\(([^)]+)\)$', matched)
                if link_match:
                    url = link_match.group(1).split('#')[0].split('?')[0].strip()
                    if url and not url.startswith(('http', 'mailto', 'tel')):
                        ctx.node_outlinks.add(url)

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

        mask_pattern = ctx.engine.config.system.mask_pattern
        ctx.masked_source = re.sub(mask_pattern, mask_fn, ctx.body_content, flags=re.DOTALL)

        vault_path = ctx.engine.paths.get('vault', '.')
        sub = os.path.dirname(os.path.relpath(ctx.src_path, os.path.join(vault_path, ctx.route_source))).replace('\\', '/')
        if sub == '.': sub = ""
        ctx.mapped_sub_dir = ctx.engine.route_manager.get_mapped_sub_dir(sub, allow_ai=not ctx.is_silent_edit)

        ctx.engine.meta.register_document(ctx.rel_path, ctx.title, slug=ctx.slug, route_prefix=ctx.route_prefix, route_source=ctx.route_source)

class VerificationStep(PipelineStep):
    """阶段 15: 全息主权验证 (Holographic Verification) 🛡️ [AEL-Iter-v11.0]"""
    PLUGIN_ID = "verification"
    def process(self, ctx):
        tlog.info(f"🛡️ [全息审计] 正在验证资产完整性: {ctx.rel_path}")

        # 1. 占位符对齐校验 (Mask Integrity)
        # 我们检查还原后的 body 中是否仍包含 STB_MASK 标记
        if "[[STB_MASK_" in ctx.body_content:
            err = "侦测到残留占位符！这通常意味着解蔽逻辑 (unmasking) 发生断裂。"
            tlog.error(f"❌ [审计失败] {err}")
            ctx.engine.brain.log_lesson("MASK_INTEGRITY", err, {"path": ctx.rel_path})
            ctx.is_aborted = True
            return

        # 2. 括号匹配度审计 (Sovereignty Shield)
        # 验证 [[SECRET_TAG]] 等关键结构的完整性（如果原文有，译文也必须有）
        if "[[SECRET_TAG]]" in ctx.raw_content and "[[SECRET_TAG]]" not in ctx.body_content:
            err = "敏感标签 [[SECRET_TAG]] 在流转中丢失！"
            tlog.warning(f"⚠️ [审计警告] {err}")
            ctx.engine.brain.log_lesson("SOVEREIGNTY_SHIELD", err, {"path": ctx.rel_path})
            # 这是一个强约束，在商业级模式下应视为失败
            ctx.is_aborted = True
            return

        # 3. 多语言矩阵对齐校验 (SEO Alignment)
        if hasattr(ctx, 'hreflangs') and len(ctx.hreflangs) < 1:
            tlog.warning("⚠️ [审计警告] 缺失多语言指向矩阵 (hreflangs)。")

        tlog.info("✨ [审计通过] 资产完整性 100% 严丝合缝。")
