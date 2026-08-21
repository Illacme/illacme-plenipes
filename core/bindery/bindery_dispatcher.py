#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Illacme-plenipes Core - Egress Dispatcher
🛡️ [AEL-Iter-v5.3]"""

import os
import re
import yaml
import logging
import hashlib
from datetime import datetime
from core.utils import sanitize_ai_response
from core.bindery.bindery_unmasker import BinderyUnmasker

from core.utils.tracing import tlog

class BinderyDispatcher:
    def __init__(self, paths, meta, route_manager, asset_pipeline, ssg_adapter, ast_resolver,
                 deployment_manager=None, pub_cfg=None, fm_order=None,
                 asset_base_url="", i18n_cfg=None, janitor=None, link_resolver=None):
        self.paths = paths
        self.meta = meta
        self.route_manager = route_manager
        self.asset_pipeline = asset_pipeline
        self.ssg_adapter = ssg_adapter
        self.ast_resolver = ast_resolver
        self.deployment_manager = deployment_manager

        self.pub_cfg = pub_cfg
        self.fm_order = fm_order
        self.asset_base_url = asset_base_url
        self.i18n = i18n_cfg
        self.janitor = janitor # 🛡️ [V10.3] 清理卫士挂载修复
        self.link_resolver = link_resolver

        # 🚀 [TDR-Iter-021] 挂载子模块
        self.unmasker = BinderyUnmasker(self, link_resolver=self.link_resolver)


    def dispatch(self, asset_index, title, slug, masked_body, fm_dict, rel_path, lang_code, route_prefix, route_source, mapped_sub_dir, masks, is_dry_run, is_target=False, node_assets=None, node_ext_assets=None, node_outlinks=None, assets_lock=None, force_persistence_date=None, seo_data=None, is_sandbox=False, target_slot="docs"):
        tlog.info(f"🚀 [Dispatcher Debug] Dispatching {rel_path} | Lang: {lang_code} | Target: {is_target}")
        if not self.paths.get('source_dir') and not self.paths.get('site_dir'):
             return None, None

        # 1. 🧬 [NoneType 免疫] 内容净化与解蔽
        masked_body = masked_body or ""
        sanitized_body = sanitize_ai_response(masked_body)
        fm_dict = fm_dict or {}
        seo_data = seo_data or {}

        # 🚀 [V11.2] 获取该主题的输出契约 (插件化驱动)
        output_schema = self.ssg_adapter.get_output_schema()
        
        persistence_results = {}
        current_tid = "AEL-SYSTEM-FALLBACK"
        
        # 2. 🚀 [V24.0] 资产全量预热 (Global Pre-Warming)
        self.unmasker.warm_assets(sanitized_body, masks, asset_index, slug=slug)

        # 3. 核心分发循环
        for mode in output_schema:
            # 🚀 [V11.2] 根据模式计算最终内容与路径
            # source 模式始终输出 Markdown；static 模式由渲染器决定
            is_static = (mode == "static")
            
            # 执行解蔽 (Unmask)
            # 注意：unmask 逻辑可能依赖于最终输出格式，此处需确保兼容
            final_body = self.unmasker.unmask(sanitized_body, lang_code, route_prefix, route_source, mapped_sub_dir, masks, is_dry_run, is_target, asset_index, node_assets, assets_lock, node_outlinks, slug=slug, rel_path=rel_path)

            # 3. MDX 处理与 Credit 注入
            if rel_path.lower().endswith('.mdx'):
                final_body = self._handle_mdx_specifics(final_body)

            # 🚀 [V7.9] 语种感知的组件动态注入
            injection = self.i18n.injection_matrix.get(lang_code)
            if injection:
                for placeholder, replacement in injection.replace_placeholders.items():
                    final_body = final_body.replace(placeholder, replacement)
                if injection.prepend_body: final_body = f"{injection.prepend_body}\n\n{final_body}"
                if injection.append_body: final_body = f"{final_body}\n\n{injection.append_body}"
                if rel_path.lower().endswith('.mdx') and injection.imports:
                    final_body = "\n".join(injection.imports) + "\n\n" + final_body

            if self.pub_cfg.append_credit:
                final_body += f"{self.pub_cfg.credit_text}\n"

            from core.utils.tracing import Tracer
            current_tid = Tracer.get_id() or "AEL-SYSTEM-FALLBACK"
            if is_target and not is_dry_run:
                if current_tid not in final_body and "AEL-" not in final_body:
                    final_body += f"\n\n<!-- Sovereign-Tag: [[AEL-Iter-ID: {current_tid}]] -->"

            # 4. 元数据准备
            merged_fm = self._prepare_metadata(fm_dict, title, slug, rel_path, is_target, force_persistence_date, lang_code, route_prefix, route_source, mapped_sub_dir)

            final_out_body = final_body
            final_out_fm = merged_fm
            if is_static:
                actual_seo = seo_data
                if is_target and seo_data and "i18n_seo" in seo_data and isinstance(seo_data["i18n_seo"], dict):
                    lang_seo = seo_data["i18n_seo"].get(lang_code)
                    if lang_seo and isinstance(lang_seo, dict):
                        actual_seo = {**seo_data, **lang_seo}
                eff_sub = mapped_sub_dir
                if mapped_sub_dir and route_prefix:
                    sub_clean = mapped_sub_dir.strip("/\\")
                    prefix_parts = [p for p in route_prefix.replace('\\', '/').split('/') if p]
                    if sub_clean in prefix_parts:
                        eff_sub = ""

                # 🚀 [V100.9] 静态层级精准对齐：直接基于 resolve_physical_path 预判实际静态落盘相对路径
                static_site_root = self.paths.get('site_dir') or 'dist'
                predicted_dest = self.route_manager.resolve_physical_path(
                    static_site_root, lang_code, route_prefix, eff_sub, slug, '.html', source_type=target_slot
                )
                sub_path = os.path.relpath(predicted_dest, static_site_root).replace('\\', '/')

                # 🔒 [I5] 人工校对锁检测（Q4=A：SSG 渲染前拦截，确保跨主题兼容）
                _use_locked = False
                _locked_body = final_body
                _locked_fm = merged_fm
                _lang_meta = {}
                if is_target and self.meta:
                    _doc_meta = self.meta.get_doc_info(rel_path)
                    if isinstance(_doc_meta, dict) and type(_doc_meta).__name__ not in ('MagicMock', 'Mock'):
                        _translations = _doc_meta.get("translations")
                        if isinstance(_translations, dict) and type(_translations).__name__ not in ('MagicMock', 'Mock'):
                            _lang_meta = _translations.get(lang_code, {})
                            if isinstance(_lang_meta, dict) and type(_lang_meta).__name__ not in ('MagicMock', 'Mock'):
                                if _lang_meta.get("human_approved"):
                                    # Q3=B：hash 变更后打 stale 标记，但不自动解锁
                                    _approved_hash = _lang_meta.get("approved_source_hash", "")
                                    if _approved_hash:
                                        _cur_hash = hashlib.md5(sanitized_body.encode("utf-8")).hexdigest()
                                        if _cur_hash != _approved_hash and not _lang_meta.get("review_is_stale"):
                                            self.meta.mark_review_stale(rel_path, lang_code)
                                            tlog.warning(
                                                f"⚠️ [I5校对锁] {rel_path}/{lang_code} 原稿已变更，"
                                                f"校对内容可能失效（锁定保留，请在 Dashboard 复核）"
                                            )
                                    _use_locked = True
                                    _locked_body = _lang_meta.get("reviewed_body") or final_body
                                    _locked_fm = merged_fm.copy()
                                    if _lang_meta.get("reviewed_title"):
                                        _locked_fm["title"] = _lang_meta["reviewed_title"]
                                    tlog.info(f"🔒 [I5校对锁] {rel_path}/{lang_code} 跳过 AI 内容，使用人工锁定版本")

                if _use_locked:
                    final_out_body, final_out_fm = self.ssg_adapter.render(
                        _locked_body, _locked_fm, seo_data=actual_seo,
                        target_lang=lang_code, sub_path=sub_path
                    )
                    # 注入校对版 SEO 描述（若有）
                    _locked_desc = _lang_meta.get("reviewed_desc")
                    if _locked_desc and isinstance(final_out_fm, dict):
                        final_out_fm["description"] = _locked_desc
                else:
                    final_out_body, final_out_fm = self.ssg_adapter.render(
                        final_body, merged_fm, seo_data=actual_seo,
                        target_lang=lang_code, sub_path=sub_path
                    )
            
            # 6. 元数据序列化
            fm_str = self._serialize_frontmatter(final_out_fm)

            # 7. 物理落盘 (🚀 V11.2 多路写盘)
            shadow_hash, persistence_date = self._physical_write(
                rel_path, lang_code, route_prefix, mapped_sub_dir, slug,
                fm_str, final_out_body, is_dry_run,
                is_sandbox=is_sandbox, source_type=target_slot, mode=mode
            )
            persistence_results[mode] = (shadow_hash, persistence_date)

        # 8. [V35.2] 分发已提级至同步管线末端的 [LifecycleManager] 阶段
        
        return persistence_results.get("source", (None, None))


    def _prepare_metadata(self, fm_dict, title, slug, rel_path, is_target, force_date, current_lang, route_prefix, route_source, mapped_sub_dir):
        merged_fm = fm_dict.copy()
        

        if 'title' not in merged_fm or not merged_fm['title']:
            if slug:
                merged_fm['title'] = slug.replace('-', ' ').title() if is_target else title
            else:
                merged_fm['title'] = title

        # 🚀 [V7.7] Hreflang SEO 矩阵注入
        hreflangs = []
        source_code = self.i18n.source.lang_code if (self.i18n and self.i18n.source) else "zh"
        # 🚀 [V7.7.1] 将 "auto" 解析为系统的默认母语言，杜绝覆盖为当前译文语言导致源语种丢失
        if not source_code or source_code == "auto":
            source_code = getattr(self.route_manager, 'default_lang', 'zh') or 'zh'
            if source_code == 'auto':
                source_code = 'zh'
        
        target_codes = [t.lang_code for t in self.i18n.targets if t.lang_code] if (self.i18n and self.i18n.targets) else []
        all_langs = [source_code] + [tc for tc in target_codes if tc != source_code]

        for code in all_langs:
            # 推导逻辑 URL
            logical_url = self.route_manager.resolve_logical_url(code, route_prefix, mapped_sub_dir, slug)
            hreflangs.append({"lang": code, "url": logical_url})

        merged_fm['hreflangs'] = hreflangs
        merged_fm['language'] = current_lang


        merged_fm['route_prefix'] = route_prefix
        merged_fm['route_source'] = route_source
        merged_fm['mapped_sub_dir'] = mapped_sub_dir
        merged_fm['slug'] = slug

        src_abs = os.path.join(self.paths.get('vault', '.'), rel_path)
        try:
            mtime_dt = datetime.fromtimestamp(os.path.getmtime(src_abs)).astimezone()
        except OSError:
            mtime_dt = datetime.now().astimezone()

        post_date = None
        if force_date:
            try: post_date = datetime.fromisoformat(force_date)
            except Exception: pass

        if not post_date:
            doc_info = self.meta.get_doc_info(rel_path) if self.meta else None
            hp_date = None
            if doc_info and isinstance(doc_info, dict) and type(doc_info).__name__ not in ('MagicMock', 'Mock'):
                hp_date = doc_info.get('persistent_date')
            
            if isinstance(hp_date, str):
                try: post_date = datetime.fromisoformat(hp_date)
                except Exception: post_date = mtime_dt
            else:
                post_date = mtime_dt

        merged_fm['date'] = post_date


        if not merged_fm.get('title'): merged_fm['title'] = title or "Untitled"
        if not merged_fm.get('language'): merged_fm['language'] = current_lang or "zh"

        return self.ssg_adapter.adapt_metadata(merged_fm, mtime_dt, merged_fm.get('author', 'Illacme Engine'))

    def _serialize_frontmatter(self, fm):
        ordered = {k: fm.pop(k) for k in self.fm_order if k in fm}
        ordered.update(fm)
        return "---\n" + yaml.dump(ordered, Dumper=NoAliasDumper, allow_unicode=True, default_flow_style=False, sort_keys=False, width=float("inf")) + "---\n\n"

    def _physical_write(self, rel_path, lang, prefix, sub, slug, fm_str, body, is_dry_run, is_sandbox=False, source_type="docs", mode="source"):
        ext = os.path.splitext(rel_path)[1].lower()

        # 🚀 [V11.2 & V12.0] 后缀与双相适配
        target_ext = self.ssg_adapter.output_extensions.get(mode)
        if target_ext is None:
            target_ext = ext

        if is_sandbox:
            target_root = self.paths.get('sandbox')
        else:
            target_root = self.paths.get('site_dir') if mode == 'static' else self.paths.get('source_dir')
        
        if not target_root:
            tlog.warning(f"⚠️ [分发拦截] 未定义模式 '{mode}' 的根目录，跳过落盘: {rel_path}")
            return None, None

        dest = self.route_manager.resolve_physical_path(target_root, lang, prefix, sub, slug, target_ext, source_type=source_type)
        tlog.info(f"💾 [物理落盘] ({mode}) -> {dest}")

        if mode == "source":
            cache_mirror = self.route_manager.resolve_physical_path(self.paths.get('cache'), lang, prefix, sub, slug, target_ext, source_type=source_type)
            # 计算主题专属的源文件缓存路径镜像
            theme_name = getattr(self.ssg_adapter.engine, 'active_theme', 'default') or 'default'
            theme_cache_dir = self.ssg_adapter.engine.config.get_theme_source_cache_dir(theme_name)
            theme_source_mirror = self.route_manager.resolve_physical_path(theme_cache_dir, lang, prefix, sub, slug, target_ext, source_type=source_type)
        else:
            cache_mirror = None
            theme_source_mirror = None

        is_markup_content = self.ssg_adapter.supports_frontmatter(target_ext)
        if not is_markup_content and mode == 'static':
            full_content = body
        else:
            full_content = fm_str + body

        if not is_dry_run:
            tmp_dest = dest + ".tmp"
            try:
                # 写入缓存镜像 (原子化)
                if cache_mirror:
                    tmp_cache = cache_mirror + ".tmp"
                    os.makedirs(os.path.dirname(cache_mirror), exist_ok=True)
                    with open(tmp_cache, 'w', encoding='utf-8') as f: f.write(full_content)
                    os.replace(tmp_cache, cache_mirror)

                # 写入主题专属源文件缓存 (原子化)
                if theme_source_mirror:
                    tmp_theme_cache = theme_source_mirror + ".tmp"
                    os.makedirs(os.path.dirname(theme_source_mirror), exist_ok=True)
                    with open(tmp_theme_cache, 'w', encoding='utf-8') as f: f.write(full_content)
                    os.replace(tmp_theme_cache, theme_source_mirror)

                # 写入目标路径 (原子化)
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                with open(tmp_dest, 'w', encoding='utf-8') as f: f.write(full_content)
                
                # 🚀 [V13.0] 系统级原子替换，确保 0 中断风险
                os.replace(tmp_dest, dest)
                
                if not is_sandbox and self.janitor:
                    self.janitor.mark_as_fresh(dest)
            except Exception as e:
                tlog.error(f"🛑 [原子落盘失败] ({mode}): {e}")
                if os.path.exists(tmp_dest): os.remove(tmp_dest)
        
        return hashlib.md5(full_content.encode('utf-8')).hexdigest(), None

    def _handle_mdx_specifics(self, body):
        import_pattern = re.compile(r'^(import\s+.*?from\s+[\'"].*?[\'"];?)$', re.MULTILINE)
        imports = import_pattern.findall(body)
        if imports:
            body = import_pattern.sub('', body)
            body = '\n'.join(list(dict.fromkeys(imports))) + '\n\n' + body.lstrip()
        return body

class NoAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data): return True
