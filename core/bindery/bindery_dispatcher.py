#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Egress Dispatcher
模块职责：物理出站分发器。
🛡️ [AEL-Iter-v5.3]：基于分层架构的 TDR 复健版本。
"""

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


    def dispatch(self, asset_index, title, slug, masked_body, fm_dict, rel_path, lang_code, route_prefix, route_source, mapped_sub_dir, masks, is_dry_run, is_target=False, node_assets=None, node_ext_assets=None, node_outlinks=None, assets_lock=None, force_persistence_date=None, seo_data=None, is_sandbox=False):
        if not self.paths.get('source_dir') and not self.paths.get('static_dir'):
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
        # 在进入语种/模式循环前，先对源文档引用的所有资产进行并行化加工投递。
        # 这样后续的所有 unmask 过程都将直接受益于已启动的异步任务。
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

            # 🧪 [V10.2] 主权盾牌注入
            from core.utils.tracing import Tracer
            current_tid = Tracer.get_id() or "AEL-SYSTEM-FALLBACK"
            if is_target and not is_dry_run:
                if current_tid not in final_body and "AEL-" not in final_body:
                    final_body += f"\n\n<!-- Sovereign-Tag: [[AEL-Iter-ID: {current_tid}]] -->"

            # 4. 元数据准备
            merged_fm = self._prepare_metadata(fm_dict, title, slug, rel_path, is_target, force_persistence_date, lang_code, route_prefix, route_source, mapped_sub_dir)

            # 5. 🧪 [V10.3] SSG 适配层渲染 (仅针对静态路执行渲染，源码路保持原汁原味)
            final_out_body = final_body
            final_out_fm = merged_fm
            if is_static:
                sub_path = os.path.join(route_prefix, mapped_sub_dir) if route_prefix or mapped_sub_dir else ""
                final_out_body, final_out_fm = self.ssg_adapter.render(final_body, merged_fm, seo_data=seo_data, target_lang=lang_code, sub_path=sub_path)
            
            # 6. 元数据序列化
            fm_str = self._serialize_frontmatter(final_out_fm)

            # 7. 物理落盘 (🚀 V11.2 多路写盘)
            shadow_hash, persistence_date = self._physical_write(
                rel_path, lang_code, route_prefix, mapped_sub_dir, slug,
                fm_str, final_out_body, is_dry_run,
                is_sandbox=is_sandbox, source_type=route_source, mode=mode
            )
            persistence_results[mode] = (shadow_hash, persistence_date)

        # 8. [V35.2] 分发提级：移除了此处的单文件分发逻辑。
        # 全渠道分发现已提级至同步管线末端的 [LifecycleManager] 阶段，以实现全局事务化与高并发优化。
        
        return persistence_results.get("source", (None, None))


    def _prepare_metadata(self, fm_dict, title, slug, rel_path, is_target, force_date, current_lang, route_prefix, route_source, mapped_sub_dir):
        merged_fm = fm_dict.copy()
        
        # 🚀 [V25.8] 标题主权对齐：优先尊重 Frontmatter 中已有的润色标题
        if 'title' not in merged_fm or not merged_fm['title']:
            if slug:
                merged_fm['title'] = slug.replace('-', ' ').title() if is_target else title
            else:
                merged_fm['title'] = title

        # 🚀 [V7.7] Hreflang SEO 矩阵注入
        # 让搜索引擎知道该页面的其他语种版本，极大提升全球权重
        hreflangs = []
        source_code = self.i18n.source.lang_code
        all_langs = [source_code] + [t.lang_code for t in self.i18n.targets if t.lang_code]

        for code in all_langs:
            # 推导逻辑 URL
            logical_url = self.route_manager.resolve_logical_url(code, route_prefix, mapped_sub_dir, slug)
            hreflangs.append({"lang": code, "url": logical_url})

        merged_fm['hreflangs'] = hreflangs
        merged_fm['language'] = current_lang

        # 🚀 [V15.7] 物理主权对齐：透传路由前缀与源，确保 SSG 适配器能正确感知布局形态
        merged_fm['route_prefix'] = route_prefix
        merged_fm['route_source'] = route_source
        merged_fm['mapped_sub_dir'] = mapped_sub_dir
        merged_fm['slug'] = slug

        src_abs = os.path.join(self.paths.get('vault', '.'), rel_path)
        mtime_dt = datetime.fromtimestamp(os.path.getmtime(src_abs)).astimezone()

        post_date = None
        if force_date:
            try: post_date = datetime.fromisoformat(force_date)
            except Exception: pass

        if not post_date:
            doc_info = self.meta.get_doc_info(rel_path)
            hp_date = doc_info.get('persistent_date') if doc_info else None
            try: post_date = datetime.fromisoformat(hp_date) if hp_date else mtime_dt
            except Exception: post_date = mtime_dt

        merged_fm['date'] = post_date

        # 🚀 [V11.0] 最终渲染前的主权审计：确保所有关键路径参数非空
        if not merged_fm.get('title'): merged_fm['title'] = title or "Untitled"
        if not merged_fm.get('language'): merged_fm['language'] = current_lang or "zh"

        return self.ssg_adapter.adapt_metadata(merged_fm, mtime_dt, merged_fm.get('author', 'Illacme Engine'))

    def _serialize_frontmatter(self, fm):
        ordered = {k: fm.pop(k) for k in self.fm_order if k in fm}
        ordered.update(fm)
        return "---\n" + yaml.dump(ordered, Dumper=NoAliasDumper, allow_unicode=True, default_flow_style=False, sort_keys=False, width=float("inf")) + "---\n\n"

    def _physical_write(self, rel_path, lang, prefix, sub, slug, fm_str, body, is_dry_run, is_sandbox=False, source_type="docs", mode="source"):
        ext = os.path.splitext(rel_path)[1].lower()

        # 🚀 [V11.2] 双相出口扩展名适配
        # 🚀 [V12.0] 后缀主权对齐：如果适配器返回 None，则保留原始后缀 (如 .mdx, .markdown)
        target_ext = self.ssg_adapter.output_extensions.get(mode)
        if target_ext is None:
            target_ext = ext

        # 🚀 [V11.2] 根据模式选择物理根目录
        if is_sandbox:
            target_root = self.paths.get('sandbox')
        else:
            target_root = self.paths.get('static_dir') if mode == 'static' else self.paths.get('source_dir')
        
        if not target_root:
            tlog.warning(f"⚠️ [分发拦截] 未定义模式 '{mode}' 的根目录，跳过落盘: {rel_path}")
            return None, None

        # 计算最终物理路径
        dest = self.route_manager.resolve_physical_path(target_root, lang, prefix, sub, slug, target_ext, source_type=source_type)
        tlog.info(f"💾 [物理落盘] ({mode}) -> {dest}")


        # 保持 cache 镜像以备后研 (统一使用 source 模式镜像)
        if mode == "source":
            cache_mirror = self.route_manager.resolve_physical_path(self.paths.get('cache'), lang, prefix, sub, slug, target_ext, source_type=source_type)
        else:
            cache_mirror = None

        # 🚀 [V15.6] 洁净度控制：由 SSG 适配器决定该输出格式是否支持元数据头
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
