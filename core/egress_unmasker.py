#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Engine Assembly Factory
模块职责：负责主引擎的所有核心组件装配、服务挂载与依赖注入。
🛡️ [AEL-Iter-v5.3]：彻底消灭上帝函数的架构分层枢纽。
"""
import re
import urllib.parse
import hashlib
import logging
import os

logger = logging.getLogger("Illacme.plenipes")

class EgressUnmasker:
    """🚀 [TDR-Iter-021] 解蔽引擎：专注处理方言解蔽、资产寻址与链接映射"""
    
    def __init__(self, service):
        self.service = service
        self.paths = service.paths
        self.meta = service.meta
        self.route_manager = service.route_manager
        self.asset_pipeline = service.asset_pipeline
        self.asset_base_url = service.asset_base_url

    def unmask(self, body, lang_code, route_prefix, route_source, mapped_sub_dir, masks, is_dry_run, is_target, asset_index, node_assets, assets_lock, node_outlinks):
        def _get_closest_asset(target_filename):
            candidates = asset_index.get(target_filename, [])
            if not candidates: return None
            if len(candidates) == 1: return candidates[0]
            current_abs_dir = os.path.dirname(os.path.join(self.paths.get('vault', '.'), ""))
            return sorted(candidates, key=lambda p: len(os.path.commonprefix([current_abs_dir, os.path.dirname(p)])), reverse=True)[0]

        def unmask_fn(m):
            idx = int(re.search(r'\d+', m.group(0)).group())
            orig = masks[idx]
            if orig.startswith('\\'): return orig 
            
            # Helper for logging
            def log_asset(p_name):
                if node_assets is not None and assets_lock is not None:
                    with assets_lock: node_assets.add(p_name)
                return p_name

            def log_outlink(tgt_path):
                if tgt_path and node_outlinks is not None and assets_lock is not None:
                    with assets_lock: node_outlinks.add(tgt_path)

            # URL-only unmasking
            if orig.startswith('URL_ONLY_LNK:') or orig.startswith('URL_ONLY_IMG:'):
                clean_path = urllib.parse.unquote(orig.split(':', 1)[1].strip())
                if clean_path.startswith(('http://', 'https://', 'mailto:', '#')): return clean_path
                
                asset_filename = os.path.basename(clean_path.split('?')[0].split('#')[0])
                target_asset_path = _get_closest_asset(asset_filename)
                if target_asset_path:
                    alt_text = ""
                    try:
                        with open(target_asset_path, 'rb') as f:
                            h = hashlib.md5(f.read()).hexdigest()
                        meta = self.meta.get_asset_metadata(h)
                        if meta: alt_text = meta.get("alt_texts", {}).get(lang_code) or meta.get("alt_text", "")
                    except Exception: pass
                    processed_name = log_asset(self.asset_pipeline.process(target_asset_path, asset_filename, is_dry_run))
                    return f"{self.asset_base_url}{processed_name}" if not orig.startswith('URL_ONLY_IMG:') else f"![{alt_text}]({self.asset_base_url}{processed_name})"
                
                target_rel_path = self.meta.resolve_link(clean_path)
                if target_rel_path:
                    log_outlink(target_rel_path)
                    t_doc_info = self.meta.get_doc_info(target_rel_path)
                    t_slug = t_doc_info.get("slug") or re.sub(r'[^\w\-]', '', target_rel_path.replace(' ', '-').lower())
                    t_abs = os.path.join(self.paths.get('vault', '.'), target_rel_path)
                    t_sub = os.path.dirname(os.path.relpath(t_abs, os.path.join(self.paths.get('vault', '.'), t_doc_info.get("source", route_source)))).replace('\\', '/')
                    t_mapped = self.route_manager.get_mapped_sub_dir(t_sub, allow_ai=False)
                    return self.route_manager.resolve_logical_url(lang_code, t_doc_info.get("prefix", route_prefix), t_mapped, t_slug)
                return clean_path

            # Image unmasking
            if orig.startswith('![') and '(' in orig:
                match = re.match(r'^\!\[(.*?)\]\((.*?)\)$', orig)
                if match:
                    orig_alt, img_url = match.groups()
                    clean_path = urllib.parse.unquote(img_url.strip())
                    asset_filename = os.path.basename(clean_path.split('?')[0].split('#')[0])
                    target_asset_path = _get_closest_asset(asset_filename)
                    if target_asset_path:
                        final_alt = orig_alt
                        try:
                            with open(target_asset_path, 'rb') as f:
                                h = hashlib.md5(f.read()).hexdigest()
                            meta = self.meta.get_asset_metadata(h)
                            if meta:
                                alt_map = meta.get("alt_texts", {})
                                final_alt = alt_map.get(lang_code) or meta.get("alt_text") or orig_alt
                        except Exception: pass
                        processed_name = log_asset(self.asset_pipeline.process(target_asset_path, asset_filename, is_dry_run))
                        return f"![{final_alt}]({self.asset_base_url}{processed_name})"
                return orig

            return orig

        final_body = body
        max_depth = 10
        current_depth = 0
        while re.search(r'\[\[STB_MASK_\d+\]\]', final_body) and current_depth < max_depth:
            final_body = re.sub(r'\[\[STB_MASK_\d+\]\]', unmask_fn, final_body)
            current_depth += 1
        return final_body
