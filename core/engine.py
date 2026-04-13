#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Main Engine (Pipeline Driven)
模块职责：全局生命周期调度总线。
架构进化：引入 Context + Pipeline 模式，彻底消灭上帝函数。
"""

import os
import re
import time
import yaml
import fnmatch
import logging
import tempfile
import urllib.parse
import threading
import concurrent.futures

from .utils import load_unified_config
from .adapters.ingress import InputAdapter
from .adapters.egress import SSGAdapter
from .adapters.ast_resolver import TransclusionResolver, MDXResolver
from .adapters.api_egress import WebhookBroadcaster
from .adapters.syndication import ContentSyndicator
from .adapters.ai_provider import TranslatorFactory
from .storage.ledger import MetadataManager
from .asset_pipeline import AssetPipeline
from .router import RouteManager
from .janitor import JanitorService

# 引入我们刚刚创建的管线组件
from .pipeline.context import SyncContext
from .pipeline.runner import Pipeline
from .pipeline.steps import (ReadAndNormalizeStep, ASTAndPurifyStep, MetadataAndHashStep, AISlugAndSEOStep, MaskingAndRoutingStep, ContextualImageAltStep)

logger = logging.getLogger("Illacme.plenipes")

class IllacmeEngine:
    def __init__(self, config_path):
        self.config = load_unified_config(config_path)
        self.sys_tuning = self.config.get('system_tuning', {})
        self.sys_cfg = self.config.get('system', {})
        self.fm_defaults = self.config.get('frontmatter_defaults') or {}
        self.max_workers = self.sys_cfg.get('max_workers', 5)
        self.auto_save_interval = self.sys_cfg.get('auto_save_interval', 2.0)
        self.max_depth = self.sys_cfg.get('max_depth', 3)
        self.fm_order = self.config.get('frontmatter_order', ['title', 'description', 'keywords', 'author', 'date', 'tags', 'categories'])
        
        log_level_str = self.sys_cfg.get('log_level', 'INFO').upper()
        logger.setLevel(getattr(logging, log_level_str, logging.INFO))
        
        self.vault_root = os.path.abspath(os.path.expanduser(self.config.get('vault_root', '')))
        self.route_matrix = self.config.get('route_matrix', [])
        self.active_theme = self.config.get('active_theme', 'starlight')
        
        output_paths = self.config.get('output_paths', {})
        target_base_dir = output_paths.get('markdown_dir')
        target_assets_dir = output_paths.get('assets_dir')
        
        theme_opts = self.config.get('theme_options', {}).get(self.active_theme, {})
        self.ssg_adapter = SSGAdapter(theme_opts.get('syntax_engine', self.active_theme), custom_adapters=self.config.get('framework_adapters', {}))
        
        editor_settings = self.config.get('editor_settings', {})
        self.input_adapter = InputAdapter(editor_settings.get('active_editor', 'auto'), editor_settings.get('custom_sanitizers', {}))
        
        self.paths = {
            "vault": self.vault_root,
            "target_base": os.path.abspath(os.path.expanduser(target_base_dir)) if target_base_dir else None,
            "assets": os.path.abspath(os.path.expanduser(target_assets_dir)) if target_assets_dir else None,
            "db": os.path.abspath(os.path.expanduser(self.config.get('metadata_db', './plenipes_metadata.json')))
        }
        
        self.i18n = self.config.get('i18n_settings', {})
        self.seo_cfg = self.config.get('seo_settings', {})
        self.img_cfg = self.config.get('image_settings', {})
        self.pub_cfg = self.config.get('publish_control', {})
        self.asset_base_url = self.img_cfg.get('base_url', '/assets/').rstrip('/') + '/'
        
        # 依赖注入
        self.meta = MetadataManager(self.paths["db"], self.auto_save_interval)
        self.translator = TranslatorFactory.create(self.config.get('translation', {}), sys_tuning_cfg=self.sys_tuning)
        self.asset_pipeline = AssetPipeline(self.paths['assets'], self.img_cfg)
        self.route_manager = RouteManager(self.meta, self.translator)
        
        self.asset_index = {}
        self.md_index = {}
        self._build_indexes()
        
        self.transclusion_resolver = TransclusionResolver(self.md_index, self.asset_index, self.max_depth)
        self._processing_locks = {}
        self._global_engine_lock = threading.Lock()
        
        self.janitor = JanitorService(self._global_engine_lock, self._processing_locks, self.paths, self.meta, self.route_manager, self.i18n)
        self.mdx_resolver = MDXResolver(self.paths["vault"], self.paths["target_base"])
        self.broadcaster = WebhookBroadcaster(self.pub_cfg, sys_tuning_cfg=self.sys_tuning)
        self.syndicator = ContentSyndicator(self.config.get('syndication', {}), self.config.get('site_url', ''), sys_tuning_cfg=self.sys_tuning)

    def _get_document_lock(self, rel_path):
        with self._global_engine_lock:
            if rel_path not in self._processing_locks:
                self._processing_locks[rel_path] = threading.Lock()
            return self._processing_locks[rel_path]

    def _build_indexes(self):
        for root, dirs, files in os.walk(self.paths['vault']):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for f in files:
                if f.startswith("."): continue 
                abs_path = os.path.join(root, f)
                if f.endswith((".md", ".mdx")):
                    self.md_index[f] = abs_path
                    self.md_index[os.path.splitext(f)[0]] = abs_path
                else:
                    if f not in self.asset_index: self.asset_index[f] = []
                    self.asset_index[f].append(abs_path)

    def _is_excluded(self, rel_path):
        for p in self.pub_cfg.get('exclude_patterns', []):
            if fnmatch.fnmatch(rel_path, p) or fnmatch.fnmatch(os.path.basename(rel_path), p): return True
        return False

    def get_lang_name_by_code(self, code):
        """
        🚀 映射助手：根据语种代码获取对应的自然语言名称
        该方法直接对接 config.yaml 中的 i18n_settings，确保 AI 能够获得准确的翻译目标描述。
        """
        # 1. 检查是否为源语言代码 (例如 zh-cn -> 中文)
        src_cfg = self.i18n.get('source', {})
        if src_cfg.get('code') == code:
            return src_cfg.get('name', 'Chinese')
        
        # 2. 在目标语言配置阵列中查找 (例如 en -> English)
        targets = self.i18n.get('targets', [])
        for target in targets:
            if target.get('code') == code:
                # 优先返回配置中定义的 name，若无则返回 code 兜底
                return target.get('name', code)
        
        # 3. 物理兜底：针对常见的标准代码进行硬核映射
        fallback_map = {
            'en': 'English',
            'zh-cn': 'Chinese',
            'ja': 'Japanese',
            'ko': 'Korean'
        }
        return fallback_map.get(code.lower(), code)

    def sync_document(self, src_path, route_prefix, route_source, is_dry_run=False, force_sync=False):
        """🚀 核心管线调度枢纽"""
        rel_path = os.path.relpath(src_path, self.paths['vault']).replace('\\', '/')
        if self._is_excluded(rel_path): return

        doc_lock = self._get_document_lock(rel_path)
        if not doc_lock.acquire(blocking=False): return

        try:
            # 🚀 [架构升级 V15.2]：目标端物理探针 (Target Physical Probe)
            # 在进入管线前，如果非强制同步，则核验所有目标语种的物理产物是否健在
            if not force_sync and self.paths['target_base']:
                doc_info = self.meta.get_doc_info(rel_path)
                # 仅当账本里存在该文件（说明之前成功同步过），才核验其产物
                if doc_info and doc_info.get('hash') and doc_info.get('slug'):
                    slug = doc_info['slug']
                    target_files_missing = False
                    
                    # 推导当前文件的前端映射目录
                    t_abs = os.path.join(self.paths['vault'], rel_path)
                    t_sub_dir = os.path.dirname(os.path.relpath(t_abs, os.path.join(self.paths['vault'], route_source)).replace('\\', '/')).replace('\\', '/')
                    if t_sub_dir == '.': t_sub_dir = ""
                    mapped_sub_dir = self.route_manager.get_mapped_sub_dir(t_sub_dir, is_dry_run=is_dry_run, allow_ai=False)
                    ext = os.path.splitext(rel_path)[1].lower()
                    
                    # 收集需要核验的语种白名单
                    langs_to_check = []
                    src_code = self.i18n.get('source', {}).get('code', 'zh-cn')
                    if src_code: langs_to_check.append(src_code)
                    
                    if self.i18n.get('enabled', True):
                        for t in self.i18n.get('targets', []):
                            if t.get('code'): langs_to_check.append(t['code'])
                            
                    # 交叉比对硬盘物理文件
                    for code in langs_to_check:
                        expected_dest = os.path.join(self.paths['target_base'], code, route_prefix, mapped_sub_dir, f"{slug}{ext}")
                        if not os.path.exists(expected_dest):
                            target_files_missing = True
                            break
                            
                    if target_files_missing:
                        logger.info(f"🩹 [状态机自愈] {rel_path}：检测到前端物理产物丢失，强行打破增量锁触发重建！")
                        force_sync = True

            # 1. 组装上下文与管线
            ctx = SyncContext(self, src_path, route_prefix, route_source, is_dry_run, force_sync)
            pipeline = Pipeline()
            pipeline.add_step(ReadAndNormalizeStep()) \
                    .add_step(ASTAndPurifyStep()) \
                    .add_step(MetadataAndHashStep()) \
                    .add_step(AISlugAndSEOStep()) \
                    .add_step(ContextualImageAltStep()) \
                    .add_step(MaskingAndRoutingStep())
            
            # 2. 执行管线前置加工
            pipeline.execute(ctx)
            if ctx.is_aborted: return

            # 3. 后置阶段：SEO 注入闭包与分发 (Phase 15)
            seo_lock = threading.Lock()
            def inject_seo(fm, lang_code, text_content):
                # 💡 专家视角：不再在闭包里写复杂的 Prompt 逻辑，而是直接调用 provider
                lang_name = self.get_lang_name_by_code(lang_code) # 封装一个获取语言名称的方法
                seo_data, success = self.translator.generate_seo_metadata(text_content, lang_name, ctx.is_dry_run)
                
                if success and seo_data:
                    fm['description'] = seo_data.get('description', '')
                    fm['keywords'] = seo_data.get('keywords', '')
                return fm

            src_cfg = self.i18n.get('source', {})
            if src_cfg:
                src_code = src_cfg.get('code', 'zh-cn')
                src_fm = inject_seo(ctx.base_fm.copy(), src_code, ctx.body_content)
                self._dispatch_output(ctx.title, ctx.slug, ctx.masked_source, src_fm, ctx.rel_path, src_code, ctx.route_prefix, ctx.route_source, ctx.mapped_sub_dir, ctx.masks, ctx.is_dry_run, node_assets=ctx.node_assets, node_ext_assets=ctx.node_ext_assets, assets_lock=ctx.assets_lock)
    
            # 🚀 [架构补丁]：激活多语言管线总闸
            i18n_enabled = self.i18n.get('enabled', True)
            targets = self.i18n.get('targets', [])

            if i18n_enabled and targets and not ctx.is_silent_edit:
                def process_target(target):
                    code = target.get('code')
                    if not code: return None
                    final_body, target_health = ctx.masked_source, True
                    
                    # 👈 提取一份当前文章的基础元数据字典
                    target_fm = ctx.base_fm.copy() 

                    if target.get('translate_body', False):
                        if is_dry_run:
                            final_body = f"[DRY-RUN]\n{ctx.masked_source}"
                            target_fm['title'] = f"[EN] {target_fm.get('title', '')}"
                        else:
                            try:
                                target_lang_name = target.get('name', code)
                                source_lang_name = self.i18n.get('source', {}).get('name', '中文')
                                
                                if self.config.get('system', {}).get('verbose_ai_logs', True):
                                    logger.info(f"🌐 [AI 翻译] 正在将正文及元数据转换为目标语言 ({code})...")
                                
                                # 1. 翻译正文 (Markdown Body)
                                final_body = self.translator.translate(ctx.masked_source, source_lang_name, target_lang_name)
                                
                                # 2. 翻译元数据 (Title) -> 采用极致强硬的 Prompt 斩断大模型的废话
                                if target_fm.get('title'):
                                    meta_prompt = f"Target: Translate this title to {target_lang_name}. Rule: Output ONLY the translated string, NO quotes, NO explanation, NO conversational filler. Title: '{target_fm['title']}'"
                                    raw_title = self.translator.translate(meta_prompt, "Auto", "Meta Title")
                                    # 物理级除垢：防止有些笨模型依然加了双引号
                                    target_fm['title'] = raw_title.replace('"', '').replace('\n', '').strip()
                                    
                            except Exception as e:
                                logger.warning(f"⚠️ [翻译失败] 文章 {rel_path} ({code}) 翻译过程中断: {e}")
                                target_health = False
                    
                    # 3. 执行 SEO 注入
                    # 💡 架构魔法：此时传入的是纯正的英文 final_body，SEO 引擎会直接原生提取出完美的英文 Description 和 Keywords！
                    target_fm = inject_seo(target_fm, code, final_body)
                    
                    return (code, final_body, target_fm, target_health)
    
                # 使用系统配置的并发数 (max_workers) 启动并发翻译阵列
                with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                    future_to_code = {executor.submit(process_target, t): t for t in targets if t.get('code')}
                    for future in concurrent.futures.as_completed(future_to_code):
                        res = future.result()
                        if res:
                            t_code, t_body, t_fm, t_health = res
                            if not t_health: ctx.ai_health_flag[0] = False
                            self._dispatch_output(ctx.title, ctx.slug, t_body, t_fm, rel_path, t_code, route_prefix, route_source, ctx.mapped_sub_dir, ctx.masks, is_dry_run, is_target=True, node_assets=ctx.node_assets, node_ext_assets=ctx.node_ext_assets, assets_lock=ctx.assets_lock)
            elif not i18n_enabled and targets:
                # 💡 专家视角日志提示：当存在 target 但总闸关闭时，给出静默跳过提示
                logger.debug(f"🤫 [多语言跳过] {rel_path}：检测到 i18n 总闸已关闭，已绕过所有目标语种翻译任务。")

            # 4. 终态记录与广播 (Phase 16)
            if not ctx.is_dry_run:
                final_assets, final_ext_assets = list(ctx.node_assets), list(ctx.node_ext_assets)
                elapsed = time.perf_counter() - ctx.node_start_perf
                persist_hash = ctx.current_hash if ctx.ai_health_flag[0] else ""
                
                self.meta.register_document(ctx.rel_path, ctx.title, slug=ctx.slug, file_hash=persist_hash, seo_data=ctx.seo_data, route_prefix=ctx.route_prefix, route_source=ctx.route_source, assets=final_assets, ext_assets=final_ext_assets)
                
                if ctx.is_silent_edit: logger.info(f"✨ [静默直传成功] {ctx.rel_path} | ⏱️ 耗时: {elapsed:.2f} 秒")
                elif ctx.ai_health_flag[0]:
                    logger.info(f"✨ [同步成功] {ctx.rel_path} | 📦 资产: {len(final_assets)} | ⚡️ 耗时: {elapsed:.2f} 秒")
                    self.broadcaster.broadcast(ctx.title, ctx.rel_path, src_cfg.get('code') or 'zh-cn', ctx.mapped_sub_dir, ctx.slug)
                else: logger.warning(f"🚧 [局部降级] {ctx.rel_path} 部分 AI 任务不完整，已拦截指纹缓存。")

        finally:
            doc_lock.release()

    def _dispatch_output(self, title, slug, masked_body, fm_dict, rel_path, lang_code, route_prefix, route_source, mapped_sub_dir, masks, is_dry_run, is_target=False, node_assets=None, node_ext_assets=None, assets_lock=None):
        """核心写盘辅助函数 (逻辑未改动，保持字节级一致)"""
        if not self.paths['target_base']: return
        
        def _get_closest_asset(target_filename):
            candidates = self.asset_index.get(target_filename, [])
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

            # --- 🚀 增强处理：Markdown 标准图片图片 ![Alt](Path) ---
            if orig.startswith('!['):
                match = re.match(r'\!\[(.*?)\]\((.*?)\)', orig)
                if match:
                    alt_text, img_path = match.groups()
                    
                    # [专家逻辑]：如果当前是英文版，但 alt_text 包含中文，说明之前的 Masking 屏蔽过重
                    # 我们在这里执行一次快速的语义转换补偿（如果此时 AI 已经翻译了 body，这里可以尝试推导）
                    # 💡 更优方案是在 Masking 阶段只屏蔽 (path)，这里我们先保证路径的绝对正确
                    filename = os.path.basename(urllib.parse.unquote(img_path.strip()).split('?')[0].split('#')[0])
                    target_asset_path = _get_closest_asset(filename)
                    
                    if target_asset_path:
                        processed_name = log_asset(self.asset_pipeline.process(target_asset_path, filename, is_dry_run))
                        
                        # 💡 优化点：如果 alt_text 是中文且处于英文分发阶段，
                        # 此时 final_body 已经是英文了，AI 应该已经在正文中翻译了 alt 占位符。
                        # 这里我们优先返回处理后的物理路径。
                        return f"![{alt_text}]({self.asset_base_url}{processed_name})"
                return orig
                
            elif orig.startswith('!['):
                match = re.match(r'\!\[(.*?)\]\((.*?)\)', orig)
                if match:
                    alt_text, img_path = match.groups()
                    filename = os.path.basename(urllib.parse.unquote(img_path.strip()).split('?')[0].split('#')[0])
                    target_asset_path = _get_closest_asset(filename)
                    if target_asset_path:
                        processed_name = log_asset(self.asset_pipeline.process(target_asset_path, filename, is_dry_run))
                        return f"![{alt_text}]({self.asset_base_url}{processed_name})"
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
                    t_doc_info = self.meta.get_doc_info(target_rel_path)
                    t_slug = t_doc_info.get("slug") or re.sub(r'-+', '-', re.sub(r'[^\w\-]', '', target_text.replace(' ', '-').lower())).strip('-')
                    t_prefix, t_source = t_doc_info.get("prefix", route_prefix), t_doc_info.get("source", route_source)
                    if not is_dry_run: self.meta.register_document(target_rel_path, target_text, slug=t_slug, route_prefix=t_prefix, route_source=t_source)
                    
                    t_abs = os.path.join(self.paths['vault'], target_rel_path)
                    t_sub_dir = os.path.dirname(os.path.relpath(t_abs, os.path.join(self.paths['vault'], t_source)).replace('\\', '/')).replace('\\', '/')
                    if t_sub_dir == '.': t_sub_dir = ""

                    t_mapped_sub_dir = self.route_manager.get_mapped_sub_dir(t_sub_dir, is_dry_run=is_dry_run, allow_ai=True)
                    t_prefix_part = f"/{t_prefix}" if t_prefix else ""
                    raw_url = f"/{lang_code}{t_prefix_part}/{t_mapped_sub_dir}/{t_slug}" if t_mapped_sub_dir else f"/{lang_code}{t_prefix_part}/{t_slug}"
                    display_text = t_slug.replace('-', ' ').title() if is_target else custom_zh_text
                    return f"[{display_text}]({re.sub(r'/+', '/', raw_url)})"
                return orig
                
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
                        t_doc_info = self.meta.get_doc_info(target_rel_path)
                        t_slug = t_doc_info.get("slug") or re.sub(r'-+', '-', re.sub(r'[^\w\-]', '', os.path.splitext(os.path.basename(target_rel_path))[0].replace(' ', '-').lower())).strip('-')
                        t_prefix, t_source = t_doc_info.get("prefix", route_prefix), t_doc_info.get("source", route_source)
                        
                        t_abs = os.path.join(self.paths['vault'], target_rel_path)
                        t_sub_dir = os.path.dirname(os.path.relpath(t_abs, os.path.join(self.paths['vault'], t_source)).replace('\\', '/')).replace('\\', '/')
                        if t_sub_dir == '.': t_sub_dir = ""

                        t_mapped_sub_dir = self.route_manager.get_mapped_sub_dir(t_sub_dir, is_dry_run=is_dry_run, allow_ai=True)
                        t_prefix_part = f"/{t_prefix}" if t_prefix else ""
                        raw_url = f"/{lang_code}{t_prefix_part}/{t_mapped_sub_dir}/{t_slug}" if t_mapped_sub_dir else f"/{lang_code}{t_prefix_part}/{t_slug}"
                        display_text = t_slug.replace('-', ' ').title() if is_target else link_text
                        return f"[{display_text}]({re.sub(r'/+', '/', raw_url)})"
                return orig
            return orig

        final_body = re.sub(r'\[\[STB_MASK_\d+\]\]', unmask_fn, masked_body)
        
        if self.pub_cfg.get('append_credit', False):
            final_body += f"{self.pub_cfg.get('credit_text', '')}\n"
        
        merged_fm = fm_dict.copy()
        merged_fm['title'] = slug.replace('-', ' ').title() if is_target else title
        
        import_pattern = re.compile(r'^(import\s+.*?from\s+[\'"].*?[\'"];?)$', re.MULTILINE)
        imports = import_pattern.findall(final_body)
        if imports:
            final_body = import_pattern.sub('', final_body)
            final_body = '\n'.join(list(dict.fromkeys(imports))) + '\n\n' + final_body.lstrip()
            
        ordered_fm = {key: merged_fm.pop(key) for key in self.fm_order if key in merged_fm}
        ordered_fm.update(merged_fm)

        fm_str = "---\n" + yaml.dump(ordered_fm, allow_unicode=True, default_flow_style=False, sort_keys=False, width=float("inf")) + "---\n\n"

        if node_ext_assets is not None and assets_lock is not None:
            ext_md_pattern = re.compile(r'\!\[.*?\]\((https?://[^\)]+)\)')
            ext_html_pattern = re.compile(r'<img[^>]+src=["\'](https?://[^"\']+)["\']')
            with assets_lock:
                for match in ext_md_pattern.finditer(final_body): node_ext_assets.add(match.group(1))
                for match in ext_html_pattern.finditer(final_body): node_ext_assets.add(match.group(1))

        ext = os.path.splitext(rel_path)[1].lower()
        dest = os.path.join(self.paths['target_base'], lang_code, route_prefix, mapped_sub_dir, f"{slug}{ext}")
        
        if ext == '.mdx':
            src_abs_path = os.path.join(self.paths['vault'], rel_path)
            final_body = self.mdx_resolver.remap_imports(final_body, src_abs_path, dest)

        if not is_dry_run:
            try:
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                tmp_fd, tmp_path = tempfile.mkstemp(dir=os.path.dirname(dest), suffix=".tmp.md")
                with os.fdopen(tmp_fd, 'w', encoding='utf-8') as f: f.write(fm_str + final_body)
                os.replace(tmp_path, dest)
                
                if lang_code == self.i18n.get('source', {}).get('code', 'zh-cn'):
                    self.syndicator.syndicate(ordered_fm, final_body, f"/{lang_code}/{mapped_sub_dir}/{slug}".replace('//', '/'))
            except Exception as e:
                logger.error(f"🛑 写入失败: {e}")