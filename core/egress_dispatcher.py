#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Egress Dispatcher
模块职责：物理出站分发器。
负责将 AI 处理完毕的纯净文本，进行方言解蔽、双链寻址映射、MDX 隔离与最终的物理落盘。
🚀 [V16.4 架构重构]：彻底从 engine.py 中剥离，解除 God Class 的 I/O 耦合。
"""

import os
import re
import urllib.parse
import yaml
import tempfile
import logging
import hashlib
from datetime import datetime, timezone  # 🚀 [补入时空模块]
from .utils import sanitize_ai_response

logger = logging.getLogger("Illacme.plenipes")

class EgressDispatcher:
    def __init__(self, paths, meta, route_manager, asset_pipeline, ssg_adapter, mdx_resolver, syndicator, pub_cfg, fm_order, asset_base_url, i18n_cfg, janitor=None):
        """
        🚀 依赖注入：只接收执行写盘和正则解蔽所需的核心资产组件
        """
        self.paths = paths
        self.meta = meta
        self.route_manager = route_manager
        self.asset_pipeline = asset_pipeline
        self.ssg_adapter = ssg_adapter
        self.mdx_resolver = mdx_resolver
        self.syndicator = syndicator
        self.pub_cfg = pub_cfg
        self.fm_order = fm_order
        self.asset_base_url = asset_base_url
        self.i18n = i18n_cfg
        self.janitor = janitor

    # 🚀 完整剥离的核心派发逻辑，绝对不省略任何一行代码
    def dispatch(self, asset_index, title, slug, masked_body, fm_dict, rel_path, lang_code, route_prefix, route_source, mapped_sub_dir, masks, is_dry_run, is_target=False, node_assets=None, node_ext_assets=None, node_outlinks=None, assets_lock=None):
        if not self.paths['target_base']: return ""
        
        def _get_closest_asset(target_filename):
            candidates = asset_index.get(target_filename, [])
            if not candidates: return None
            if len(candidates) == 1: return candidates[0]
            current_abs_dir = os.path.dirname(os.path.join(self.paths['vault'], rel_path))
            return sorted(candidates, key=lambda p: len(os.path.commonprefix([current_abs_dir, os.path.dirname(p)])), reverse=True)[0]
        
        def unmask_fn(m):
            idx = int(re.search(r'\d+', m.group(0)).group())
            orig = masks[idx]
            if orig.startswith('\\'): return orig 
            
            def log_asset(p_name):
                if node_assets is not None and assets_lock is not None:
                    with assets_lock: node_assets.add(p_name)
                return p_name

            def log_outlink(tgt_path):
                if tgt_path and node_outlinks is not None and assets_lock is not None:
                    with assets_lock: node_outlinks.add(tgt_path)

            if orig.startswith('URL_ONLY_IMG:'):
                clean_path = urllib.parse.unquote(orig.replace('URL_ONLY_IMG:', '').strip())
                if clean_path.startswith(('http://', 'https://', '//')): return clean_path
                filename = os.path.basename(clean_path.split('?')[0].split('#')[0])
                target_asset_path = _get_closest_asset(filename)
                if target_asset_path:
                    processed_name = log_asset(self.asset_pipeline.process(target_asset_path, filename, is_dry_run))
                    return f"{self.asset_base_url}{processed_name}"
                return clean_path
                
            if orig.startswith('URL_ONLY_LNK:'):
                clean_path = urllib.parse.unquote(orig.replace('URL_ONLY_LNK:', '').strip())
                if clean_path.startswith(('http://', 'https://', 'mailto:', '#')): return clean_path
                
                asset_filename = os.path.basename(clean_path.split('?')[0].split('#')[0])
                target_asset_path = _get_closest_asset(asset_filename)
                if target_asset_path:
                    processed_name = log_asset(self.asset_pipeline.process(target_asset_path, asset_filename, is_dry_run))
                    return f"{self.asset_base_url}{processed_name}"
                
                target_rel_path = self.meta.resolve_link(clean_path) or self.meta.resolve_link(os.path.splitext(os.path.basename(clean_path))[0])
                if target_rel_path:
                    log_outlink(target_rel_path)
                    t_doc_info = self.meta.get_doc_info(target_rel_path)
                    t_slug = t_doc_info.get("slug") or re.sub(r'-+', '-', re.sub(r'[^\w\-]', '', os.path.splitext(os.path.basename(target_rel_path))[0].replace(' ', '-').lower())).strip('-')
                    t_prefix, t_source = t_doc_info.get("prefix", route_prefix), t_doc_info.get("source", route_source)
                    t_abs = os.path.join(self.paths['vault'], target_rel_path)
                    t_sub_dir = os.path.dirname(os.path.relpath(t_abs, os.path.join(self.paths['vault'], t_source)).replace('\\', '/')).replace('\\', '/')
                    if t_sub_dir == '.': t_sub_dir = ""
                    t_mapped_sub_dir = self.route_manager.get_mapped_sub_dir(t_sub_dir, is_dry_run=is_dry_run, allow_ai=False)
                    t_prefix_part = f"/{t_prefix}" if t_prefix else ""
                    raw_url = f"/{lang_code}{t_prefix_part}/{t_mapped_sub_dir}/{t_slug}" if t_mapped_sub_dir else f"/{lang_code}{t_prefix_part}/{t_slug}"
                    return re.sub(r'/+', '/', raw_url)
                return clean_path

            if orig.startswith('![['):
                filename = orig[3:-2].split('|')[0].strip()
                alt_text = orig[3:-2].split('|')[1] if '|' in orig[3:-2] else filename
                target_asset_path = _get_closest_asset(filename) 
                if target_asset_path:
                    processed_name = log_asset(self.asset_pipeline.process(target_asset_path, filename, is_dry_run))
                    ext = os.path.splitext(processed_name)[1].lower()
                    return f"![{alt_text}]({self.asset_base_url}{processed_name})" if ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.tiff', '.svg'] else f"[{alt_text}]({self.asset_base_url}{processed_name})"
                return f"[{alt_text}](#broken-link)"
                
            elif orig.startswith('!['):
                match = re.match(r'\!\[(.*?)\]\((.*?)\)', orig)
                if match:
                    alt_text, img_path = match.groups()
                    filename = os.path.basename(urllib.parse.unquote(img_path.strip()).split('?')[0].split('#')[0])
                    target_asset_path = _get_closest_asset(filename)
                    if target_asset_path:
                        processed_name = log_asset(self.asset_pipeline.process(target_asset_path, filename, is_dry_run))
                        return f"![{alt_text}]({self.asset_base_url}{processed_name})"
                    if not img_path.startswith(('http://', 'https://', '/', '#')):
                        return f"![{alt_text}](/broken-image.png)"
                return orig
                
            elif orig.startswith('[['):
                target_text = orig[2:-2].split('|')[0].strip()
                custom_zh_text = orig[2:-2].split('|')[1].strip() if '|' in orig[2:-2] else target_text
                target_asset_path = _get_closest_asset(target_text)
                if target_asset_path:
                    processed_name = log_asset(self.asset_pipeline.process(target_asset_path, target_text, is_dry_run))
                    return f"[{custom_zh_text}]({self.asset_base_url}{processed_name})"
                
                target_rel_path = self.meta.resolve_link(target_text)
                if target_rel_path:
                    log_outlink(target_rel_path)
                    t_doc_info = self.meta.get_doc_info(target_rel_path)
                    t_slug = t_doc_info.get("slug") or re.sub(r'-+', '-', re.sub(r'[^\w\-]', '', target_text.replace(' ', '-').lower())).strip('-')
                    t_prefix, t_source = t_doc_info.get("prefix", route_prefix), t_doc_info.get("source", route_source)
                    if not is_dry_run: self.meta.register_document(target_rel_path, target_text, slug=t_slug, route_prefix=t_prefix, route_source=t_source)
                    t_abs = os.path.join(self.paths['vault'], target_rel_path)
                    t_sub_dir = os.path.dirname(os.path.relpath(t_abs, os.path.join(self.paths['vault'], t_source)).replace('\\', '/')).replace('\\', '/')
                    if t_sub_dir == '.': t_sub_dir = ""
                    t_mapped_sub_dir = self.route_manager.get_mapped_sub_dir(t_sub_dir, is_dry_run=is_dry_run, allow_ai=False)
                    t_prefix_part = f"/{t_prefix}" if t_prefix else ""
                    raw_url = f"/{lang_code}{t_prefix_part}/{t_mapped_sub_dir}/{t_slug}" if t_mapped_sub_dir else f"/{lang_code}{t_prefix_part}/{t_slug}"
                    display_text = t_slug.replace('-', ' ').title() if is_target else custom_zh_text
                    return f"[{display_text}]({re.sub(r'/+', '/', raw_url)})"
                return f"[{custom_zh_text}](#broken-link)"
                
            elif orig.startswith('['):
                match = re.match(r'\[(.*?)\]\((.*?)\)', orig)
                if match and not match.group(2).startswith(('http://', 'https://', 'mailto:', '#')):
                    link_text, link_path = match.groups()
                    clean_path = urllib.parse.unquote(link_path.strip())
                    asset_filename = os.path.basename(clean_path.split('?')[0].split('#')[0])
                    target_asset_path = _get_closest_asset(asset_filename)
                    if target_asset_path:
                        processed_name = log_asset(self.asset_pipeline.process(target_asset_path, asset_filename, is_dry_run))
                        return f"[{link_text}]({self.asset_base_url}{processed_name})"

                    target_rel_path = self.meta.resolve_link(clean_path) or self.meta.resolve_link(os.path.splitext(os.path.basename(clean_path))[0])
                    if target_rel_path:
                        log_outlink(target_rel_path)
                        t_doc_info = self.meta.get_doc_info(target_rel_path)
                        t_slug = t_doc_info.get("slug") or re.sub(r'-+', '-', re.sub(r'[^\w\-]', '', os.path.splitext(os.path.basename(target_rel_path))[0].replace(' ', '-').lower())).strip('-')
                        t_prefix, t_source = t_doc_info.get("prefix", route_prefix), t_doc_info.get("source", route_source)
                        t_abs = os.path.join(self.paths['vault'], target_rel_path)
                        t_sub_dir = os.path.dirname(os.path.relpath(t_abs, os.path.join(self.paths['vault'], t_source)).replace('\\', '/')).replace('\\', '/')
                        if t_sub_dir == '.': t_sub_dir = ""
                        t_mapped_sub_dir = self.route_manager.get_mapped_sub_dir(t_sub_dir, is_dry_run=is_dry_run, allow_ai=False)
                        t_prefix_part = f"/{t_prefix}" if t_prefix else ""
                        raw_url = f"/{lang_code}{t_prefix_part}/{t_mapped_sub_dir}/{t_slug}" if t_mapped_sub_dir else f"/{lang_code}{t_prefix_part}/{t_slug}"
                        display_text = t_slug.replace('-', ' ').title() if is_target else link_text
                        return f"[{display_text}]({re.sub(r'/+', '/', raw_url)})"
                return orig
            return orig

        final_body = sanitize_ai_response(masked_body)
        max_depth = 10
        current_depth = 0
        while re.search(r'\[\[STB_MASK_\d+\]\]', final_body) and current_depth < max_depth:
            final_body = re.sub(r'\[\[STB_MASK_\d+\]\]', unmask_fn, final_body)
            current_depth += 1
            
        if current_depth == max_depth:
            logger.warning(f"⚠️ [防御预警] {rel_path} 解蔽层数达到上限，可能存在死循环屏蔽。")

        if rel_path.lower().endswith('.mdx'):
            final_body = re.sub(r'((?:import|export)\s+[\s\S]*?[\'"]\s*;?)\n([^\n])', r'\1\n\n\2', final_body)
            final_body = re.sub(r'([^\n])\n\s*(<[A-Z])', r'\1\n\n\2', final_body)
            final_body = re.sub(r'(</[A-Z][a-zA-Z0-9]*>|<[A-Z][^>]*/>)\n\s*([^\n<])', r'\1\n\n\2', final_body)

        if self.pub_cfg.get('append_credit', False):
            final_body += f"{self.pub_cfg.get('credit_text', '')}\n"
        
        merged_fm = fm_dict.copy()
        merged_fm['title'] = slug.replace('-', ' ').title() if is_target else title
        
        # ==========================================
        # 🚀 [V16.9 物理时间溯源补丁]：跨框架兼容与 OS 底层时空锚定
        # ==========================================
        if not merged_fm.get('date'):
            try:
                # 1. 探针定位：拼装 Obsidian 源文件的绝对物理路径
                src_abs_path = os.path.join(self.paths['vault'], rel_path)
                
                # 2. 物理提取：从操作系统底层抓取文件的最后修改时间戳 (mtime)
                mtime = os.path.getmtime(src_abs_path)
                
                # 3. 时区转换：将 Unix 时间戳转换为带本地时区的原生 datetime 对象
                merged_fm['date'] = datetime.fromtimestamp(mtime).astimezone()
            except Exception as e:
                # 极端边界防御：如果文件句柄被锁或发生 I/O 错误，降级为当前时间
                logger.warning(f"⚠️ [时空溯源失败] 无法读取 {rel_path} 的物理时间，降级为当前时间: {e}")
                merged_fm['date'] = datetime.now(timezone.utc).astimezone()
            
        # 4. 物理斩断 Docusaurus Docs 的 Git 探针 (防 1970 纪元陷阱)
        if not merged_fm.get('last_update'):
            merged_fm['last_update'] = {
                'date': merged_fm.get('date'),
                'author': merged_fm.get('author', 'Illacme Engine')
            }
        
        import_pattern = re.compile(r'^(import\s+.*?from\s+[\'"].*?[\'"];?)$', re.MULTILINE)
        imports = import_pattern.findall(final_body)
        if imports:
            final_body = import_pattern.sub('', final_body)
            final_body = '\n'.join(list(dict.fromkeys(imports))) + '\n\n' + final_body.lstrip()
            
        ordered_fm = {key: merged_fm.pop(key) for key in self.fm_order if key in merged_fm}
        ordered_fm.update(merged_fm)

        protected_blocks = ordered_fm.pop('__illacme_protected_blocks', None)
        if protected_blocks:
            final_body = final_body.rstrip() + f"\n\n{protected_blocks}\n"

        fm_str = "---\n" + yaml.dump(ordered_fm, allow_unicode=True, default_flow_style=False, sort_keys=False, width=float("inf")) + "---\n\n"

        if node_ext_assets is not None and assets_lock is not None:
            ext_md_pattern = re.compile(r'\!\[.*?\]\((https?://[^\)]+)\)')
            ext_html_pattern = re.compile(r'<img[^>]+src=["\'](https?://[^"\']+)["\']')
            with assets_lock:
                for match in ext_md_pattern.finditer(final_body): node_ext_assets.add(match.group(1))
                for match in ext_html_pattern.finditer(final_body): node_ext_assets.add(match.group(1))

        ext = os.path.splitext(rel_path)[1].lower()
        dest = self.route_manager.resolve_physical_path(self.paths['target_base'], lang_code, route_prefix, mapped_sub_dir, slug, ext)
        shadow_dest = self.route_manager.resolve_physical_path(self.paths['shadow'], lang_code, route_prefix, mapped_sub_dir, slug, ext)

        shadow_body_content = fm_str + final_body
        ssg_final_body = final_body

        if ext == '.mdx':
            src_abs_path = os.path.join(self.paths['vault'], rel_path)
            ssg_final_body = self.mdx_resolver.remap_imports(ssg_final_body, src_abs_path, dest)

        if not is_dry_run:
            try:
                os.makedirs(os.path.dirname(shadow_dest), exist_ok=True)
                with open(shadow_dest, 'w', encoding='utf-8') as f: 
                    f.write(shadow_body_content)
                
                rendered_body = self.ssg_adapter.convert_callouts(ssg_final_body)
                rendered_body = self.ssg_adapter.adapt_mdx_imports(rendered_body)
                rendered_body = rendered_body.replace('{title}', title)

                os.makedirs(os.path.dirname(dest), exist_ok=True)
                tmp_fd, tmp_path = tempfile.mkstemp(dir=os.path.dirname(dest), suffix=".tmp.md")
                with os.fdopen(tmp_fd, 'w', encoding='utf-8') as f: 
                    f.write(fm_str + rendered_body)
                
                os.replace(tmp_path, dest)
                
                if self.janitor:
                    self.janitor.mark_as_fresh(dest)

                if lang_code == self.i18n.get('source', {}).get('lang_code', 'zh-cn'):
                    self.syndicator.syndicate(ordered_fm, final_body, f"/{lang_code}/{mapped_sub_dir}/{slug}".replace('//', '/'))
                    
            except Exception as e:
                logger.error(f"🛑 物理落盘失败 (Shadow/SSG 写入异常): {e}")
            
        return hashlib.md5(shadow_body_content.encode('utf-8')).hexdigest()