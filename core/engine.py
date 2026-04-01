#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Main Engine
模块职责：全局生命周期调度总线。像乐高积木一样，将状态机、语法降维器、AI管线、资产管线组装起来，执行核心流转。
架构原则：严格执行 SEO 权重排序，配置层智能过滤空值注入，击穿 PyYAML 自动折行限制。
2026 迭代升级：
1. [Asset Tracking] 引入全格式资产追踪（图片、PDF、ZIP 等）。
2. [Safety Fuse] 引入物理瘦身保险丝，防止账本未就绪时误删。
3. [Zero-Thinning] 严格保留原始工程的所有微观监控逻辑。
4. [AI Lock Valve] 引入 `ai_sync: false` 静默编辑锁，针对错别字微调场景彻底斩断 Token 浪费。
"""

import os
import re
import time
import yaml
import hashlib
import fnmatch
import logging
import urllib.parse
import threading
import concurrent.futures

# 全量导入解耦模块，构建完整护盾
from .utils import normalize_keywords, extract_frontmatter
from .parser import SSGAdapter, TransclusionResolver
from .state_machine import MetadataManager
from .ai_pipeline import TranslatorFactory
from .asset_pipeline import AssetPipeline

logger = logging.getLogger("Illacme.plenipes")

class IllacmeEngine:
    def __init__(self, config_path):
        with open(os.path.abspath(os.path.expanduser(config_path)), 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.sys_cfg = self.config.get('system', {})
        self.fm_defaults = self.config.get('frontmatter_defaults') or {}
        self.max_workers = self.sys_cfg.get('max_workers', 5)
        
        # 🚀 抽取系统底层防线参数
        self.auto_save_interval = self.sys_cfg.get('auto_save_interval', 2.0)
        self.max_depth = self.sys_cfg.get('max_depth', 3)
        
        # 🚀 抽取 SEO 前台视图排序规则
        default_order = ['title', 'description', 'keywords', 'author', 'date', 'tags', 'categories']
        self.fm_order = self.config.get('frontmatter_order', default_order)
        
        log_level_str = self.sys_cfg.get('log_level', 'INFO').upper()
        logger.setLevel(getattr(logging, log_level_str, logging.INFO))
        
        self.vault_root = os.path.abspath(os.path.expanduser(self.config.get('vault_root', '')))
        self.route_matrix = self.config.get('route_matrix', [])
        
        framework_cfg = self.config.get('framework', {})
        engine_name = framework_cfg.get('engine', 'starlight')
        self.ssg_adapter = SSGAdapter(engine_name)
        
        frontend_target = self.config.get('frontend_dir') or self.config.get('starlight_dir', '')
        frontend_dir = os.path.abspath(os.path.expanduser(frontend_target))
        
        content_dir = framework_cfg.get('content_dir', 'src/content/docs')
        asset_dir = framework_cfg.get('asset_dir', 'public/assets')
        
        self.paths = {
            "vault": self.vault_root,
            "target_base": os.path.join(frontend_dir, content_dir),
            "assets": os.path.join(frontend_dir, asset_dir),
            "db": os.path.abspath(os.path.expanduser(self.config.get('metadata_db', './plenipes_metadata.json')))
        }
        
        self.i18n = self.config.get('i18n_settings', {})
        self.seo_cfg = self.config.get('seo_settings', {})
        self.img_cfg = self.config.get('image_settings', {})
        self.pub_cfg = self.config.get('publish_control', {})
        
        self.asset_base_url = self.img_cfg.get('base_url', '/assets/').rstrip('/') + '/'
        
        # 挂载内部解耦模块，动态注入底层参数
        self.meta = MetadataManager(self.paths["db"], self.auto_save_interval)
        self.translator = TranslatorFactory(self.config)
        self.asset_pipeline = AssetPipeline(self.paths['assets'], self.img_cfg)
        self.asset_index = {}
        self.md_index = {}
        
        # 建立全局双链寻址倒排索引
        self._build_indexes()
        
        # 注入防死循环的动态嵌套深度
        self.transclusion_resolver = TransclusionResolver(self.md_index, self.asset_index, self.max_depth)
        
        # 🚀 [v13.6.3 升级] 注入全局文件处理互斥锁字典，彻底封堵高频重入漏洞
        self._processing_locks = {}
        self._global_engine_lock = threading.Lock()

    def _get_document_lock(self, rel_path):
        """获取极细粒度的文件级互斥锁"""
        with self._global_engine_lock:
            if rel_path not in self._processing_locks:
                self._processing_locks[rel_path] = threading.Lock()
            return self._processing_locks[rel_path]

    # ==========================================
    # 🚀 目录架构引擎：多维度中英文隔离桥接器
    # ==========================================
    def _get_mapped_sub_dir(self, raw_sub_dir, is_dry_run=False, allow_ai=False):
        """
        🚀 目录结构状态机：将包含中文的源目录物理路径，极度安全地翻译并固化为纯英文 URL 路径。
        一旦确立，终身不变，彻底解决跨平台部署时的中文 URL 编码雪崩灾难。
        """
        if not raw_sub_dir or raw_sub_dir == '.': return ""
        parts = raw_sub_dir.split('/')
        mapped_parts = []
        
        for p in parts:
            if not p: continue
            
            # 1. 尝试从内存账本读取极速映射
            d_slug = self.meta.get_dir_slug(p)
            
            # 2. 缓存击穿，触发全新目录创建流程
            if not d_slug:
                if allow_ai and not is_dry_run:
                    logger.info(f"   └── ⏳ 探测到全新中文目录 '{p}'，正调度 AI 为其生成永久英文 URL 路由...")
                    d_slug, _ = self.translator.generate_slug(f"Directory Name: {p}", is_dry_run)
                
                # 3. 终极无缝兜底：彻底脱离 AI 和网络环境的防撞设计
                if not d_slug:
                    safe_p = re.sub(r'[^\w\-]', '', p.replace(' ', '-')).lower()
                    safe_p = re.sub(r'-+', '-', safe_p).strip('-')
                    # 如果剔除中文后变为空（纯中文目录），采用安全的 dir- 前缀加轻量哈希
                    d_slug = safe_p if safe_p else f"dir-{hashlib.md5(p.encode('utf-8')).hexdigest()[:6]}"
                
                # 4. 回写状态机，固化此分支历史
                self.meta.register_dir_slug(p, d_slug)
                
            mapped_parts.append(d_slug)
            
        return '/'.join(mapped_parts)

    def _build_indexes(self):
        for root, dirs, files in os.walk(self.paths['vault']):
            # 斩断隐藏目录遍历，极致加速并防止系统文件污染
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for f in files:
                if f.startswith("."): continue 
                abs_path = os.path.join(root, f)
                if f.endswith(".md"):
                    self.md_index[f] = abs_path
                    self.md_index[os.path.splitext(f)[0]] = abs_path
                else:
                    # 🚀 [架构进化] 从强行覆盖改为列表聚合，接纳所有同名异径资产
                    if f not in self.asset_index:
                        self.asset_index[f] = []
                    self.asset_index[f].append(abs_path)

    def _is_excluded(self, rel_path):
        patterns = self.pub_cfg.get('exclude_patterns', [])
        for p in patterns:
            if fnmatch.fnmatch(rel_path, p) or fnmatch.fnmatch(os.path.basename(rel_path), p): 
                return True
        return False

    def gc_assets(self, current_source_files=None, is_dry_run=False):
        """
        物理瘦身逻辑：
        系统会检查所有的文章，统计出哪些图片、PDF、附件还在被使用。
        那些“落单”的、不再被任何文章引用的资产将被物理删除，保持前端目录整洁。
        带全局写保护屏障的物理资产清算器。
        """
        # 🚀 [防退化验证]: 探针检查是否有任何文件正在被 AI 管线处理
        # 任何被持有的文件锁都代表系统中存在尚未入账的“飞行中 (in-flight)”资产
        in_flight = any(l.locked() for l in self._processing_locks.values())
        if in_flight:
            logger.warning("🚧 [GC 熔断] 检测到有文章正在处理中，为防止误删生成中的新生资产，已强行熔断本次物理清理泵。")
            return

        # 获取屏障锁，确保清算期间不会有新任务开始写入
        with self._global_engine_lock:
            logger.info("🧹 启动前端资产目录“大扫除” (gc_assets)...")
            active_assets = set()
            
            docs = self.meta.data.get("documents", {})
            total_docs = len(docs)
            
            # 🛡️ [物理瘦身保险丝]：基于全量基线信任验证
            # 如果没有传入 current_source_files（例如非全量上下文被意外调用），必须拦截以防误删
            if current_source_files is None and total_docs > 0:
                logger.warning("🚧 资产账本未接收到全量物理扫描基线，为了保护您的附件不被误删，已自动跳过本次清理。")
                logger.warning("💡 请等待全量同步完成后，自动激活资产回收泵。")
                return
            
            # 从账本中收集所有文章正在使用的“资产免死金牌”
            for doc in docs.values():
                # 🚀 稀疏字典安全读取：摒弃 if "assets" in doc，直接 get，兼容空载与稀疏存储
                assets = doc.get("assets", [])
                if isinstance(assets, list):
                    active_assets.update(assets)
            
            if not os.path.exists(self.paths['assets']): return

            for root, _, files in os.walk(self.paths['assets']):
                for f in files:
                    if f.startswith('.'): continue # 忽略系统文件
                    
                    # 🚀 架构升维：计算出每一个物理文件相对于 public/assets 根目录的深层相对路径
                    # 比如：3f/logo_a1b9c.webp
                    f_abs = os.path.join(root, f)
                    f_rel = os.path.relpath(f_abs, self.paths['assets']).replace('\\', '/')
                    
                    # 使用深层相对路径与账本进行绝对对齐核对
                    if f_rel not in active_assets:
                        if is_dry_run:
                            logger.info(f"    [模拟清理] 发现孤儿资产: {f_rel}")
                        else:
                            try:
                                os.remove(f_abs)
                                logger.info(f"    [清理成功] 物理移除冗余资产: {f_rel}")
                            except Exception as e:
                                logger.error(f"    [清理失败] 无法删除文件 {f_rel}: {e}")

    def gc_node(self, rel_path, route_prefix, route_source, is_dry_run=False):
        doc_info = self.meta.get_doc_info(rel_path)
        slug = doc_info.get("slug")
        prefix = doc_info.get("prefix", route_prefix)
        source = doc_info.get("source", route_source)
        
        if slug:
            t_abs = os.path.join(self.paths['vault'], rel_path)
            t_src_abs = os.path.join(self.paths['vault'], source)
            t_sub_rel = os.path.relpath(t_abs, t_src_abs).replace('\\', '/')
            t_sub_dir = os.path.dirname(t_sub_rel).replace('\\', '/')
            if t_sub_dir == '.': t_sub_dir = ""

            # 🚀 查询英文目录映射状态，保障物理删除路径绝对精确
            mapped_sub_dir = self._get_mapped_sub_dir(t_sub_dir, is_dry_run, allow_ai=False)

            langs = [self.i18n.get('source', {}).get('code')] + [t['code'] for t in self.i18n.get('targets', [])]
            for code in filter(None, langs):
                dest = os.path.join(self.paths['target_base'], code, prefix, mapped_sub_dir, f"{slug}.md")
                if os.path.exists(dest):
                    if is_dry_run: 
                        logger.info(f"    [Dry-Run 模拟回收] 拟删除文章文件: {dest}")
                    else: 
                        try: os.remove(dest)
                        except Exception as e: logger.error(f"回收文章文件失败 {dest}: {e}")
                            
        if not is_dry_run: self.meta.remove_document(rel_path)

    def gc_orphans(self, current_source_files, is_dry_run=False):
        to_delete = [p for p in list(self.meta.data["documents"].keys()) if p not in current_source_files]
        for rel_path in to_delete:
            if not is_dry_run: logger.info(f"  └── [文件清理] 自动移除已删除的文章: {rel_path}")
            prefix = self.meta.get_doc_info(rel_path).get("prefix", "")
            source = self.meta.get_doc_info(rel_path).get("source", "")
            self.gc_node(rel_path, prefix, source, is_dry_run)
        
        # 🚀 [联动清理] 将全量基线 current_source_files 穿透传递，解锁物理大扫除
        self.gc_assets(current_source_files, is_dry_run)

    def gc_ghost_nodes(self, is_dry_run=False):
        """
        🚀 幽灵路由清道夫 (Ghost Route Sweeper)
        全盘扫描前端文章输出目录，与底层 JSON 账本进行绝对对齐。
        任何没有被登记在册的 .md 文件（例如历史 Bug 遗留的乱码文件），将被无情地物理抹杀。
        """
        # 🚀 [防退化验证]: 探针检查是否有任何文件正在被 AI 管线处理
        in_flight = any(l.locked() for l in self._processing_locks.values())
        if in_flight:
            logger.warning("🚧 [路由清洗熔断] 检测到有文章正在生成中，为防止误删写入一半的新文章，已强行熔断本次路由清洗。")
            return

        with self._global_engine_lock:
            logger.info("🧹 启动前端路由目录“幽灵清洗” (gc_ghost_nodes)...")
            
            valid_dest_paths = set()
            docs = self.meta.data.get("documents", {})
            langs = [self.i18n.get('source', {}).get('code')] + [t.get('code') for t in self.i18n.get('targets', []) if t.get('code')]
            
            # 1. 遍历内存账本，重构出当前系统认可的、所有合法的绝对路径清单
            for rel_path, doc in docs.items():
                slug = doc.get("slug")
                if not slug: continue
                
                prefix = doc.get("prefix", "")
                source = doc.get("source", "")
                
                t_abs = os.path.join(self.paths['vault'], rel_path)
                t_src_abs = os.path.join(self.paths['vault'], source)
                t_sub_rel = os.path.relpath(t_abs, t_src_abs).replace('\\', '/')
                t_sub_dir = os.path.dirname(t_sub_rel).replace('\\', '/')
                if t_sub_dir == '.': t_sub_dir = ""
                
                # 🚀 提取其在前端真实物理落地的合法英文路由目录
                mapped_sub_dir = self._get_mapped_sub_dir(t_sub_dir, is_dry_run=is_dry_run, allow_ai=False)
                
                for code in filter(None, langs):
                    dest = os.path.abspath(os.path.join(self.paths['target_base'], code, prefix, mapped_sub_dir, f"{slug}.md"))
                    valid_dest_paths.add(dest)
                    
            # 2. 划定受控的扫描根目录范围
            # 仅扫描配置了的多语言子目录 (如 zh-cn, en)，极度安全地避开 Astro 原生的根目录文件 (如 index.mdx)
            controlled_roots = [os.path.abspath(os.path.join(self.paths['target_base'], code)) for code in filter(None, langs)]
            
            deleted_count = 0
            for scan_root in controlled_roots:
                if not os.path.exists(scan_root): continue
                
                for root, _, files in os.walk(scan_root):
                    for f in files:
                        if f.endswith('.md'):
                            f_abs = os.path.abspath(os.path.join(root, f))
                            
                            # 🚀 终极审判：如果物理硬盘上存在，但合法清单里没有，杀！
                            if f_abs not in valid_dest_paths:
                                if is_dry_run:
                                    logger.info(f"    [Dry-Run 模拟清洗] 拟删除幽灵路由文件: {f_abs}")
                                else:
                                    try:
                                        os.remove(f_abs)
                                        logger.info(f"    [路由清洗] 物理移除未受控的幽灵文章: {f_abs}")
                                        deleted_count += 1
                                    except Exception as e:
                                        logger.error(f"    [清洗失败] 无法删除幽灵文件 {f_abs}: {e}")
                                        
            if deleted_count > 0:
                logger.info(f"✨ 幽灵清洗完成，共斩断了 {deleted_count} 个脱离管线的野路由。")
            else:
                logger.info("✨ 路由健康度 100%，未发现任何幽灵文件。")

    def sync_document(self, src_path, route_prefix, route_source, is_dry_run=False, force_sync=False):
        """支持注入 route_prefix 的核心单文件全维度流转调度管线"""
        title = os.path.splitext(os.path.basename(src_path))[0]
        rel_path = os.path.relpath(src_path, self.paths['vault']).replace('\\', '/')
        
        if self._is_excluded(rel_path): return

        # 🚀 [防退化验证]：获取该文件的细粒度锁。
        # 使用非阻塞模式 (blocking=False)。如果拿不到锁，说明之前的 AI 翻译还没跑完，
        # 直接静默抛弃本次因高频按 Ctrl+S 触发的重入事件！
        doc_lock = self._get_document_lock(rel_path)
        if not doc_lock.acquire(blocking=False):
            logger.warning(f"🚧 拦截高频重入: {rel_path} 正处于 AI 翻译网络阻塞中，已拦截并丢弃本次频繁保存。")
            return

        try:
            try:
                with open(src_path, 'r', encoding='utf-8') as f: content = f.read()
            except FileNotFoundError:
                # 优雅降级：这通常是因为重命名或移动导致的旧路径残影，直接静默 return 交给 GC 处理
                return
            except IOError as e: 
                logger.error(f"🛑 读取失败: 无法读取文章 {src_path}，请检查文件权限或是否损坏: {e}")
                return
    
            fm_dict, raw_body = extract_frontmatter(content)
            
            # 🚀 [状态机强坍缩]：彻底解决 Python dict.get() 的 NoneType 穿透问题
            raw_ai_sync = fm_dict.get('ai_sync')
            if raw_ai_sync is None:
                # 针对留空现象，强行坍缩为默认放行态
                ai_sync_str = 'true'
            else:
                ai_sync_str = str(raw_ai_sync).lower()
                
            is_silent_edit = (ai_sync_str == 'false')
            
            # 🚀 逻辑升级：实质性内容探针（The Substance Probe）
            # 利用配置文件中的 empty_content_threshold 进行拦截，防止空载或极短占位符同步到前端
            substance_threshold = self.translator.empty_threshold # 借用 AI 管线中已初始化的阈值
            if len(raw_body.strip()) < substance_threshold:
                # 深度清理：如果该文件之前在前端生成过，现在内容被删至阈值以下，则执行物理下线
                if self.meta.get_doc_info(rel_path):
                    logger.info(f"🍃 拦截空载文章: {rel_path} 正文内容过短 (小于 {substance_threshold} 字)，已自动从前端移除。")
                    self.gc_node(rel_path, route_prefix, route_source, is_dry_run)
                return
    
            # 拦截墙：草稿（Draft）全语种强行下线
            if str(fm_dict.get('draft')).lower() == 'true' or str(fm_dict.get('publish')).lower() == 'false':
                if self.meta.get_doc_info(rel_path):
                    logger.info(f"🛑 拦截生效: {rel_path} (已设为草稿或下线，自动从前端移除)")
                    self.gc_node(rel_path, route_prefix, route_source, is_dry_run)
                return
    
            defaults = self.fm_defaults or {}
            base_fm = {k: v for k, v in defaults.items() if v is not None and str(v).strip() != ""}
            base_fm.update(fm_dict)
    
            if 'keywords' in base_fm:
                base_fm['keywords'] = normalize_keywords(base_fm['keywords'])
    
            # 预编译层加工：处理潜入文档与方言高亮语法
            body_content = self.transclusion_resolver.expand(raw_body)
            body_content = self.ssg_adapter.convert_callouts(body_content)
            
            if 'slug' in base_fm: del base_fm['slug']
    
            # 指纹核验中心：增量拦截
            current_hash = hashlib.md5((str(base_fm) + body_content).encode('utf-8')).hexdigest()
            self.meta.register_document(rel_path, title)
            doc_info = self.meta.get_doc_info(rel_path)
    
            # 🚀 [终极自愈前置]：如果 JSON 账本里依然残留着带 % 的毒化 Slug，必须强制击穿防抖缓存！
            is_toxic_slug = '%' in str(doc_info.get("slug", ""))
    
            if not force_sync and not is_toxic_slug and doc_info.get("hash") == current_hash: 
                return
    
            # 🚀 [微观时钟探针 - 起点] 节点真正进入 CPU/IO 密集型加工管线
            node_start_perf = time.perf_counter()
    
            prefix_log = "[Dry-Run 演练]" if is_dry_run else "[创作同步]"
            if is_silent_edit:
                logger.info(f"🤫 [静默微调] {rel_path} 已开启 ai_sync: false 锁，正在物理直传排版，切断外部通信...")
            else:
                logger.info(f"{prefix_log} 正在加工文章: {rel_path} (路由分类: /{route_prefix})")
            
            ai_health_flag = [True]
            
            slug_raw = doc_info.get("slug")
            
            # 🚀 [自愈防线] 侦测并摧毁上一代架构遗留的 URL 编码毒化缓存
            # Astro/Starlight 的底层 slugger 会把 % 视为非法字符并强行剔除，导致出现 e6b58b... 这种纯 Hex 乱码。
            # 一旦发现历史缓存被毒化，立刻强行熔断并交由下方的全新生成管线重构！
            if slug_raw and '%' in slug_raw:
                logger.warning(f"💊 [自愈机制] 拦截到历史遗留的毒化路径缓存 ({slug_raw})，已强行撕碎并移交重构！")
                slug_raw = None
            
            if not slug_raw:
                # 🚀 若用户首次建文就挂上了锁，强制采用安全本地转化兜底
                if not is_silent_edit:
                    slug_raw, slug_success = self.translator.generate_slug(title, is_dry_run)
                    if not slug_success:
                        logger.warning(f"⚠️ 文章 {rel_path} 的英文链接生成失败！已使用本地编码兜底。")
                        ai_health_flag[0] = False
                else:
                    # 🚀 废弃 urllib.parse.quote，改用全域安全正则，支持原生中文物理路径
                    fallback = re.sub(r'[^\w\u4e00-\u9fa5\-]', '', title.replace(' ', '-')).lower()
                    slug_raw = re.sub(r'-+', '-', fallback).strip('-')
                slug = slug_raw
            else:
                slug = slug_raw
            
            seo_data = doc_info.get("seo", {})
            if 'description' in seo_data or 'keywords' in seo_data: seo_data = {} 
    
            # 架构升级：注入线程锁，防止并发写时共享字典污染
            seo_lock = threading.Lock()
    
            def inject_seo(fm, lang_code, text_content):
                # 🚀 静默锁定下，完全跳过 SEO 提取开销
                if self.seo_cfg.get('enabled', False) and not is_silent_edit:
                    with seo_lock:
                        needs_generate = lang_code not in seo_data
                        
                    if needs_generate:
                        new_seo, seo_success = self.translator.generate_seo_metadata(text_content, is_dry_run)
                        if not seo_success:
                            logger.warning(f"⚠️ [SEO 提取失败] 文章 {rel_path} ({lang_code}) 的摘要/关键词生成失败，将保持原样。")
                            ai_health_flag[0] = False
                        with seo_lock:
                            seo_data[lang_code] = new_seo
                            
                    with seo_lock:
                        lang_seo = seo_data.get(lang_code, {})
                        
                    desc_raw = lang_seo.get('description') or lang_seo.get('Description') or lang_seo.get('summary')
                    if self.seo_cfg.get('generate_description', False) and desc_raw and 'description' not in fm:
                        fm['description'] = str(desc_raw).strip()
                        
                    kw_raw = lang_seo.get('keywords') or lang_seo.get('keyword') or lang_seo.get('Keywords') or lang_seo.get('tags')
                    if self.seo_cfg.get('generate_keywords', False) and kw_raw and 'keywords' not in fm:
                        fm['keywords'] = normalize_keywords(kw_raw)
                return fm
    
            # ==========================================
            # 🚀 [资产清单记账员 - node_assets]
            # ==========================================
            node_assets = set()
            assets_lock = threading.Lock()
    
            # ==========================================
            # STB_MASK 脱敏物理护盾 (Format Protection Shield)
            # ==========================================
            masks = []
            def mask_fn(m):
                masks.append(m.group(0))
                return f"[[STB_MASK_{len(masks)-1}]]"
                
            mask_pattern = r'\!\[\[[^\]]+\]\]|\[\[[^\]]+\]\]|\!\[[^\]]*\]\([^)]+\)|\[[^\]]*\]\([^)]+\)|\\[!"#$%&\'()*+,\-./:;<=>?@[\\\]^_`{|}~]'
            masked_source = re.sub(mask_pattern, mask_fn, body_content)
    
            # 剥离 source 前缀，获取真实落盘子目录
            abs_src_dir = os.path.join(self.paths['vault'], route_source)
            sub_rel_path = os.path.relpath(src_path, abs_src_dir).replace('\\', '/')
            sub_dir = os.path.dirname(sub_rel_path).replace('\\', '/')
            if sub_dir == '.': sub_dir = ""
    
            # 🚀 破防杀招：在将路由投递给前后端管线前，强制将中文物理路径转化为安全的英文 URL 路由路径！
            mapped_sub_dir = self._get_mapped_sub_dir(sub_dir, is_dry_run=is_dry_run, allow_ai=not is_silent_edit)
    
            # 6. 源语言路由投递 (保持主线程同步执行作为安全基线)
            src_cfg = self.i18n.get('source', {})
            if src_cfg:
                src_code = src_cfg.get('code', 'zh-cn')
                src_fm = inject_seo(base_fm.copy(), src_code, body_content)
                # 🚀 替换为 mapped_sub_dir 进行底层落盘分发
                self._dispatch_output(title, slug, masked_source, src_fm, rel_path, src_code, route_prefix, route_source, mapped_sub_dir, masks, is_dry_run, node_assets=node_assets, assets_lock=assets_lock)
    
            # 7. 目标语言矩阵切分翻译并发路由 (引入 ThreadPoolExecutor 彻底解放 I/O 瓶颈)
            targets = self.i18n.get('targets', [])
            # 🚀 在静默模式下，彻底斩断对目标语言的分发通道，从而保留磁盘上原有的旧翻译物理文件。
            if targets and not is_silent_edit:
                def process_target(target):
                    code = target.get('code')
                    if not code: return None
                    
                    final_body = masked_source
                    target_health = True
                    
                    if target.get('translate_body', False):
                        ai_res, trans_success = self.translator.translate_body(masked_source, target.get('prompt_lang', code), is_dry_run)
                        if ai_res: final_body = ai_res
                        if not trans_success:
                            logger.warning(f"⚠️ [翻译失败] 文章 {rel_path} 转换为目标语言 ({code}) 失败！已为您保留原文。")
                            target_health = False
                    
                    target_fm = inject_seo(base_fm.copy(), code, final_body)
                    return (code, final_body, target_fm, target_health)
    
                with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                    future_to_code = {executor.submit(process_target, t): t for t in targets if t.get('code')}
                    for future in concurrent.futures.as_completed(future_to_code):
                        try:
                            res = future.result()
                            if res:
                                t_code, t_body, t_fm, t_health = res
                                if not t_health: ai_health_flag[0] = False
                                # 🚀 替换为 mapped_sub_dir 进行底层落盘分发
                                self._dispatch_output(title, slug, t_body, t_fm, rel_path, t_code, route_prefix, route_source, mapped_sub_dir, masks, is_dry_run, is_target=True, node_assets=node_assets, assets_lock=assets_lock)
                        except Exception as exc:
                            logger.error(f"🛑 [系统异常] 多语言处理引擎崩溃 (文章: {rel_path}): {exc}")
                            ai_health_flag[0] = False
            
            # 8. 更新状态机防抖快照
            if not is_dry_run:
                # 🚀 固化资产指纹：记录引用的所有附件（图片、PDF等）
                final_assets = list(node_assets)
                
                if is_silent_edit:
                    # 🚀 架构级修正：抛弃之前“强行冻结旧 MD5”的过度设计。
                    # 直接写入当前最新计算出的真实 Hash。当用户后续删掉 `ai_sync: false` 时，
                    # YAML 属性区的变动本身就会自然触发 Hash 失配，从而完美唤醒全量重译，
                    # 彻底根除了因 Hash 永远失配导致的 Watchdog 无限循环同步 Bug。
                    self.meta.register_document(rel_path, title, slug=slug, file_hash=current_hash, seo_data=seo_data, route_prefix=route_prefix, route_source=route_source, assets=final_assets)
                    
                    node_elapsed = time.perf_counter() - node_start_perf
                    logger.info(f"✨ [静默直传成功] 本地排版已就绪: {rel_path} (翻译与SEO已跳过) | ⚡️ 耗时: {node_elapsed:.2f} 秒")
                    
                elif ai_health_flag[0]:
                    self.meta.register_document(rel_path, title, slug=slug, file_hash=current_hash, seo_data=seo_data, route_prefix=route_prefix, route_source=route_source, assets=final_assets)
                    
                    # 🚀 [微观时钟探针 - 终点] 结算单点无损耗时
                    node_elapsed = time.perf_counter() - node_start_perf
                    logger.info(f"✨ [同步成功] 文章已就绪并记录指纹: {rel_path} | 📦 关联资产数: {len(final_assets)} | ⚡️ 耗时: {node_elapsed:.2f} 秒")
                else:
                    self.meta.register_document(rel_path, title, slug=slug, file_hash="", seo_data=seo_data, route_prefix=route_prefix, route_source=route_source, assets=final_assets)
                    
                    # 🚀 故障节点同样捕获耗时，用于追溯模型卡死时长
                    node_elapsed = time.perf_counter() - node_start_perf
                    logger.warning(f"🚧 [局部重试] 文章 {rel_path} 的部分 AI 任务未完成。已拦截缓存，下次启动将自动重试补全！| ⏱️ 耗时: {node_elapsed:.2f} 秒")

        finally:
            # 🚀 无论业务流成功、报错还是被拦截，最终必须释放当前文件的独立锁，防止永久死锁
            doc_lock.release()

    def _dispatch_output(self, title, slug, masked_body, fm_dict, rel_path, lang_code, route_prefix, route_source, mapped_sub_dir, masks, is_dry_run, is_target=False, node_assets=None, assets_lock=None):
        """核心组装中枢：执行防篡改反脱敏恢复、双链转化适配与跨维度的最终物理落盘"""
        if not self.paths['target_base']: return
        
        prefix_part = f"/{route_prefix}" if route_prefix else ""
        
        # 🚀 [专家算子] Obsidian 原生就近寻址算法
        def _get_closest_asset(target_filename):
            candidates = self.asset_index.get(target_filename, [])
            if not candidates: 
                return None
            if len(candidates) == 1: 
                return candidates[0]
            
            # 若存在多个同名文件，计算它们与当前编译文章的相对物理距离
            current_abs_dir = os.path.dirname(os.path.join(self.paths['vault'], rel_path))
            
            # 以公共前缀的长度作为亲缘度得分（得分越高，目录树上离得越近）
            candidates_sorted = sorted(
                candidates, 
                key=lambda p: len(os.path.commonprefix([current_abs_dir, os.path.dirname(p)])), 
                reverse=True
            )
            return candidates_sorted[0]
        
        def unmask_fn(m):
            idx = int(re.search(r'\d+', m.group(0)).group())
            orig = masks[idx]
            if orig.startswith('\\'): return orig 
            
            def log_asset(p_name):
                if node_assets is not None and assets_lock is not None:
                    with assets_lock: node_assets.add(p_name)
                return p_name

            # Obsidian 格式双链图片 ![[img]]
            if orig.startswith('![['):
                filename = orig[3:-2].split('|')[0].strip()
                alt_text = orig[3:-2].split('|')[1] if '|' in orig[3:-2] else filename
                target_asset_path = _get_closest_asset(filename) # 🚀 呼叫就近寻址
                if target_asset_path:
                    processed_name = log_asset(self.asset_pipeline.process(target_asset_path, filename, is_dry_run))
                    ext = os.path.splitext(processed_name)[1].lower()
                    if ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.tiff', '.svg']:
                        return f"![{alt_text}]({self.asset_base_url}{processed_name})"
                    else: 
                        return f"[{alt_text}]({self.asset_base_url}{processed_name})"
                return orig
                
            # 原生标准图片 ![alt](img)
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
                
            # Obsidian 格式纯文本双链 [[link]]
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
                    t_slug = t_doc_info.get("slug") or self.translator.generate_slug(target_text, is_dry_run)[0]
                    t_prefix = t_doc_info.get("prefix", route_prefix) 
                    t_source = t_doc_info.get("source", route_source)
                    
                    if not is_dry_run: 
                        self.meta.register_document(target_rel_path, target_text, slug=t_slug, route_prefix=t_prefix, route_source=t_source)
                    
                    t_abs = os.path.join(self.paths['vault'], target_rel_path)
                    t_src_abs = os.path.join(self.paths['vault'], t_source)
                    t_sub_rel = os.path.relpath(t_abs, t_src_abs).replace('\\', '/')
                    t_sub_dir = os.path.dirname(t_sub_rel).replace('\\', '/')
                    if t_sub_dir == '.': t_sub_dir = ""

                    # 🚀 [隐蔽 Bug 修复] 嵌套双链引擎解析时，同步转换底层目标目录的 URL
                    t_mapped_sub_dir = self._get_mapped_sub_dir(t_sub_dir, is_dry_run=is_dry_run, allow_ai=True)

                    t_prefix_part = f"/{t_prefix}" if t_prefix else ""
                    # 🚀 [隐蔽 Bug 修复] 当目标文章不在任何子目录时，必须使用 t_slug (目标链接)，而不是之前被错误占用的 slug (本文章链接)
                    raw_url = f"/{lang_code}{t_prefix_part}/{t_mapped_sub_dir}/{t_slug}" if t_mapped_sub_dir else f"/{lang_code}{t_prefix_part}/{t_slug}"
                    url_path = re.sub(r'/+', '/', raw_url)
                    
                    display_text = t_slug.replace('-', ' ').title() if is_target else custom_zh_text
                    return f"[{display_text}]({url_path})"
                return orig
                
            # 原生 Markdown 跳转链接 [alt](link) (同样支持全格式附件)
            elif orig.startswith('['):
                match = re.match(r'\[(.*?)\]\((.*?)\)', orig)
                if match and not match.group(2).startswith(('http://', 'https://', 'mailto:', '#')):
                    link_text, link_path = match.groups()
                    clean_path = urllib.parse.unquote(link_path.strip())
                    
                    # 🚀 专家逻辑：检查标准 Markdown 链接是否指向一个附件资产
                    asset_filename = os.path.basename(clean_path.split('?')[0].split('#')[0])
                    target_asset_path = _get_closest_asset(asset_filename)
                    if target_asset_path:
                        processed_name = log_asset(self.asset_pipeline.process(target_asset_path, asset_filename, is_dry_run))
                        return f"[{link_text}]({self.asset_base_url}{processed_name})"

                    target_rel_path = self.meta.resolve_link(clean_path) or self.meta.resolve_link(os.path.splitext(os.path.basename(clean_path))[0])
                    if target_rel_path:
                        t_doc_info = self.meta.get_doc_info(target_rel_path)
                        t_slug = t_doc_info.get("slug") or self.translator.generate_slug(os.path.splitext(os.path.basename(target_rel_path))[0], is_dry_run)[0]
                        t_prefix = t_doc_info.get("prefix", route_prefix)
                        t_source = t_doc_info.get("source", route_source)
                        
                        t_abs = os.path.join(self.paths['vault'], target_rel_path)
                        t_src_abs = os.path.join(self.paths['vault'], t_source)
                        t_sub_rel = os.path.relpath(t_abs, t_src_abs).replace('\\', '/')
                        t_sub_dir = os.path.dirname(t_sub_rel).replace('\\', '/')
                        if t_sub_dir == '.': t_sub_dir = ""

                        # 🚀 [隐蔽 Bug 修复] 嵌套双链引擎解析时，同步转换底层目标目录的 URL
                        t_mapped_sub_dir = self._get_mapped_sub_dir(t_sub_dir, is_dry_run=is_dry_run, allow_ai=True)

                        t_prefix_part = f"/{t_prefix}" if t_prefix else ""
                        # 🚀 [隐蔽 Bug 修复] 同步修复普通链接的 slug 占位符 Bug
                        raw_url = f"/{lang_code}{t_prefix_part}/{t_mapped_sub_dir}/{t_slug}" if t_mapped_sub_dir else f"/{lang_code}{t_prefix_part}/{t_slug}"
                        url_path = re.sub(r'/+', '/', raw_url)
                        
                        display_text = t_slug.replace('-', ' ').title() if is_target else link_text
                        return f"[{display_text}]({url_path})"
                return orig
            return orig

        # 执行反脱敏还原
        final_body = re.sub(r'\[\[STB_MASK_\d+\]\]', unmask_fn, masked_body)
        
        # 🚀 植入开源推广尾缀 (受控开关)
        if self.pub_cfg.get('append_credit', False):
            credit_text = self.pub_cfg.get('credit_text', '\n\n---\n*Powered by Illacme-plenipes*')
            final_body += f"{credit_text}\n"
        
        merged_fm = fm_dict.copy()
        merged_fm['title'] = slug.replace('-', ' ').title() if is_target else title
        
        # 🚀 应用动态 SEO 视觉权重排序体系
        ordered_fm = {}
        for key in self.fm_order:
            if key in merged_fm:
                ordered_fm[key] = merged_fm.pop(key)
        for key, value in merged_fm.items():
            ordered_fm[key] = value

        # 强制配置 PyYAML 杜绝折行
        fm_str = "---\n" + yaml.dump(ordered_fm, allow_unicode=True, default_flow_style=False, sort_keys=False, width=float("inf")) + "---\n\n"

        # 🚀 最终物理落盘：使用映射出的纯英文 URL 目录进行隔离写入
        dest = os.path.join(self.paths['target_base'], lang_code, route_prefix, mapped_sub_dir, f"{slug}.md")
        if not is_dry_run:
            try:
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                with open(dest, 'w', encoding='utf-8') as f:
                    f.write(fm_str + final_body)
            except Exception as e:
                logger.error(f"🛑 写入失败: 无法将文章存入前端目录 {dest}。请检查磁盘空间或文件夹权限: {e}")