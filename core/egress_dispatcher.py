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
import tempfile
import logging
import hashlib
from datetime import datetime
from .utils import sanitize_ai_response
from .egress_unmasker import EgressUnmasker

logger = logging.getLogger("Illacme.plenipes")

class EgressDispatcher:
    def __init__(self, paths, meta, route_manager, asset_pipeline, ssg_adapter, mdx_resolver, syndicator, broadcaster, pub_cfg, fm_order, asset_base_url, i18n_cfg, janitor=None):
        self.paths = paths
        self.meta = meta
        self.route_manager = route_manager
        self.asset_pipeline = asset_pipeline
        self.ssg_adapter = ssg_adapter
        self.mdx_resolver = mdx_resolver
        self.syndicator = syndicator
        self.broadcaster = broadcaster
        self.pub_cfg = pub_cfg
        self.fm_order = fm_order
        self.asset_base_url = asset_base_url
        self.i18n = i18n_cfg
        self.janitor = janitor
        self.ael_iter_id = "AEL-2026.04.23.TDR"
        
        # 🚀 [TDR-Iter-021] 挂载子模块
        self.unmasker = EgressUnmasker(self)

    def dispatch(self, asset_index, title, slug, masked_body, fm_dict, rel_path, lang_code, route_prefix, route_source, mapped_sub_dir, masks, is_dry_run, is_target=False, node_assets=None, node_ext_assets=None, node_outlinks=None, assets_lock=None, force_persistence_date=None):
        if not self.paths.get('target_base'): return ""
        
        # 1. 净化与解蔽
        sanitized_body = sanitize_ai_response(masked_body)
        final_body = self.unmasker.unmask(sanitized_body, lang_code, route_prefix, route_source, mapped_sub_dir, masks, is_dry_run, is_target, asset_index, node_assets, assets_lock, node_outlinks)

        # 2. MDX 处理与 Credit 注入
        if rel_path.lower().endswith('.mdx'):
            final_body = self._handle_mdx_specifics(final_body)
        if self.pub_cfg.append_credit:
            final_body += f"{self.pub_cfg.credit_text}\n"
        
        # 3. 元数据合并与排序
        merged_fm = self._prepare_metadata(fm_dict, title, slug, rel_path, is_target, force_persistence_date)
        fm_str = self._serialize_frontmatter(merged_fm)

        # 4. 物理落盘与分发
        shadow_hash, persistence_date = self._physical_write(rel_path, lang_code, route_prefix, mapped_sub_dir, slug, fm_str, final_body, is_dry_run)
        
        if not is_dry_run and lang_code == self.i18n.source.lang_code:
            self.syndicator.syndicate(merged_fm, final_body, f"/{lang_code}/{mapped_sub_dir}/{slug}".replace('//', '/'), ael_iter_id=self.ael_iter_id)
            self.broadcaster.broadcast(title, rel_path, lang_code, mapped_sub_dir, slug, ael_iter_id=self.ael_iter_id)
            
        return shadow_hash, persistence_date

    def _prepare_metadata(self, fm_dict, title, slug, rel_path, is_target, force_date):
        merged_fm = fm_dict.copy()
        if slug:
            merged_fm['title'] = slug.replace('-', ' ').title() if is_target else title
        else:
            merged_fm['title'] = title
        
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
        return self.ssg_adapter.adapt_metadata(merged_fm, mtime_dt, merged_fm.get('author', 'Illacme Engine'))

    def _serialize_frontmatter(self, fm):
        ordered = {k: fm.pop(k) for k in self.fm_order if k in fm}
        ordered.update(fm)
        return "---\n" + yaml.dump(ordered, Dumper=NoAliasDumper, allow_unicode=True, default_flow_style=False, sort_keys=False, width=float("inf")) + "---\n\n"

    def _physical_write(self, rel_path, lang, prefix, sub, slug, fm_str, body, is_dry_run):
        ext = os.path.splitext(rel_path)[1].lower()
        dest = self.route_manager.resolve_physical_path(self.paths.get('target_base'), lang, prefix, sub, slug, ext)
        shadow = self.route_manager.resolve_physical_path(self.paths.get('shadow'), lang, prefix, sub, slug, ext)
        
        full_content = fm_str + body
        if not is_dry_run:
            try:
                os.makedirs(os.path.dirname(shadow), exist_ok=True)
                with open(shadow, 'w', encoding='utf-8') as f: f.write(full_content)
                
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                with open(dest, 'w', encoding='utf-8') as f: f.write(full_content)
                if self.janitor: self.janitor.mark_as_fresh(dest)
            except Exception as e: logger.error(f"🛑 写入失败: {e}")
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