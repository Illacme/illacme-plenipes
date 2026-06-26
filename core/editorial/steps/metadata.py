# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Pipeline Steps Shard
工序职责：MetadataAndHashStep (元数据注入与指纹核验)
🛡️ [AEL-Iter-v5.3]：基于分层架构的 TDR 复健版本。
"""

import os
import hashlib
import shutil
from core.utils import normalize_keywords
from core.utils.tracing import tlog
from core.editorial.runner import PipelineStep

class MetadataAndHashStep(PipelineStep):
    """阶段 8-9: 元数据注入与指纹核验"""
    PLUGIN_ID = "metadata_hash"
    DISPLAY_NAME = "元数据注入与指纹核验"
    VERSION = "V5.3"
    DESCRIPTION = "执行物理指纹计算，确保增量同步的一致性与元数据对正。"

    def process(self, ctx):
        defaults = ctx.engine.fm_defaults or {}
        ctx.base_fm = {k: v for k, v in defaults.items() if v is not None and str(v).strip() != ""}
        ctx.base_fm.update(ctx.fm_dict)

        for f in ['keywords', 'tags', 'categories']:
            if f in ctx.base_fm: ctx.base_fm[f] = normalize_keywords(ctx.base_fm.get(f))

        if 'slug' in ctx.base_fm: ctx.base_fm.pop('slug', None)
        ctx.current_hash = hashlib.md5((str(ctx.base_fm) + ctx.body_content).encode('utf-8')).hexdigest()

        old_info = ctx.engine.meta.get_doc_info(ctx.rel_path)
        ctx.engine.meta.register_document(
            ctx.rel_path, ctx.title,
            source_hash=ctx.current_hash,
            source_lang=getattr(ctx, 'source_lang', None)
        )
        ctx.doc_info = ctx.engine.meta.get_doc_info(ctx.rel_path)

        if not old_info.get("slug"):
            hit = ctx.engine.meta.find_by_hash(ctx.current_hash)
            if hit and hit.get("slug"):
                ctx.engine.meta.register_document(ctx.rel_path, ctx.title, slug=hit.get("slug"), seo_data=hit.get("seo_data") or hit.get("seo"), shadow_hash=hit.get("shadow_hash"))
                self._handle_shadow_roaming(ctx, hit)
                ctx.doc_info = ctx.engine.meta.get_doc_info(ctx.rel_path)

        if not ctx.force_sync and old_info.get("source_hash") == ctx.current_hash:
            # 🚀 [V105.0 物理缓存自愈] 如果指纹未变，但物理缓存镜像在主题专属源文件缓存目录下丢失，则绝不跳过
            all_cached = True
            ext = os.path.splitext(ctx.rel_path)[1].lower()
            langs = []
            from core.config.models.governance import PublishingMode
            if ctx.engine.config.i18n_settings.enabled and ctx.engine.config.governance.publishing_mode == PublishingMode.GLOBAL:
                langs = [t.lang_code for t in ctx.engine.config.i18n_settings.targets if t.lang_code]
                src_lang = ctx.engine.config.i18n_settings.source.lang_code
                if src_lang and src_lang not in langs:
                    langs.append(src_lang)
            
            theme_name = getattr(ctx.engine, 'active_theme', 'default') or 'default'
            cache_dir = ctx.engine.config.get_theme_source_cache_dir(theme_name)
            slug = ctx.doc_info.get("slug") or old_info.get("slug") or os.path.splitext(os.path.basename(ctx.rel_path))[0]
            
            if cache_dir and slug:
                vault_root = ctx.engine.paths.get('vault', '.')
                sub = os.path.dirname(os.path.relpath(ctx.src_path, os.path.join(vault_root, ctx.route_source))).replace('\\', '/')
                if sub == '.': sub = ""
                mapped_sub = ctx.engine.route_manager.get_mapped_sub_dir(sub, allow_ai=False)
                
                for lang in langs:
                    try:
                        cache_mirror = ctx.engine.route_manager.resolve_physical_path(
                            cache_dir, lang, ctx.route_prefix, mapped_sub, slug, ext, source_type=ctx.target_slot
                        )
                        if not os.path.exists(cache_mirror):
                            all_cached = False
                            break
                    except Exception:
                        all_cached = False
                        break
            else:
                all_cached = False
                
            if all_cached:
                ctx.is_skipped = True
                ctx.is_aborted = True

    def _handle_shadow_roaming(self, ctx, hit):
        try:
            ext = os.path.splitext(ctx.rel_path)[1].lower()
            vault_path = ctx.engine.paths.get('vault', '.')
            shadow_path = ctx.engine.paths.get('shadow')
            if not shadow_path: return

            from core.config.models.governance import PublishingMode
            if ctx.engine.config.governance.publishing_mode == PublishingMode.GLOBAL:
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
