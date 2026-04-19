#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Egress Dispatcher
模块职责：物理出站分发器。
负责将 AI 处理完毕的纯净文本，进行方言解蔽、双链寻址映射、MDX 隔离与最终的物理落盘。
🚀 [V22 “元数据精炼版”]: 彻底消除 YAML 锚点与冗余时间戳格式。
"""

import os
import re
import urllib.parse
import yaml
import tempfile
import logging
import hashlib
from datetime import datetime
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

    def dispatch(self, asset_index, title, slug, masked_body, fm_dict, rel_path, lang_code, route_prefix, route_source, mapped_sub_dir, masks, is_dry_run, is_target=False, node_assets=None, node_ext_assets=None, node_outlinks=None, assets_lock=None, force_persistence_date=None):
        if not self.paths['target_base']: return ""
        
        # ... (内部工具函数保持不变)
        
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
            
            # 🚀 [V28 逻辑回归]：处理 URL 专用屏蔽标记（由 MaskingAndRoutingStep 产生）
            is_url_only_lnk = orig.startswith('URL_ONLY_LNK:')
            is_url_only_img = orig.startswith('URL_ONLY_IMG:')
            
            if is_url_only_lnk or is_url_only_img:
                clean_path = urllib.parse.unquote(orig.split(':', 1)[1].strip())
                if clean_path.startswith(('http://', 'https://', 'mailto:', '#')): return clean_path
                
                # 1. 尝试匹配物理资产
                asset_filename = os.path.basename(clean_path.split('?')[0].split('#')[0])
                target_asset_path = _get_closest_asset(asset_filename)
                if target_asset_path:
                    processed_name = log_asset(self.asset_pipeline.process(target_asset_path, asset_filename, is_dry_run))
                    return f"{self.asset_base_url}{processed_name}"
                
                # 2. 尝试解析逻辑文档链接 (Slug 寻址)
                target_rel_path = self.meta.resolve_link(clean_path) or self.meta.resolve_link(os.path.splitext(os.path.basename(clean_path))[0])
                if target_rel_path:
                    log_outlink(target_rel_path)
                    t_doc_info = self.meta.get_doc_info(target_rel_path)
                    t_slug = t_doc_info.get("slug") or re.sub(r'-+', '-', re.sub(r'[^\w\-]', '', os.path.splitext(os.path.basename(target_rel_path))[0].replace(' ', '-').lower())).strip('-')
                    t_prefix, t_source = t_doc_info.get("prefix", route_prefix), t_doc_info.get("source", route_source)
                    
                    # 🚀 召回路由于经理构造 URL
                    t_abs = os.path.join(self.paths['vault'], target_rel_path)
                    t_sub_dir = os.path.dirname(os.path.relpath(t_abs, os.path.join(self.paths['vault'], t_source)).replace('\\', '/')).replace('\\', '/')
                    if t_sub_dir == '.': t_sub_dir = ""
                    t_mapped_sub_dir = self.route_manager.get_mapped_sub_dir(t_sub_dir, is_dry_run=is_dry_run, allow_ai=False)
                    
                    return self.route_manager.resolve_logical_url(lang_code, t_prefix, t_mapped_sub_dir, t_slug)
                return clean_path

            if orig.startswith('\\'): return orig
            
            # 🚀 [V28 灵魂回归]：处理 Obsidian 风格的双链、图片嵌入
            if orig.startswith('![['):
                filename = orig[3:-2].split('|')[0].strip()
                alt_text = orig[3:-2].split('|')[1] if '|' in orig[3:-2] else filename
                target_asset_path = _get_closest_asset(filename) 
                if target_asset_path:
                    processed_name = log_asset(self.asset_pipeline.process(target_asset_path, filename, is_dry_run))
                    ext = os.path.splitext(processed_name)[1].lower()
                    return f"![{alt_text}]({self.asset_base_url}{processed_name})" if ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.tiff', '.svg'] else f"[{alt_text}]({self.asset_base_url}{processed_name})"
                return f"[{alt_text}](#broken-link)"
                
            elif orig.startswith('[['):
                target_text = orig[2:-2].split('|')[0].strip()
                custom_text = orig[2:-2].split('|')[1].strip() if '|' in orig[2:-2] else target_text
                
                # A. 检查是否为物理文件链接（如 PDF）
                target_asset_path = _get_closest_asset(target_text)
                if target_asset_path:
                    processed_name = log_asset(self.asset_pipeline.process(target_asset_path, target_text, is_dry_run))
                    return f"[{custom_text}]({self.asset_base_url}{processed_name})"
                
                # B. 检查是否为文档双链
                target_rel_path = self.meta.resolve_link(target_text)
                if target_rel_path:
                    log_outlink(target_rel_path)
                    t_doc_info = self.meta.get_doc_info(target_rel_path)
                    t_slug = t_doc_info.get("slug") or re.sub(r'-+', '-', re.sub(r'[^\w\-]', '', target_text.replace(' ', '-').lower())).strip('-')
                    t_prefix, t_source = t_doc_info.get("prefix", route_prefix), t_doc_info.get("source", route_source)
                    
                    t_abs = os.path.join(self.paths['vault'], target_rel_path)
                    t_sub_dir = os.path.dirname(os.path.relpath(t_abs, os.path.join(self.paths['vault'], t_source)).replace('\\', '/')).replace('\\', '/')
                    if t_sub_dir == '.': t_sub_dir = ""
                    t_mapped_sub_dir = self.route_manager.get_mapped_sub_dir(t_sub_dir, is_dry_run=is_dry_run, allow_ai=False)

                    url_path = self.route_manager.resolve_logical_url(lang_code, t_prefix, t_mapped_sub_dir, t_slug)
                    display_text = t_slug.replace('-', ' ').title() if is_target else custom_text
                    return f"[{display_text}]({url_path})"
                return orig
                
            elif orig.startswith('['):
                # 处理标准 Markdown 链接指向本地文件的情况
                match = re.match(r'\[(.*?)\]\((.*?)\)', orig)
                if match and not match.group(2).startswith(('http://', 'https://', 'mailto:', '#')):
                    link_text, link_path = match.groups()
                    clean_path = urllib.parse.unquote(link_path.strip())
                    
                    # 优先级：资产 -> 文档
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

                        url_path = self.route_manager.resolve_logical_url(lang_code, t_prefix, t_mapped_sub_dir, t_slug)
                        display_text = t_slug.replace('-', ' ').title() if is_target else link_text
                        return f"[{display_text}]({url_path})"
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
            import_pattern = re.compile(r'^(import\s+.*?from\s+[\'"].*?[\'"];?)$', re.MULTILINE)
            imports = import_pattern.findall(final_body)
            if imports:
                final_body = import_pattern.sub('', final_body)
                # 🚀 [去重并提升]：保护编译上下文的干净
                unique_imports = list(dict.fromkeys(imports))
                hoisted_imports = '\n'.join(unique_imports) + '\n\n'
                final_body = hoisted_imports + final_body.lstrip()

            # 🚀 [审美间距优化]：为组件与正文之间注入标准空行
            final_body = re.sub(r'([^\n])\n\s*(<[A-Z])', r'\1\n\n\2', final_body)
            final_body = re.sub(r'(</[A-Z][a-zA-Z0-9]*>|<[A-Z][^>]*/>)\n\s*([^\n<])', r'\1\n\n\2', final_body)

        if self.pub_cfg.append_credit:
            final_body += f"{self.pub_cfg.credit_text}\n"
        
        merged_fm = fm_dict.copy()
        merged_fm['title'] = slug.replace('-', ' ').title() if is_target else title
        
        src_abs_path = os.path.join(self.paths['vault'], rel_path)
        current_mtime = os.path.getmtime(src_abs_path)
        current_mtime_dt = datetime.fromtimestamp(current_mtime).astimezone()

        # 🚀 [V25-V27 时空分流协议]：生日溯源逻辑
        persistence_date_str = None
        post_date = merged_fm.get('date')
        
        # [V27 加固]：如果外部调度中心（多语言环境）强行锁定了生日，则无条件服从
        if force_persistence_date:
            try:
                post_date = datetime.fromisoformat(force_persistence_date)
                persistence_date_str = force_persistence_date
            except Exception:
                pass

        if not post_date:
            # 尝试回溯账本中的“固化生日”
            doc_info = self.meta.get_doc_info(rel_path)
            if doc_info and doc_info.get('persistent_date'):
                try:
                    hp_date = doc_info['persistent_date']
                    post_date = datetime.fromisoformat(hp_date)
                    persistence_date_str = hp_date
                except Exception:
                    post_date = current_mtime_dt
            else:
                # 新文件：将当前物理时间作为法定生日，并准备持久化
                post_date = current_mtime_dt
                persistence_date_str = post_date.isoformat()
        elif not persistence_date_str:
            # 若源文件有显式定义，则以源文件为准，并更新/同步到账本
            if isinstance(post_date, datetime):
                persistence_date_str = post_date.isoformat()
        
        merged_fm['date'] = post_date
            
        # 🚀 [V27 稳态加固]：注入技术指纹（仅监听模式），需位于语义适配之前以接受规则审查
        if getattr(self.meta, 'is_watch_mode', False):
            import random
            import string
            merged_fm['_illacme_ver'] = ''.join(random.choices(string.ascii_letters + string.digits, k=6))

        # 🚀 [V26 全域语义适配]：由适配器接管全量元数据投影 (含时间、标签、作者映射)
        merged_fm = self.ssg_adapter.adapt_metadata(
            merged_fm,
            current_mtime_dt, 
            merged_fm.get('author', 'Illacme Engine')
        )
        
        ordered_fm = {key: merged_fm.pop(key) for key in self.fm_order if key in merged_fm}
        ordered_fm.update(merged_fm)

        # 🚀 [审美加固]：强行将技术指纹置于元信息的最后一行，保持排版整洁
        if '_illacme_ver' in ordered_fm:
            ver_val = ordered_fm.pop('_illacme_ver')
            ordered_fm['_illacme_ver'] = ver_val

        # 🚀 [V22 “元数据精炼补丁”]：执行深度清理并调用无别名 Dumper
        cleaned_fm = _clean_frontmatter_for_yaml(ordered_fm)
        fm_str = "---\n" + yaml.dump(
            cleaned_fm, 
            Dumper=NoAliasDumper,
            allow_unicode=True, 
            default_flow_style=False, 
            sort_keys=False, 
            width=float("inf")
        ) + "---\n\n"

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
                with open(shadow_dest, 'w', encoding='utf-8') as f: f.write(shadow_body_content)
                
                rendered_body = self.ssg_adapter.convert_callouts(ssg_final_body)
                rendered_body = self.ssg_adapter.adapt_mdx_imports(rendered_body)
                rendered_body = rendered_body.replace('{title}', title)

                i18n_root = os.path.abspath(os.path.join(self.paths['target_base'], "../../"))
                tmp_sync_dir = os.path.join(i18n_root, ".tmp_sync")
                os.makedirs(tmp_sync_dir, exist_ok=True)
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                
                tmp_fd, tmp_path = tempfile.mkstemp(dir=tmp_sync_dir, suffix=".tmp")
                try:
                    with os.fdopen(tmp_fd, 'w', encoding='utf-8') as f: f.write(fm_str + rendered_body)
                    os.replace(tmp_path, dest)
                except Exception:
                    if os.path.exists(tmp_path): os.remove(tmp_path)
                    raise
                
                if self.janitor: self.janitor.mark_as_fresh(dest)
                if lang_code == self.i18n.source.lang_code:
                    self.syndicator.syndicate(ordered_fm, final_body, f"/{lang_code}/{mapped_sub_dir}/{slug}".replace('//', '/'))
            except Exception as e:
                logger.error(f"🛑 物理落盘失败: {e}")
            
        return hashlib.md5(shadow_body_content.encode('utf-8')).hexdigest(), persistence_date_str

# ==========================================
# 🛠 V22 元数据精炼辅助工具 (Module-Level Helpers)
# ==========================================
def _clean_frontmatter_for_yaml(data):
    """递归清理 Frontmatter：消除物理引用关系，保持对象类型"""
    if isinstance(data, dict):
        return {k: _clean_frontmatter_for_yaml(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [_clean_frontmatter_for_yaml(v) for v in data]
    return data

class NoAliasDumper(yaml.SafeDumper):
    """物理层禁用 YAML 别名/锚点的专用 Dumper，并强制 ISO 时间格式"""
    def ignore_aliases(self, data):
        return True

def _iso_datetime_representer(dumper, data):
    """强制输出带 T 的标准化日期 (ISO 8601)"""
    return dumper.represent_scalar('tag:yaml.org,2002:timestamp', data.isoformat())

NoAliasDumper.add_representer(datetime, _iso_datetime_representer)