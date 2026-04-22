#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Main Engine (Pipeline Driven)
模块职责：全局生命周期调度总线。
架构进化：引入 Context + Pipeline 模式，彻底消灭上帝函数。

🚀 [V16 终极重构 - 完整防退化版]：
1. 影子恢复 (Shadow Recovery)：如果源文件指纹未变，但前端产物丢失（如切换主题），
   引擎将直接从 .illacme-shadow 提取翻译资产进行秒级渲染，物理拦截 AI 调用。
2. 绝对防退化：完整保留了 588 行代码中的 MDX 穿梭、图片资产解蔽、多线程锁等所有工业级逻辑。
"""

import os
import time
import fnmatch
import logging
import threading
from datetime import datetime

# ==========================================
# 🛠️ 1. 核心工具与基建层 (Core Utilities & Infrastructure)
# 职责：提供纯函数计算、全域索引以及顶层分发能力
# ==========================================
from .config import load_config, Configuration, ThemeSettings
from .utils import normalize_keywords, extract_frontmatter
from .vault_indexer import VaultIndexer
from .ai_scheduler import AIScheduler
from .egress_dispatcher import EgressDispatcher

# ==========================================
# ⚙️ 2. 核心管线与生命周期层 (Pipeline & Execution Flow)
# 职责：承载文章从读取到落盘的链式处理流程
# ==========================================
from .pipeline.context import SyncContext
from .pipeline.runner import Pipeline
from .pipeline.staticizer import StaticizerStep
from .pipeline.steps import (
    ReadAndNormalizeStep, 
    ASTAndPurifyStep, 
    MetadataAndHashStep, 
    AISlugAndSEOStep, 
    ContextualImageAltStep,
    MaskingAndRoutingStep
)

# ==========================================
# 🔌 3. 适配器与协议层 (Adapters & Protocol Interfaces)
# 职责：抹平所有外部框架的方言差异（大模型、SSG框架、Obsidian语法）
# ==========================================
from .adapters.ingress import InputAdapter
from .adapters.egress import SSGAdapter
from .adapters.ast_resolver import TransclusionResolver, MDXResolver
from .adapters.ai_provider import TranslatorFactory
from .adapters.api_egress import WebhookBroadcaster
from .adapters.syndication import ContentSyndicator

# ==========================================
# 📦 4. 服务模块与状态管理层 (Services & State Management)
# 职责：掌管引擎的“记忆”与物理硬盘的“资产”
# ==========================================
from .storage.ledger import MetadataManager
from .storage.timeline import TimelineManager
from .storage.sentinel import SentinelManager
from .asset_pipeline import AssetPipeline
from .router import RouteManager
from .janitor import JanitorService

logger = logging.getLogger("Illacme.plenipes")

class IllacmeEngine:
    def __init__(self, config_path, no_ai=False):
        self.no_ai = no_ai
        # 🚀 [V32] 接入强类型配置枢纽
        self.config: Configuration = load_config(config_path)
        
        # 保持对旧逻辑引用的属性兼容
        self.sys_cfg = self.config.system
        self.sys_tuning = {
            "ai_translation": {
                "temperature": self.config.translation.temperature,
                "max_tokens": self.config.translation.max_tokens
            }
        }
        self.fm_defaults = self.config.frontmatter_defaults
        self.fm_order = self.config.frontmatter_order or ['title', 'description', 'keywords', 'author', 'date', 'tags', 'categories']
        
        # 🚀 [V32] 对齐系统调优参数
        self.max_workers = self.config.system.max_workers
        self.auto_save_interval = self.config.system.auto_save_interval
        self.max_depth = self.config.system.max_depth
        
        log_level_str = self.config.system.log_level.upper()
        logger.setLevel(getattr(logging, log_level_str, logging.INFO))
        
        self.vault_root = os.path.abspath(os.path.expanduser(self.config.vault_root))
        self.route_matrix = self.config.route_matrix
        self.active_theme = self.config.active_theme
        
        paths = self.config.output_paths
        target_base_dir = paths.get('markdown_dir')
        target_assets_dir = paths.get('assets_dir')
        target_graph_dir = paths.get('graph_json_dir')
        
        theme_settings = self.config.theme_options.get(self.active_theme, ThemeSettings())
        self.ssg_adapter = SSGAdapter(theme_settings, custom_adapters=self.config.framework_adapters)
        
        # 🔌 [V31 专家版]：方言处理策略初始化
        ingress_cfg = self.config.ingress_settings
        self.input_adapter = InputAdapter(
            active_dialects=ingress_cfg.active_dialects, 
            custom_rules=ingress_cfg.custom_sanitizers,
            hard_line_break=ingress_cfg.hard_line_break
        )
        
        self.paths = {
            "vault": self.vault_root,
            "target_base": os.path.abspath(os.path.expanduser(target_base_dir)) if target_base_dir else None,
            "assets": os.path.abspath(os.path.expanduser(target_assets_dir)) if target_assets_dir else None,
            "graph_json_dir": os.path.abspath(os.path.expanduser(target_graph_dir)) if target_graph_dir else None,
            "db": os.path.abspath(os.path.expanduser(self.config.metadata_db)),
            "shadow": os.path.join(self.vault_root, '.illacme-shadow')
        }
        
        self.i18n = self.config.i18n_settings
        self.seo_cfg = self.config.seo_settings
        self.img_cfg = self.config.image_settings
        self.pub_cfg = self.config.publish_control
        self.asset_base_url = self.img_cfg.base_url.rstrip('/') + '/'
        
        # 依赖注入
        self.meta = MetadataManager(self.paths["db"], self.auto_save_interval)
        
        # 🚀 [V34.5] 挂载审计时间轴 (Industrial Audit Timeline)
        self.timeline = TimelineManager(self.config)
        
        # 🛡️ [V34.6 Sentinel] 挂载健康哨兵 (Guardian Sentinel)
        self.sentinel = SentinelManager(self.config)
        
        self.translator = TranslatorFactory.create(self.config.translation)
        self.asset_pipeline = AssetPipeline(self.paths['assets'], self.img_cfg)
        self.route_manager = RouteManager(
            self.meta, self.translator, 
            lang_mapping=self.config.lang_mapping,
            default_lang=self.i18n.source.lang_code,
            active_theme=self.active_theme
        )
        
        # 🚀 [V16.4 重构] 呼叫独立扫描雷达
        self.md_index, self.asset_index = VaultIndexer.build_indexes(self.paths['vault'])
        
        self.transclusion_resolver = TransclusionResolver(self.md_index, self.asset_index, self.max_depth)
        self._processing_locks = {}
        self._global_engine_lock = threading.Lock()
        
        self.janitor = JanitorService(
            self._global_engine_lock, self._processing_locks, 
            self.paths, self.meta, self.route_manager, self.i18n, 
            sys_cfg=self.config.system, 
            active_theme=self.active_theme
        )
        self.mdx_resolver = MDXResolver(self.paths["vault"], self.paths["target_base"])
        self.broadcaster = WebhookBroadcaster(self.pub_cfg, sys_tuning_cfg=self.config.system)
        self.syndicator = ContentSyndicator(self.config.syndication, self.config.site_url, sys_tuning_cfg=self.config.system)

        # 🚀 [V16.4 重构] 挂载独立的物理出站分发器
        self.dispatcher = EgressDispatcher(
            paths=self.paths, meta=self.meta, route_manager=self.route_manager,
            asset_pipeline=self.asset_pipeline, ssg_adapter=self.ssg_adapter,
            mdx_resolver=self.mdx_resolver, syndicator=self.syndicator,
            broadcaster=self.broadcaster,
            pub_cfg=self.pub_cfg, 
            fm_order=self.fm_order,
            asset_base_url=self.asset_base_url,
            i18n_cfg=self.i18n,
            janitor=self.janitor
        )

    def _get_document_lock(self, rel_path):
        with self._global_engine_lock:
            if rel_path not in self._processing_locks:
                self._processing_locks[rel_path] = threading.Lock()
            return self._processing_locks[rel_path]

    def _is_excluded(self, rel_path):
        for p in self.pub_cfg.exclude_patterns:
            if fnmatch.fnmatch(rel_path, p) or fnmatch.fnmatch(os.path.basename(rel_path), p): return True
        return False

    def get_lang_name_by_code(self, code):
        """
        🚀 映射助手：根据语种代码获取对应的自然语言名称
        该方法直接对接 config.yaml 中的 i18n_settings，确保 AI 能够获得准确的翻译目标描述。
        """
        # 1. 检查是否为源语言代码 (例如 zh-cn -> 中文)
        src_cfg = self.i18n.source
        if src_cfg.lang_code == code:
            return src_cfg.name or 'Chinese'
        
        # 2. 在目标语言配置阵列中查找 (例如 en -> English)
        targets = self.i18n.targets
        for target in targets:
            if target.lang_code == code:
                # 优先返回配置中定义的 name，若无则返回 code 兜底
                return target.name or code
        
        # 3. 物理兜底：针对常见的标准代码进行硬核映射
        fallback_map = {
            'en': 'English',
            'zh-cn': 'Chinese',
            'ja': 'Japanese',
            'ko': 'Korean'
        }
        return fallback_map.get(code.lower(), code)

    def sync_document(self, src_path, route_prefix, route_source, is_dry_run=False, force_sync=False):
        """🚀 核心管线调度枢纽 (已接入 V16.1 统一寻址探针 / V16.4 架构极简版)"""
        rel_path = os.path.relpath(src_path, self.paths['vault']).replace('\\', '/')
        if self._is_excluded(rel_path): return

        doc_lock = self._get_document_lock(rel_path)
        if not doc_lock.acquire(blocking=False): return

        try:
            cli_force = force_sync  # 🚀 [V16 状态机修复] 提取并保护最真实的终端指令意图
            
            # 🚀 [架构升级 V15.2/V16.1]：目标端物理探针 (Target Physical Probe)
            if not force_sync and self.paths['target_base']:
                doc_info = self.meta.get_doc_info(rel_path)
                if doc_info and doc_info.get('source_hash') and doc_info.get('slug'):
                    slug = doc_info['slug']
                    target_files_missing = False
                    
                    t_abs = os.path.join(self.paths['vault'], rel_path)
                    t_sub_dir = os.path.dirname(os.path.relpath(t_abs, os.path.join(self.paths['vault'], route_source)).replace('\\', '/')).replace('\\', '/')
                    if t_sub_dir == '.': t_sub_dir = ""
                    mapped_sub_dir = self.route_manager.get_mapped_sub_dir(t_sub_dir, is_dry_run=is_dry_run, allow_ai=False)
                    ext = os.path.splitext(rel_path)[1].lower()
                    
                    langs_to_check = []
                    src_code = self.i18n.source.lang_code
                    if src_code: langs_to_check.append(src_code)
                    
                    if self.i18n.enabled:
                        for t in self.i18n.targets:
                            if t.lang_code: langs_to_check.append(t.lang_code)
                            
                    # 交叉比对硬盘物理文件
                    for code in langs_to_check:
                        expected_dest = self.route_manager.resolve_physical_path(
                            self.paths['target_base'], code, route_prefix, mapped_sub_dir, slug, ext
                        )
                        if not os.path.exists(expected_dest):
                            target_files_missing = True
                            logger.debug(f"🔍 [探针脱靶] 目标物理路径缺失: {expected_dest}")
                            break
                            
                    if target_files_missing:
                        logger.info(f"🩹 [状态机自愈] {rel_path}：检测到前端物理产物丢失，强行打破增量锁触发重建！")
                        force_sync = True

            # 1. 组装上下文与管线
            ctx = SyncContext(self, src_path, route_prefix, route_source, is_dry_run, force_sync)
            
            # 🚀 [V34.5] 记录审计起点
            self.timeline.log_event("SYNC", ctx.rel_path, "PENDING", "管线启动")

            pipeline = Pipeline()
            pipeline.add_step(ReadAndNormalizeStep()) \
                    .add_step(StaticizerStep()) \
                    .add_step(ASTAndPurifyStep()) \
                    .add_step(MetadataAndHashStep()) \
                    .add_step(AISlugAndSEOStep()) \
                    .add_step(ContextualImageAltStep()) \
                    .add_step(MaskingAndRoutingStep())

            # [V31.2] 动态熔断策略：如果全局开启了 --no-ai，强行将文章标记为静默编辑，拦截推理流程
            if self.no_ai:
                ctx.is_silent_edit = True
                ctx.ai_health_flag[0] = False

            # 2. 执行管线前置加工
            pipeline.execute(ctx)
            if ctx.is_aborted: 
                # 🚀 [V34.5 修复] 如果是显式标记的跳过（指纹匹配），返回 SKIP 码，确保统计精确
                if getattr(ctx, 'is_skipped', False):
                    return "SKIP"
                return "OFFLINE"

            # [V31.2] 再次加固：如果 --no-ai 开启，跳过多语言分派逻辑
            if self.no_ai:
                persistence_date = datetime.now().strftime("%Y-%m-%d")
                # 即使没有 AI，我们也需要写入主语种文件
                primary_shadow_hash, persistence_date = self.dispatcher.dispatch(self.asset_index, ctx.title, ctx.slug, ctx.masked_source, ctx.base_fm, rel_path, self.i18n.source.lang_code or 'zh', ctx.route_prefix, ctx.route_source, ctx.mapped_sub_dir, ctx.masks, ctx.is_dry_run, force_persistence_date=persistence_date)
            else:
                # 3. 后置阶段：SEO 注入闭包与分发
                def inject_seo(fm, lang_code, text_content):
                    seo_opts = self.config.seo_settings
                    if not seo_opts.enabled:
                        return fm
                        
                    lang_name = self.get_lang_name_by_code(lang_code)
                    seo_data, success = self.translator.generate_seo_metadata(text_content, lang_name, ctx.is_dry_run)
                    
                    if success and seo_data:
                        if seo_opts.generate_description:
                            fm['description'] = seo_data.get('description', '')
                        if seo_opts.generate_keywords:
                            fm['keywords'] = normalize_keywords(seo_data.get('keywords', ''))
                    return fm

                primary_shadow_hash = ""  # 🚀 初始化影子探针
                src_cfg = self.i18n.source

                if src_cfg:
                    src_code = src_cfg.lang_code or 'zh-cn'
                    
                    src_fm = ctx.base_fm.copy()
                    if ctx.seo_data:
                        src_fm.update(ctx.seo_data)
                        if 'keywords' in src_fm:
                            src_fm['keywords'] = normalize_keywords(src_fm['keywords'])
                    
                    # 🚀 [V16 影子探针]：主语种 SEO 物理自愈
                    doc_info = self.meta.get_doc_info(rel_path)
                    can_recover = (not cli_force and doc_info.get("source_hash") == ctx.current_hash and not ctx.is_silent_edit)
                    
                    ext = os.path.splitext(rel_path)[1].lower()
                    shadow_src_path = self.route_manager.resolve_physical_path(
                        self.paths['shadow'], src_code, route_prefix, ctx.mapped_sub_dir, ctx.slug, ext
                    )
                    
                    if can_recover and os.path.exists(shadow_src_path):
                        logger.debug(f"⚡️ [影子自愈] {rel_path} ({src_code}) 命中影子资产，跳过 AI SEO 提取。")
                        try:
                            with open(shadow_src_path, 'r', encoding='utf-8') as sf:
                                s_fm, _ = extract_frontmatter(sf.read())
                                src_fm.update({'description': s_fm.get('description', ''), 'keywords': s_fm.get('keywords', [])})
                                ctx.seo_data = {'description': s_fm.get('description', ''), 'keywords': s_fm.get('keywords', [])}
                        except Exception as e: logger.debug(f"影子读取失败: {e}")
                    elif not ctx.is_silent_edit:
                        src_fm = inject_seo(src_fm, src_code, ctx.body_content)
                        ctx.seo_data = {
                            'description': src_fm.get('description', ''),
                            'keywords': src_fm.get('keywords', '')
                        }

                    # --- 🚀 [V18.10 增强] 命中哈希增量逻辑判定 ---
                    # 如果指纹一致且物理位置在，且没有 cli_force，且影子存在，则判定为 SKIP
                    if can_recover and os.path.exists(shadow_src_path):
                        # 如果是强制同步或者是空载恢复，则继续，否则跳过
                        # 🚀 [V32.4 增强] 展示真实的目标物理路径，而非占位符
                        src_code = self.i18n.source.lang_code or 'zh'
                        display_dest = self.route_manager.resolve_physical_path(
                            self.paths['target_base'], src_code, route_prefix, ctx.mapped_sub_dir, ctx.slug, ext
                        )
                        rel_display_dest = os.path.relpath(display_dest, self.paths['target_base'])
                        logger.info(f"🔄 [同步跳过] {rel_path} -> {rel_display_dest} (指纹未变)")
                        # 🚀 [V34.5] 记录审计终点 (跳过)
                        self.timeline.update_event_status(rel_path, "SKIP", "内容未变，已拦截")
                        return "SKIP"
                    
                    # 🚀 物理派发主语种并锁定哈希与生日
                    primary_shadow_hash, persistence_date = self.dispatcher.dispatch(self.asset_index, ctx.title, ctx.slug, ctx.masked_source, src_fm, rel_path, src_code, ctx.route_prefix, ctx.route_source, ctx.mapped_sub_dir, ctx.masks, ctx.is_dry_run, node_assets=ctx.node_assets, node_ext_assets=ctx.node_ext_assets, node_outlinks=ctx.node_outlinks, assets_lock=ctx.assets_lock)

                # 🚀 [V16.4 重构] 呼叫独立的多语言 AI 并发调度中枢 (透传 V27 锁定的持久化日期)
                AIScheduler.dispatch_targets(self, ctx, inject_seo, route_prefix, route_source, cli_force, rel_path, is_dry_run, persistence_date=persistence_date)

            # 4. 终态记录与广播
            if not ctx.is_dry_run:
                final_assets, final_ext_assets = list(ctx.node_assets), list(ctx.node_ext_assets)
                elapsed = time.perf_counter() - ctx.node_start_perf
                persist_hash = ctx.current_hash if ctx.ai_health_flag[0] else ""
                
                self.meta.register_document(
                    ctx.rel_path, 
                    ctx.title, 
                    slug=ctx.slug, 
                    source_hash=persist_hash, 
                    shadow_hash=primary_shadow_hash, 
                    seo_data=ctx.seo_data, 
                    route_prefix=ctx.route_prefix, 
                    route_source=ctx.route_source, 
                    assets=final_assets, 
                    ext_assets=final_ext_assets,
                    outlinks=list(ctx.node_outlinks),
                    persistent_date=persistence_date
                )
                self.meta.save()

                if ctx.is_silent_edit: 
                    logger.info(f"✨ [静默直传成功] {ctx.rel_path} | ⏱️ 耗时: {elapsed:.2f} 秒")
                    self.timeline.update_event_status(ctx.rel_path, "UPDATED", "记录指纹 (静默模式)")
                elif ctx.ai_health_flag[0]:
                    logger.info(f"✨ [同步成功] {ctx.rel_path} | 📦 资产: {len(final_assets)} | ⚡️ 耗时: {elapsed:.2f} 秒")
                    self.timeline.update_event_status(ctx.rel_path, "UPDATED", f"资产: {len(final_assets)}")
                    self.broadcaster.broadcast(ctx.title, ctx.rel_path, src_cfg.lang_code or 'zh-cn', ctx.mapped_sub_dir, ctx.slug)
                else: 
                    logger.warning(f"🚧 [局部降级] {ctx.rel_path} 部分 AI 任务不完整，已拦截指纹缓存。")
                    self.timeline.update_event_status(ctx.rel_path, "DEGRADED", "部分 AI 任务失败")
                    return "DEGRADED"

            return "UPDATED"

        except Exception as e:
            self.timeline.update_event_status(rel_path, "ERROR", str(e))
            logger.error(f"❌ 文章处理发生错误 {rel_path}: {e}")
            return "ERROR"
        finally:
            doc_lock.release()