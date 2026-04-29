#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Egress Unmasker (解蔽引擎)
🛡️ [V24.0] 并行预热版：支持资产预扫描与并行加工调度。
"""
import re
import urllib.parse
import hashlib
import logging
import os
from concurrent.futures import wait

from core.utils.tracing import tlog

class BinderyUnmasker:
    """🚀 [V24.0] 解蔽引擎：支持资产预热与并行解蔽"""

    def __init__(self, service, link_resolver=None):
        self.service = service
        self.paths = service.paths
        self.meta = service.meta
        self.route_manager = service.route_manager
        self.asset_pipeline = service.asset_pipeline
        self.asset_base_url = service.asset_base_url
        self.link_resolver = link_resolver

    def warm_assets(self, body, masks, asset_index, slug=None):
        """🚀 [V24.0] 资产预热：扫描文档引用的所有资产，并行投递至加工管线"""
        futures = []
        
        def _get_closest_asset(target_filename):
            candidates = asset_index.get(target_filename, [])
            if not candidates: return None
            if len(candidates) == 1: return candidates[0]
            current_abs_dir = os.path.dirname(os.path.join(self.paths.get('vault', '.'), ""))
            return sorted(candidates, key=lambda p: len(os.path.commonprefix([current_abs_dir, os.path.dirname(p)])), reverse=True)[0]

        # 扫描所有掩码
        for orig in masks:
            if not isinstance(orig, str): continue
            
            clean_path = None
            if orig.startswith(('URL_ONLY_LNK:', 'URL_ONLY_IMG:')):
                clean_path = urllib.parse.unquote(orig.split(':', 1)[1].strip())
            elif orig.startswith('![') and '(' in orig:
                match = re.match(r'^\!\[(.*?)\]\((.*?)\)$', orig)
                if match: clean_path = urllib.parse.unquote(match.group(2).strip())
            
            if clean_path and not clean_path.startswith(('http://', 'https://', 'mailto:', '#')):
                asset_filename = os.path.basename(clean_path.split('?')[0].split('#')[0])
                target_asset_path = _get_closest_asset(asset_filename)
                if target_asset_path:
                    # 投递异步加工任务
                    futures.append(self.asset_pipeline.process_async(target_asset_path, asset_filename, slug=slug))
        
        if futures:
            tlog.debug(f"🔥 [资产预热] 已为文档分发 {len(futures)} 个并行加工任务...")
            # 等待所有任务入池完成 (不需要等待执行完，因为后续 process 会 DCL 阻塞)
            # 但为了性能，我们这里可以稍微 wait 一下，或者干脆不 wait
            pass
        return futures

    def unmask(self, body, lang_code, route_prefix, route_source, mapped_sub_dir, masks, is_dry_run, is_target, asset_index, node_assets, assets_lock, node_outlinks, slug=None, rel_path=None):
        # 🚀 [V11.7] 动态深度感知
        route_path = os.path.join(route_prefix or "", mapped_sub_dir or "")
        depth = len([p for p in route_path.replace('\\', '/').split('/') if p]) + 1
        root_path = "../" * depth
        
        # 🚀 [V24.0] 自动触发预热
        self.warm_assets(body, masks, asset_index, slug=slug)

        def _get_closest_asset(target_filename):
            candidates = asset_index.get(target_filename, [])
            if not candidates: return None
            if len(candidates) == 1: return candidates[0]
            current_abs_dir = os.path.dirname(os.path.join(self.paths.get('vault', '.'), ""))
            return sorted(candidates, key=lambda p: len(os.path.commonprefix([current_abs_dir, os.path.dirname(p)])), reverse=True)[0]

        def unmask_fn(m):
            raw_tag = m.group(0)
            idx_match = re.search(r'\d+', raw_tag)
            if not idx_match: return raw_tag

            idx = int(idx_match.group())
            if idx >= len(masks):
                return f"[[INVALID_MASK_{idx}]]"

            orig = masks[idx]
            if not isinstance(orig, str): return str(orig)
            if orig.startswith('\\'): return orig

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
                        # 🚀 [V24.0] 利用指纹缓存
                        h = self.asset_pipeline._generate_fingerprint(target_asset_path, use_dedup=True)
                        meta = self.meta.get_asset_metadata(h)
                        if meta: alt_text = meta.get("alt_texts", {}).get(lang_code) or meta.get("alt_text", "")
                    except Exception: pass
                    
                    # 🚀 此处调用 process 会因为之前的 warm_assets 而极速命中或安全等待 DCL
                    processed_name = log_asset(self.asset_pipeline.process(target_asset_path, asset_filename, is_dry_run, slug=slug))
                    final_url = f"{root_path}{self.asset_base_url}{processed_name}".replace('//', '/')
                    return final_url if not orig.startswith('URL_ONLY_IMG:') else f"![{alt_text}]({final_url})"

                target_rel_path = self.meta.resolve_link(clean_path)
                if target_rel_path:
                    log_outlink(target_rel_path)
                    if self.link_resolver:
                        resolved = self.link_resolver.resolve_link(target_rel_path, lang_code, route_prefix, mapped_sub_dir)
                        if resolved: return resolved
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
                            h = self.asset_pipeline._generate_fingerprint(target_asset_path, use_dedup=True)
                            meta = self.meta.get_asset_metadata(h)
                            if meta:
                                alt_map = meta.get("alt_texts", {})
                                final_alt = alt_map.get(lang_code) or meta.get("alt_text") or orig_alt
                        except Exception: pass
                        
                        processed_name = log_asset(self.asset_pipeline.process(target_asset_path, asset_filename, is_dry_run, slug=slug))
                        final_url = f"{root_path}{self.asset_base_url}{processed_name}".replace('//', '/')
                        return f"![{final_alt}]({final_url})"
                return orig

            return orig

        final_body = body
        max_depth = 10
        current_depth = 0
        while re.search(r'\[\[STB_MASK_\d+\]\]', final_body) and current_depth < max_depth:
            final_body = re.sub(r'\[\[STB_MASK_\d+\]\]', unmask_fn, final_body)
            current_depth += 1

        if self.link_resolver:
            final_body = self.link_resolver.heal_content(final_body, lang_code, route_prefix, mapped_sub_dir)

        return final_body
